/*
Copyright_License {

  XCSoar Glide Computer - http://www.xcsoar.org/
  Copyright (C) 2000-2014 The XCSoar Project
  A detailed list of copyright holders can be found in the file "AUTHORS".

  This program is free software; you can redistribute it and/or
  modify it under the terms of the GNU General Public License
  as published by the Free Software Foundation; either version 2
  of the License, or (at your option) any later version.

  This program is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU General Public License for more details.

  You should have received a copy of the GNU General Public License
  along with this program; if not, write to the Free Software
  Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
}
*/

#include "Queue.hpp"
#include "DisplayOrientation.hpp"
#include "OS/Clock.hpp"

EventQueue::EventQueue()
  :SignalListener(io_loop),
   thread(ThreadHandle::GetCurrent()),
   now_us(MonotonicClockUS()),
#ifndef NON_INTERACTIVE
#ifdef USE_LIBINPUT
   libinput_handler(io_loop, *this),
#else
#ifdef KOBO
   keyboard(io_loop, *this, merge_mouse),
#elif !defined(USE_LINUX_INPUT)
   keyboard(*this, io_loop),
#endif
#ifdef KOBO
   mouse(io_loop, *this, merge_mouse),
#elif defined(USE_LINUX_INPUT)
   all_input(io_loop, *this, merge_mouse),
#else
   mouse(io_loop, merge_mouse),
#endif
#endif
#endif
   running(true)
{
  SignalListener::Create(SIGINT, SIGTERM);

  event_pipe.Create();
  io_loop.Add(event_pipe.GetReadFD(), io_loop.READ, discard);

#ifndef NON_INTERACTIVE
#ifdef USE_LIBINPUT
  libinput_handler.Open();
#else
#ifdef KOBO
  /* power button */
  keyboard.Open("/dev/input/event0");

  /* Kobo touch screen */
  mouse.Open("/dev/input/event1");
#elif defined(USE_LINUX_INPUT)
  all_input.Open();
#else
  mouse.Open();
#endif
#endif
#endif
}

EventQueue::~EventQueue()
{
}

#if !defined(NON_INTERACTIVE) && !defined(USE_LIBINPUT)

void
EventQueue::SetMouseRotation(DisplayOrientation orientation)
{
  switch (orientation) {
  case DisplayOrientation::DEFAULT:
  case DisplayOrientation::PORTRAIT:
    SetMouseRotation(true, true, false);
    break;

  case DisplayOrientation::LANDSCAPE:
    SetMouseRotation(false, false, false);
    break;

  case DisplayOrientation::REVERSE_PORTRAIT:
    SetMouseRotation(true, false, true);
    break;

  case DisplayOrientation::REVERSE_LANDSCAPE:
    SetMouseRotation(false, true, true);
    break;
  }
}

#endif

void
EventQueue::Push(const Event &event)
{
  ScopeLock protect(mutex);
  if (!running)
    return;

  events.push(event);
  WakeUp();
}

int
EventQueue::GetTimeout() const
{
  int64_t timeout = timers.GetTimeoutUS(now_us);
  return timeout > 0
    ? int((timeout + 999) / 1000)
    : int(timeout);
}

void
EventQueue::Poll()
{
  io_loop.Lock();
  now_us = MonotonicClockUS();
  io_loop.Wait(GetTimeout());
  now_us = MonotonicClockUS();
  io_loop.Dispatch();
  io_loop.Unlock();
}

void
EventQueue::PushKeyPress(unsigned key_code)
{
  Push(Event(Event::KEY_DOWN, key_code));
  Push(Event(Event::KEY_UP, key_code));
}

bool
EventQueue::Generate(Event &event)
{
  Timer *timer = timers.Pop(now_us);
  if (timer != nullptr) {
    event.type = Event::TIMER;
    event.ptr = timer;
    return true;
  }

#if !defined(NON_INTERACTIVE) && !defined(USE_LIBINPUT)
  event = merge_mouse.Generate();
  if (event.type != Event::Type::NOP)
    return true;
#endif

  return false;
}

bool
EventQueue::Pop(Event &event)
{
  ScopeLock protect(mutex);
  if (!running || events.empty())
    return false;

  if (events.empty()) {
    if (Generate(event))
      return true;
  }

  event = events.front();
  events.pop();

  if (event.type == Event::QUIT)
    Quit();

  return true;
}

bool
EventQueue::Wait(Event &event)
{
  ScopeLock protect(mutex);
  if (!running)
    return false;

  if (events.empty()) {
    if (Generate(event))
      return true;

    while (events.empty()) {
      if (!running)
        return false;

      mutex.Unlock();
      Poll();
      mutex.Lock();

      if (Generate(event))
        return true;
    }
  }

  event = events.front();
  events.pop();

  if (event.type == Event::QUIT)
    Quit();

  return true;
}

void
EventQueue::Purge(bool (*match)(const Event &event, void *ctx), void *ctx)
{
  ScopeLock protect(mutex);
  size_t n = events.size();
  while (n-- > 0) {
    if (!match(events.front(), ctx))
      events.push(events.front());
    events.pop();
  }
}

static bool
match_type(const Event &event, void *ctx)
{
  const Event::Type *type_p = (const Event::Type *)ctx;
  return event.type == *type_p;
}

void
EventQueue::Purge(Event::Type type)
{
  Purge(match_type, &type);
}

static bool
MatchCallback(const Event &event, void *ctx)
{
  const Event *match = (const Event *)ctx;
  return event.type == Event::CALLBACK && event.callback == match->callback &&
    event.ptr == match->ptr;
}

void
EventQueue::Purge(Event::Callback callback, void *ctx)
{
  Event match(callback, ctx);
  Purge(MatchCallback, (void *)&match);
}

static bool
match_window(const Event &event, void *ctx)
{
  return event.type == Event::USER && event.ptr == ctx;
}

void
EventQueue::Purge(Window &window)
{
  Purge(match_window, (void *)&window);
}

void
EventQueue::AddTimer(Timer &timer, unsigned ms)
{
  ScopeLock protect(mutex);

  const uint64_t due_us = MonotonicClockUS() + ms * 1000;
  timers.Add(timer, MonotonicClockUS() + ms * 1000);

  if (timers.IsBefore(due_us))
    WakeUp();
}

void
EventQueue::CancelTimer(Timer &timer)
{
  ScopeLock protect(mutex);

  timers.Cancel(timer);
}

void
EventQueue::OnSignal(int signo)
{
  Quit();
}

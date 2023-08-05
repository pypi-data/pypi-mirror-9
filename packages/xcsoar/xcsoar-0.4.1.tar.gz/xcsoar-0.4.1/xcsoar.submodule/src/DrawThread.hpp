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

#ifndef XCSOAR_DRAW_THREAD_HPP
#define XCSOAR_DRAW_THREAD_HPP

#include "Thread/RecursivelySuspensibleThread.hpp"
#include "Thread/Trigger.hpp"
#include "Compiler.h"

class GlueMapWindow;

/**
 * The DrawThread handles the rendering and drawing on the screen.
 * The Map and GaugeFLARM both are triggered on GPS updates synchronously, 
 * which is why they are both handled by this thread.  The GaugeVario is
 * triggered on vario data which may be faster than GPS updates, which is
 * why it is not handled by this thread.
 * 
 */
class DrawThread final : public RecursivelySuspensibleThread {
  static constexpr unsigned MIN_WAIT_TIME = 100;

  /**
   * This triggers a redraw.
   */
  Trigger trigger;

  /** Pointer to the MapWindow */
  GlueMapWindow &map;

public:
  DrawThread(GlueMapWindow &_map)
    :RecursivelySuspensibleThread("DrawThread"), map(_map) {}

  /** Locks the Mutex and "pauses" the drawing thread */
  void BeginSuspend() {
    RecursivelySuspensibleThread::BeginSuspend();
    TriggerRedraw();
  }

  void Suspend() {
    BeginSuspend();
    WaitUntilSuspended();
  }

  /**
   * To be removed, only used by GlueMapWindow::Idle().
   */
  bool IsTriggered() {
    return trigger.Test();
  }

  /**
   * Triggers a redraw.
   */
  void TriggerRedraw() {
    trigger.Signal();
  }

  /**
   * Triggers thread shutdown.  Call join() after this to wait
   * synchronously for the thread to exit.
   */
  void BeginStop() {
    RecursivelySuspensibleThread::BeginStop();
    TriggerRedraw();
  }

protected:
  virtual void Run();
};

#endif

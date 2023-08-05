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

#ifndef XCSOAR_EVENT_LIBINPUT_LIBINPUT_HPP
#define XCSOAR_EVENT_LIBINPUT_LIBINPUT_HPP

#include "IO/Async/FileEventHandler.hpp"

#include <assert.h>

class EventQueue;
class IOLoop;
class UdevContext;

struct libinput;
struct libinput_interface;

/**
 * A driver for handling libinput events.
 */
class LibInputHandler final : private FileEventHandler {
  IOLoop &io_loop;
  EventQueue &queue;

  UdevContext* udev_context = nullptr;

  struct libinput* li = nullptr;
  struct libinput_interface* li_if = nullptr;

  int li_fd = -1;

  double x = -1.0, y = -1.0;
  unsigned width = 0, height = 0;

public:
  explicit LibInputHandler(IOLoop &_io_loop, EventQueue &_queue)
    :io_loop(_io_loop), queue(_queue) {}

  ~LibInputHandler() {
    Close();
  }

  bool Open();
  void Close();

  void SetScreenSize(unsigned _width, unsigned _height) {
    width = _width;
    height = _height;

    assert(width > 0);
    assert(height > 0);

    if (-1.0 == x)
      x = width / 2;

    if (-1.0 == y)
      y = height / 2;
  }

  unsigned GetX() const {
    return (unsigned) x;
  }

  unsigned GetY() const {
    return (unsigned) y;
  }

private:
  int OpenDevice(const char *path, int flags);
  void CloseDevice(int fd);

  void HandlePendingEvents();

  /* virtual methods from FileEventHandler */
  virtual bool OnFileEvent(int fd, unsigned mask) override;
};

#endif

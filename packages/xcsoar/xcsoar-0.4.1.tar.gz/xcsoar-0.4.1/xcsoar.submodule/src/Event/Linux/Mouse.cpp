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

#include "Mouse.hpp"
#include "MergeMouse.hpp"
#include "IO/Async/IOLoop.hpp"

bool
LinuxMouse::Open(const char *path)
{
  if (!fd.OpenReadOnly(path))
    return false;

  fd.SetNonBlocking();
  io_loop.Add(fd.Get(), io_loop.READ, *this);

  merge.AddPointer();

  return true;
}

void
LinuxMouse::Close()
{
  if (!IsOpen())
    return;

  merge.RemovePointer();

  io_loop.Remove(fd.Get());
  fd.Close();
}

void
LinuxMouse::Read()
{
  int8_t mb[3];
  while (fd.Read(mb, sizeof(mb)) == sizeof(mb)) {
    const bool down = (mb[0] & 0x7) != 0;
    merge.SetDown(down);

    const int dx = mb[1], dy = -mb[2];
    merge.MoveRelative(dx, dy);
  }
}

bool
LinuxMouse::OnFileEvent(int fd, unsigned mask)
{
  Read();

  return true;
}

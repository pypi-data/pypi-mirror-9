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

/** Library for calculating on-screen coordinates */

#ifndef XCSOAR_MATH_SCREEN_HPP
#define XCSOAR_MATH_SCREEN_HPP

struct RasterPoint;
class Angle;

void
ScreenClosestPoint(const RasterPoint &p1, const RasterPoint &p2,
                   const RasterPoint &p3, RasterPoint *p4, int offset);

/**
 * Shifts and rotates the given polygon and also sizes it via FastScale()
 *
 * @param poly Points specifying the polygon
 * @param n Number of points of the polygon
 * @param shift pixels to shift
 * @param angle Angle of rotation
 * @param scale Additional scaling in percent (100 = 100%, 150 = 150%, ...)
 */
void
PolygonRotateShift(RasterPoint *poly, int n, RasterPoint shift,
                   Angle angle, const int scale = 100);

#endif

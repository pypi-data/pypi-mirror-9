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

#include "Math/Screen.hpp"
#include "Math/Angle.hpp"
#include "Math/FastMath.h"
#include "Screen/Layout.hpp"
#include "Screen/Point.hpp"
#include "Util/Clamp.hpp"

#include <algorithm>

void
ScreenClosestPoint(const RasterPoint &p1, const RasterPoint &p2,
                   const RasterPoint &p3, RasterPoint *p4, int offset)
{
  int v12x, v12y, v13x, v13y;

  v12x = p2.x - p1.x;
  v12y = p2.y - p1.y;
  v13x = p3.x - p1.x;
  v13y = p3.y - p1.y;

  const int mag = v12x * v12x + v12y * v12y;
  if (mag > 1) {
    const int mag12 = isqrt4(mag);
    // projection of v13 along v12 = v12.v13/|v12|
    int proj = (v12x * v13x + v12y * v13y) / mag12;
    // fractional distance
    if (offset > 0) {
      if (offset * 2 < mag12) {
        proj = std::max(0, std::min(proj, mag12));
        proj = std::max(offset, std::min(mag12 - offset, proj + offset));
      } else {
        proj = mag12 / 2;
      }
    }

    const fixed f = Clamp(fixed(proj) / mag12, fixed(0), fixed(1));
    // location of 'closest' point
    p4->x = iround(v12x * f) + p1.x;
    p4->y = iround(v12y * f) + p1.y;
  } else {
    p4->x = p1.x;
    p4->y = p1.y;
  }
}

static int
roundshift(int x)
{
  if (x > 0) {
    x += 512;
  } else if (x < 0) {
    x -= 512;
  }
  return x >> 10;
}

void
PolygonRotateShift(RasterPoint *poly, const int n,
                   const RasterPoint shift,
                   Angle angle, const int scale)
{
  const int xs = shift.x, ys = shift.y;
  const int cost = Layout::FastScale(angle.ifastcosine() * scale) / 100;
  const int sint = Layout::FastScale(angle.ifastsine() * scale) / 100;

  RasterPoint *p = poly;
  const RasterPoint *pe = poly + n;

  while (p < pe) {
    int x = p->x;
    int y = p->y;
    p->x = roundshift(x * cost - y * sint) + xs;
    p->y = roundshift(y * cost + x * sint) + ys;
    p++;
  }
}

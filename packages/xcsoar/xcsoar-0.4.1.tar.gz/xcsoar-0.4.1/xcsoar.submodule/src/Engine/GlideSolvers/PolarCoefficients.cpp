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

#include "PolarCoefficients.hpp"

PolarCoefficients
PolarCoefficients::From3VW(fixed v1, fixed v2, fixed v3,
                          fixed w1, fixed w2, fixed w3)
{
  PolarCoefficients pc;

  fixed d = sqr(v1) * (v2 - v3) + sqr(v2) * (v3 - v1) + sqr(v3) * (v1 - v2);
  pc.a = (d == fixed(0)) ? fixed(0) :
         -((v2 - v3) * (w1 - w3) + (v3 - v1) * (w2 - w3)) / d;

  d = v2 - v3;
  pc.b = (d == fixed(0)) ? fixed(0):
    -(w2 - w3 + pc.a * (sqr(v2) - sqr(v3))) / d;

  pc.c = -(w3 + pc.a * sqr(v3) + pc.b * v3);

  return pc;
}

PolarCoefficients
PolarCoefficients::From2VW(fixed v1, fixed v2, fixed w1, fixed w2)
{
  PolarCoefficients pc;

  fixed d = sqr(v2 - v1);
  pc.a = (d == fixed(0)) ? fixed(0) : (w2 - w1) / d;
  pc.b = - Double(pc.a * v1);
  pc.c = pc.a * sqr(v1) + w1;

  return pc;
}

bool
PolarCoefficients::IsValid() const
{
  return positive(a) && negative(b) && positive(c);
}

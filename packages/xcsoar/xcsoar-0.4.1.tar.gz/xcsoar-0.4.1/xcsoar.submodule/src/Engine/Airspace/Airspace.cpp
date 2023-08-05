/* Copyright_License {

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

#include "Airspace.hpp"
#include "AbstractAirspace.hpp"
#include "AirspaceIntersectionVector.hpp"
#include "Geo/Flat/FlatProjection.hpp"

void
Airspace::Destroy()
{
  delete airspace;
}

Airspace::Airspace(AbstractAirspace &airspace,
                   const FlatProjection &tp)
  :FlatBoundingBox(airspace.GetBoundingBox(tp)),
   airspace(&airspace)
{
}

Airspace::Airspace(const GeoPoint &loc, const FlatProjection &task_projection,
                   const fixed range)
  :FlatBoundingBox(task_projection.ProjectInteger(loc),
                   task_projection.ProjectRangeInteger(loc, range)),
   airspace(nullptr)
{
}

Airspace::Airspace(const GeoPoint &ll, const GeoPoint &ur,
                   const FlatProjection &task_projection)
  :FlatBoundingBox(task_projection.ProjectInteger(ll),
                   task_projection.ProjectInteger(ur)),
   airspace(nullptr)
{
}

bool
Airspace::IsInside(const AircraftState &loc) const
{
  assert(airspace != nullptr);
  return airspace->Inside(loc);
}


bool
Airspace::IsInside(const GeoPoint &loc) const
{
  assert(airspace != nullptr);
  return airspace->Inside(loc);
}

bool
Airspace::Intersects(const FlatRay &ray) const
{
  return FlatBoundingBox::Intersects(ray);
}


AirspaceIntersectionVector
Airspace::Intersects(const GeoPoint &g1, const GeoPoint &end,
                     const FlatProjection &projection) const
{
  assert(airspace != nullptr);
  return airspace->Intersects(g1, end, projection);
}

void
Airspace::SetGroundLevel(const fixed alt) const
{
  assert(airspace != nullptr);
  airspace->SetGroundLevel(alt);
}

bool
Airspace::NeedGroundLevel() const
{
  assert(airspace != nullptr);
  return airspace->NeedGroundLevel();
}

void
Airspace::SetFlightLevel(const AtmosphericPressure &press) const
{
  assert(airspace != nullptr);
  airspace->SetFlightLevel(press);
}

void
Airspace::SetActivity(const AirspaceActivity mask) const
{
  assert(airspace != nullptr);
  airspace->SetActivity(mask);
}

void
Airspace::ClearClearance() const
{
  assert(airspace != nullptr);
  airspace->ClearClearance();
}

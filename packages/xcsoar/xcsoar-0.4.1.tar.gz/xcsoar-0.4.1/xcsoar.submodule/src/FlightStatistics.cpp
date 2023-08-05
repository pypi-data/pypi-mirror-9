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

#include "FlightStatistics.hpp"

void FlightStatistics::Reset() {
  ScopeLock lock(mutex);

  thermal_average.Reset();
  altitude.Reset();
  altitude_base.Reset();
  altitude_ceiling.Reset();
  task_speed.Reset();
  altitude_terrain.Reset();
}

void
FlightStatistics::StartTask()
{
  ScopeLock lock(mutex);
  // JMW clear thermal climb average on task start
  thermal_average.Reset();
  task_speed.Reset();
}

void
FlightStatistics::AddAltitudeTerrain(const fixed tflight, const fixed terrainalt)
{
  ScopeLock lock(mutex);
  altitude_terrain.Update(std::max(fixed(0), tflight / 3600),
                          terrainalt);
}

void
FlightStatistics::AddAltitude(const fixed tflight, const fixed alt)
{
  ScopeLock lock(mutex);
  altitude.Update(std::max(fixed(0), tflight / 3600), alt);
}

fixed
FlightStatistics::AverageThermalAdjusted(const fixed mc_current,
                                         const bool circling)
{
  ScopeLock lock(mutex);

  fixed mc_stats;
  if (positive(thermal_average.GetAverageY())) {
    if (mc_current > fixed(0) && circling)
      mc_stats = (thermal_average.GetCount() * thermal_average.GetAverageY() + mc_current) /
        (thermal_average.GetCount() + 1);
    else
      mc_stats = thermal_average.GetAverageY();
  } else {
    mc_stats = mc_current;
  }

  return mc_stats;
}

void
FlightStatistics::AddTaskSpeed(const fixed tflight, const fixed val)
{
  ScopeLock lock(mutex);
  task_speed.Update(tflight / 3600, std::max(fixed(0),val));
}

void
FlightStatistics::AddClimbBase(const fixed tflight, const fixed alt)
{
  ScopeLock lock(mutex);

  if (!altitude_ceiling.IsEmpty())
    // only update base if have already climbed, otherwise
    // we will catch the takeoff height as the base.
    altitude_base.Update(std::max(fixed(0), tflight) / 3600, alt);
}

void
FlightStatistics::AddClimbCeiling(const fixed tflight, const fixed alt)
{
  ScopeLock lock(mutex);
  altitude_ceiling.Update(std::max(fixed(0), tflight) / 3600, alt);
}

/**
 * Adds a thermal to the ThermalAverage calculator
 * @param v Average climb speed of the last thermal
 */
void
FlightStatistics::AddThermalAverage(const fixed v)
{
  ScopeLock lock(mutex);
  thermal_average.Update(v);
}

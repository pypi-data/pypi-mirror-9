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

#include "RasterWeatherCache.hpp"
#include "RasterWeatherStore.hpp"
#include "RasterMap.hpp"
#include "Language/Language.hpp"
#include "Units/Units.hpp"
#include "LocalPath.hpp"
#include "OS/FileUtil.hpp"
#include "Util/ConvertString.hpp"
#include "Util/Clamp.hpp"
#include "Util/Macros.hpp"
#include "Operation/Operation.hpp"
#include "zzip/zzip.h"

#include <assert.h>
#include <tchar.h>
#include <stdio.h>
#include <windef.h> // for MAX_PATH

static inline constexpr unsigned
ToHalfHours(BrokenTime t)
{
  return t.hour * 2u + t.minute / 30;
}

RasterWeatherCache::RasterWeatherCache(const RasterWeatherStore &_store)
  :store(_store),
   center(GeoPoint::Invalid()),
   parameter(0), last_parameter(0),
   weather_time(0), last_weather_time(0),
   weather_map(nullptr)
{
}

const TCHAR *
RasterWeatherCache::GetMapName() const
{
  assert(!IsTerrain());

  return store.GetItemInfo(parameter).name;
}

void
RasterWeatherCache::SetTime(BrokenTime t)
{
  unsigned i = t.IsPlausible() ? ToHalfHours(t) : 0;
  weather_time = i;
}

BrokenTime
RasterWeatherCache::GetTime() const
{
  return weather_time == 0
    ? BrokenTime::Invalid()
    : RasterWeatherStore::IndexToTime(weather_time);
}

void
RasterWeatherCache::Reload(BrokenTime time_local, OperationEnvironment &operation)
{
  assert(time_local.IsPlausible());

  if (parameter == 0)
    // will be drawing terrain
    return;

  unsigned effective_weather_time = weather_time;
  if (effective_weather_time == 0) {
    // "Now" time, so find time in half hours
    effective_weather_time = ToHalfHours(time_local);
    assert(effective_weather_time < RasterWeatherStore::MAX_WEATHER_TIMES);
  }

  if (parameter == last_parameter && effective_weather_time == last_weather_time)
    // no change, quick exit.
    return;

  last_parameter = parameter;
  last_weather_time = effective_weather_time;

  // scan forward to next valid time
  while (!store.IsTimeAvailable(parameter, effective_weather_time)) {
    ++effective_weather_time;

    if (effective_weather_time >= RasterWeatherStore::MAX_WEATHER_TIMES)
      // can't find valid time
      return;
  }

  Close();

  weather_map = store.LoadItem(store.GetItemInfo(parameter).name,
                               effective_weather_time, operation);
}

void
RasterWeatherCache::Close()
{
  delete weather_map;
  weather_map = nullptr;
  center = GeoPoint::Invalid();
}

void
RasterWeatherCache::SetViewCenter(const GeoPoint &location, fixed radius)
{
  if (parameter == 0)
    // will be drawing terrain
    return;

  if (weather_map == nullptr)
    return;

  /* only update the RasterMap if the center was moved far enough */
  if (center.IsValid() && center.Distance(location) < fixed(1000))
    return;

  weather_map->SetViewCenter(location, radius);
  if (!weather_map->IsDirty())
    center = location;
}

bool
RasterWeatherCache::IsDirty() const
{
  if (parameter == 0)
    // will be drawing terrain
    return false;

  return weather_map != nullptr && weather_map->IsDirty();
}

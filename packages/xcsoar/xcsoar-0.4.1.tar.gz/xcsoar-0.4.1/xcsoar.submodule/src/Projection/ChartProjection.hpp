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

#include "WindowProjection.hpp"

class TaskProjection;
class OrderedTask;
class OrderedTaskPoint;

/**
 * Utility class to determine projection for a chart from task data,
 * typically scaled to fill the canvas
 */
class ChartProjection:
  public WindowProjection
{
public:
  ChartProjection() = default;

  explicit ChartProjection(const PixelRect &rc,
                           const TaskProjection &task_projection,
                           fixed radius_factor=fixed(1.1)) {
    Set(rc, task_projection, radius_factor);
  }

  ChartProjection(const PixelRect &rc, const OrderedTask &task,
                  const GeoPoint &fallback_loc) {
    Set(rc, task, fallback_loc);
  }

  ChartProjection(const PixelRect &rc, const OrderedTaskPoint &point,
                  const GeoPoint &fallback_loc) {
    Set(rc, point, fallback_loc);
  }

  void Set(const PixelRect &rc, const TaskProjection &task_projection,
           fixed radius_factor=fixed(1.1));

  void Set(const PixelRect &rc, const OrderedTask &task,
           const GeoPoint &fallback_loc);

  void Set(const PixelRect &rc, const OrderedTaskPoint &point,
           const GeoPoint &fallback_loc);

private:
  void Set(const PixelRect &rc, const GeoPoint &center, const fixed radius);
};

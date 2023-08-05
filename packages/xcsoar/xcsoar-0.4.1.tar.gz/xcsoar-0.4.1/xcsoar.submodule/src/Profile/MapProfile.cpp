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

#include "Profile/MapProfile.hpp"
#include "Profile/TerrainConfig.hpp"
#include "Profile/AirspaceConfig.hpp"
#include "Profile/Profile.hpp"
#include "MapSettings.hpp"
#include "Util/Clamp.hpp"

static bool
IsValidMapOrientation(unsigned value)
{
  switch (value) {
  case (unsigned)MapOrientation::TRACK_UP:
  case (unsigned)MapOrientation::NORTH_UP:
  case (unsigned)MapOrientation::TARGET_UP:
  case (unsigned)MapOrientation::HEADING_UP:
  case (unsigned)MapOrientation::WIND_UP:
    return true;
  }

  return false;
}

static void
Load(FAITriangleSettings &settings)
{
  FAITriangleSettings::Threshold threshold;
  if (Profile::GetEnum(ProfileKeys::FAITriangleThreshold, threshold) &&
      unsigned(threshold) < unsigned(FAITriangleSettings::Threshold::MAX))
    settings.threshold = threshold;
}

void
Profile::Load(MapSettings &settings)
{
  Get(ProfileKeys::CircleZoom, settings.circle_zoom_enabled);
  Get(ProfileKeys::MaxAutoZoomDistance, settings.max_auto_zoom_distance);
  Get(ProfileKeys::DrawTopography, settings.topography_enabled);

  LoadTerrainRendererSettings(settings.terrain);

  GetEnum(ProfileKeys::AircraftSymbol, settings.aircraft_symbol);

  Get(ProfileKeys::DetourCostMarker, settings.detour_cost_markers_enabled);
  GetEnum(ProfileKeys::DisplayTrackBearing, settings.display_ground_track);
  Get(ProfileKeys::AutoZoom, settings.auto_zoom_enabled);

  GetEnum(ProfileKeys::WindArrowStyle, settings.wind_arrow_style);

  settings.waypoint.LoadFromProfile();

  Load(settings.airspace);

  Get(ProfileKeys::GliderScreenPosition, settings.glider_screen_position);

  bool orientation_found = false;

  unsigned Temp = (unsigned)MapOrientation::NORTH_UP;
  if (Get(ProfileKeys::OrientationCircling, Temp)) {
    orientation_found = true;

    if (IsValidMapOrientation(Temp))
      settings.circling_orientation = (MapOrientation)Temp;
  }

  Temp = (unsigned)MapOrientation::NORTH_UP;
  if (Get(ProfileKeys::OrientationCruise, Temp)) {
    orientation_found = true;

    if (IsValidMapOrientation(Temp))
      settings.cruise_orientation = (MapOrientation)Temp;
  }

  if (!orientation_found) {
    Temp = 1;
    Get(ProfileKeys::DisplayUpValue, Temp);
    switch (Temp) {
    case 0:
      settings.cruise_orientation = MapOrientation::TRACK_UP;
      settings.circling_orientation = MapOrientation::TRACK_UP;
      break;
    case 1:
      settings.cruise_orientation = MapOrientation::NORTH_UP;
      settings.circling_orientation = MapOrientation::NORTH_UP;
      break;
    case 2:
      settings.cruise_orientation = MapOrientation::TRACK_UP;
      settings.circling_orientation = MapOrientation::NORTH_UP;
      break;
    case 3:
      settings.cruise_orientation = MapOrientation::TRACK_UP;
      settings.circling_orientation = MapOrientation::TARGET_UP;
      break;
    case 4:
      settings.cruise_orientation = MapOrientation::NORTH_UP;
      settings.circling_orientation = MapOrientation::TRACK_UP;
      break;
    }
  }

  fixed tmp;
  if (Profile::Get(ProfileKeys::ClimbMapScale, tmp))
    settings.circling_scale = Clamp(tmp / 10000, fixed(0.0003), fixed(10));

  if (Profile::Get(ProfileKeys::CruiseMapScale, tmp))
    settings.cruise_scale = Clamp(tmp / 10000, fixed(0.0003), fixed(10));

  GetEnum(ProfileKeys::MapShiftBias, settings.map_shift_bias);
  Get(ProfileKeys::EnableFLARMMap, settings.show_flarm_on_map);

  Get(ProfileKeys::EnableThermalProfile, settings.show_thermal_profile);
  Get(ProfileKeys::EnableFinalGlideBarMC0,
      settings.final_glide_bar_mc0_enabled);
  GetEnum(ProfileKeys::FinalGlideBarDisplayMode,
          settings.final_glide_bar_display_mode);
  Get(ProfileKeys::ShowFAITriangleAreas,
      settings.show_fai_triangle_areas);
  ::Load(settings.fai_triangle_settings);

  Get(ProfileKeys::EnableVarioBar,
      settings.vario_bar_enabled);

  Load(settings.trail);
  Load(settings.item_list);
}

void
Profile::Load(TrailSettings &settings)
{
  Get(ProfileKeys::TrailDrift, settings.wind_drift_enabled);
  Get(ProfileKeys::SnailWidthScale, settings.scaling_enabled);
  GetEnum(ProfileKeys::SnailType, settings.type);
  GetEnum(ProfileKeys::SnailTrail, settings.length);
}

void
Profile::Load(MapItemListSettings &settings)
{
  Get(ProfileKeys::EnableLocationMapItem, settings.add_location);
  Get(ProfileKeys::EnableArrivalAltitudeMapItem, settings.add_arrival_altitude);
}

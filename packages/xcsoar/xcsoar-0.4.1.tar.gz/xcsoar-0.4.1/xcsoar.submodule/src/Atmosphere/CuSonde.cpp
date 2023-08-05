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

#include "Atmosphere/CuSonde.hpp"
#include "NMEA/Info.hpp"
#include "NMEA/Derived.hpp"
#include "Temperature.hpp"

#include <math.h>
#include <stdlib.h> /* for abs() */
#include <algorithm>

/**
 * Dry adiabatic lapse rate (degrees C per meter)
 *
 * DALR = dT/dz = g/c_p =
 * @see http://en.wikipedia.org/wiki/Lapse_rate#Dry_adiabatic_lapse_rate
 * @see http://pds-atmospheres.nmsu.edu/education_and_outreach/encyclopedia/adiabatic_lapse_rate.htm
 */
#define DALR fixed(-0.00974)

/** ThermalIndex threshold in degrees C */
#define TITHRESHOLD fixed(-1.6)

using std::max;

void
CuSonde::Reset()
{
  last_level = 0;
  thermalHeight = fixed(0);
  cloudBase = fixed(0);
  hGround = fixed(0);
  maxGroundTemperature = fixed(25);

  for (unsigned i = 0; i < NUM_LEVELS; ++i)
    cslevels[i].Reset();
}

// TODO accuracy: recalculate thermal index etc if maxGroundTemp changes

/**
 * Sets the predicted maximum ground temperature to val
 * @param val New predicted maximum ground temperature in degrees C
 */
void
CuSonde::SetForecastTemperature(fixed val)
{
  if (maxGroundTemperature == val)
    return;

  maxGroundTemperature = val;

  unsigned zlevel = 0;

  // set these to invalid, so old values must be overwritten
  cloudBase = fixed(-1);
  thermalHeight = fixed(-1);

  // iterate through all levels
  fixed h_agl = -CuSonde::hGround;
  for (unsigned level = 0; level < NUM_LEVELS;
       level++, h_agl += fixed(HEIGHT_STEP)) {
    // update the ThermalIndex for each level with
    // the new maxGroundTemperature
    cslevels[level].UpdateThermalIndex(h_agl, maxGroundTemperature);

    // determine to which level measurements are available
    if (!cslevels[level].empty())
      zlevel = level;

    if (cslevels[level].empty() && zlevel)
      break;
  }

  // iterate through all levels with measurements
  for (unsigned level = 0; level <= zlevel; level++) {
    // calculate ThermalHeight
    FindThermalHeight((unsigned short)level);
    // calculate CloudBase
    FindCloudBase((unsigned short)level);
  }
}

/**
 * Update the measurements if new level reached
 * @param basic NMEA_INFO for temperature and humidity
 */
void
CuSonde::UpdateMeasurements(const NMEAInfo &basic,
                            const DerivedInfo &calculated)
{
  // if (not flying) nothing to update...
  if (!calculated.flight.flying)
    return;

  // if (no temperature or humidity available) nothing to update...
  if (!basic.temperature_available || !basic.humidity_available)
    return;

  // find appropriate level
  const auto any_altitude = basic.GetAnyAltitude();
  if (!any_altitude.first)
    return;

  unsigned short level = (unsigned short)((int)max(any_altitude.second,
                                                   fixed(0.0))
                                          / HEIGHT_STEP);

  // if (level out of range) cancel update
  if (level >= NUM_LEVELS)
    return;

  // if (level skipped) cancel update
  if (abs(level - last_level) > 1) {
    last_level = level;
    return;
  }

  // if (no level transition yet) wait for transition
  if (abs(level - last_level) == 0)
    return;

  // calculate ground height
  hGround = calculated.altitude_agl;

  // if (going up)
  if (level > last_level) {
    // we round down (level) because of potential lag of temp sensor
    cslevels[level].UpdateTemps(basic.humidity,
                                KelvinToCelsius(basic.temperature));

    fixed h_agl = fixed(level * HEIGHT_STEP) - hGround;
    cslevels[level].UpdateThermalIndex(h_agl, maxGroundTemperature);

    if (level > 0) {
      FindThermalHeight((unsigned short)(level - 1));
      FindCloudBase((unsigned short)(level - 1));
    }

  // if (going down)
  } else {
    // we round up (level+1) because of potential lag of temp sensor
    cslevels[level + 1].UpdateTemps(basic.humidity,
                                    KelvinToCelsius(basic.temperature));

    fixed h_agl = fixed((level + 1) * HEIGHT_STEP) - hGround;
    cslevels[level + 1].UpdateThermalIndex(h_agl, maxGroundTemperature);

    if (level < NUM_LEVELS - 1) {
      FindThermalHeight(level);
      FindCloudBase(level);
    }
  }

  last_level = level;
}

/**
 * Finds the estimated ThermalHeight based on the given level and the one
 * above
 * @param level Level used for calculation
 */
void
CuSonde::FindThermalHeight(unsigned short level)
{
  if (cslevels[level + 1].empty())
    return;
  if (cslevels[level].empty())
    return;

  // Delta of ThermalIndex
  fixed dti = cslevels[level + 1].thermalIndex - cslevels[level].thermalIndex;

  // Reset estimated ThermalHeight
  cslevels[level].thermalHeight = fixed(-1);

  if (fabs(dti) < fixed(0.001))
    return;

  // ti = dlevel * dti + ti0;
  // (-1.6 - ti0)/dti = dlevel;

  fixed dlevel = (TITHRESHOLD - cslevels[level].thermalIndex) / dti;
  fixed dthermalheight = (fixed(level) + dlevel) * HEIGHT_STEP;

  if ((dlevel > fixed(1))
      && (level + 2u < NUM_LEVELS)
      && !cslevels[level + 2].empty())
      // estimated point should be in next level.
      return;

  if (positive(dlevel)) {
    // set the level thermal height to the calculated value
    cslevels[level].thermalHeight = dthermalheight;

    // set the overall thermal height to the calculated value
    thermalHeight = dthermalheight;
  }
}

/**
 * Finds the estimated CloudBase based on the given level and the one
 * above
 * @param level Level used for calculation
 */
void
CuSonde::FindCloudBase(unsigned short level)
{
  if (cslevels[level + 1].empty())
    return;
  if (cslevels[level].empty())
    return;

  fixed dti = (cslevels[level + 1].tempDry - cslevels[level + 1].dewpoint)
               - (cslevels[level].tempDry - cslevels[level].dewpoint);

  // Reset estimated CloudBase
  cslevels[level].cloudBase = fixed(-1);

  if (fabs(dti) < fixed(0.001))
    return;

  // ti = dlevel * dti + ti0;
  // (-3 - ti0)/dti = dlevel;

  fixed dlevel = -(cslevels[level].tempDry - cslevels[level].dewpoint) / dti;
  fixed dcloudbase = (fixed(level) + dlevel) * HEIGHT_STEP;

  if ((dlevel > fixed(1))
      && (level + 2u < NUM_LEVELS)
      && !cslevels[level + 2].empty())
    // estimated point should be in next level.
    return;

  if (positive(dlevel)) {
    // set the level cloudbase to the calculated value
    cslevels[level].cloudBase = dcloudbase;

    // set the overall cloudbase to the calculated value
    cloudBase = dcloudbase;
  }
}

/**
 * Calculates the dew point and saves the measurement
 * @param rh Humidity in percent
 * @param t Temperature in degrees C
 */
void
CuSonde::Level::UpdateTemps(fixed humidity, fixed temperature)
{
  fixed log_ex, _dewpoint;

  log_ex = fixed(7.5) * temperature / (fixed(237.3) + temperature) +
          (fixed(log10((double)humidity)) - fixed(2));
  _dewpoint = log_ex * fixed(237.3) / (fixed(7.5) - log_ex);

  // update statistics
  if (empty()) {
    dewpoint = _dewpoint;
    airTemp = temperature;
  } else {
    dewpoint = (_dewpoint + dewpoint) / 2;
    airTemp = (temperature + airTemp) / 2;
  }

  nmeasurements++;
}

/**
 * Calculates the ThermalIndex for the given height level
 *
 * ThermalIndex is the difference in dry temp and environmental temp
 * at the specified altitude.
 * @param level level = altitude / HEIGHT_STEP
 * @param newdata Function logs data to debug file if true
 */
void
CuSonde::Level::UpdateThermalIndex(fixed h_agl, fixed max_ground_temperature)
{
  // Calculate the dry temperature at altitude = hlevel
  tempDry = DALR * h_agl + max_ground_temperature;

  // Calculate ThermalIndex
  thermalIndex = airTemp - tempDry;
}

/*
   - read sensor values
   - calculate dewpoint
   - update statistical model:

   - for each height:
       -- calculate temp of dry parcel of air from ground temp
             projected up at DALR
       -- thermal index is difference in dry temp and environmental temp
       -- calculate dew point
       -- extrapolate difference between DALR temp and dew point to
            find cloud base (where difference is 0)
       -- extrapolate thermal index to find estimated convection height
            (where thermal index = -3)
       -- extrapolation should occur at top band but may not if tow was
           higher than thermal height, or if climbing above cloud base
           (e.g. from wave lift)

   - summary:
       -- cloud base
       -- usable thermal height
       -- estimated thermal strength

   - complications:
       -- terrain
       -- temp higher in thermals?


DALR = -0.00974 degrees C per meter

C to Kelvin = +273.15
 */

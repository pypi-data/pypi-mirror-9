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

#ifndef AIRSPACE_AIRCRAFT_PERFORMANCE_HPP
#define AIRSPACE_AIRCRAFT_PERFORMANCE_HPP

#include "Math/fixed.hpp"
#include "GlideSolvers/GlidePolar.hpp"
#include "GlideSolvers/GlideResult.hpp"
#include "Util/AircraftStateFilter.hpp"
#include "Compiler.h"

#include <assert.h>

/**
 *  Class used for simplified/idealised performace
 *  of aircraft speed as a function of glide slope.
 */
class AirspaceAircraftPerformance {
  /** Tolerance in vertical max speeds (m/s) */
  fixed vertical_tolerance;

  /**
   * Nominal cruise speed [m/s]
   */
  fixed cruise_speed;

  /**
   * Nominal descent speed (m/s, positive down)
   */
  fixed cruise_descent;

  /**
   * Max descent speed (m/s, positive down)
   */
  fixed descent_rate;

  /**
   * Max climb rate (m/s, positive up)
   */
  fixed climb_rate;

  /**
   * Maximum speed achievable by this model [m/s].
   */
  fixed max_speed;

public:
  struct Simple {};

  /**
   * Simplified aircraft performance model used for testing of
   * airspace warning system with minimal dependencies.
   */
  constexpr AirspaceAircraftPerformance(Simple)
    :vertical_tolerance(0),
     cruise_speed(30), cruise_descent(2),
     descent_rate(2),
     climb_rate(10),
     max_speed(30) {}

  /**
   * Specialisation based on simplified theoretical MC cross-country
   * speeds.  Assumes cruise at best LD (ignoring wind) for current MC
   * setting, climb rate at MC setting, with direct descent possible
   * at sink rate of cruise.
   */
  explicit AirspaceAircraftPerformance(const GlidePolar &polar)
    :vertical_tolerance(0),
     cruise_speed(polar.GetVBestLD()), cruise_descent(polar.GetSBestLD()),
     descent_rate(polar.GetSMax()),
     climb_rate(polar.GetMC()),
     max_speed(polar.GetVMax()) {
    assert(polar.IsValid());
  }

  /**
   * Specialisation of AirspaceAircraftPerformance based on low pass
   * filtered aircraft state --- effectively producing potential
   * solutions at average speed in the averaged direction at the
   * averaged climb rate.
   */
  explicit AirspaceAircraftPerformance(const AircraftStateFilter &filter)
    :vertical_tolerance(0.01),
     cruise_speed(filter.GetSpeed()), cruise_descent(-filter.GetClimbRate()),
     descent_rate(-filter.GetClimbRate()),
     climb_rate(filter.GetClimbRate()),
     max_speed(filter.GetSpeed()) {}

  /**
   * Specialisation of AirspaceAircraftPerformance for tasks where
   * part of the path is in cruise, part in final glide.  This is
   * intended to be used temporarily only.
   *
   * This simplifies the path by assuming flight is constant altitude
   * or descent to the task point elevation.
   */
  AirspaceAircraftPerformance(const GlidePolar &polar,
                              const GlideResult &solution)
    :vertical_tolerance(0.001),
     cruise_speed(positive(solution.time_elapsed)
                  ? solution.vector.distance / solution.time_elapsed
                  : fixed(1)),
     cruise_descent(positive(solution.time_elapsed)
                    ? (positive(solution.height_climb)
                       ? -solution.height_climb
                       : solution.height_glide) / solution.time_elapsed
                    : fixed(0)),
     descent_rate(polar.GetSBestLD()),
     climb_rate(positive(solution.time_elapsed) &&
                positive(solution.height_climb)
                ? polar.GetMC()
                : fixed(0)),
     max_speed(cruise_speed) {
    assert(polar.IsValid());
    assert(solution.IsOk());
    assert(solution.IsAchievable());
  }

  /**
   * Return nominal speed
   *
   * @return Nominal cruise speed (m/s)
   */
  fixed GetCruiseSpeed() const {
    return cruise_speed;
  }

  /**
   * Return nominal descent rate
   *
   * @return Nominal descent speed (m/s, positive down)
   */
  fixed GetCruiseDescent() const {
    return cruise_descent;
  }

  /**
   * Return descent rate limit (above nominal descent rate)
   *
   * @return Max descent speed (m/s, positive down)
   */
  fixed GetDescentRate() const {
    return descent_rate;
  }

  /**
   * Return climb rate limit (above nominal descent rate)
   *
   * @return Max climb rate (m/s, positive up)
   */
  fixed GetClimbRate() const {
    return climb_rate;
  }

  /**
   * Return maximum speed achievable by this model
   *
   * @return Speed (m/s)
   */
  fixed GetMaxSpeed() const {
    return max_speed;
  }

  /**
   * Find minimum intercept time to a point
   *
   * @param distance Distance to point (m)
   * @param dh Relative height of observer above point (m)
   *
   * @return Time to intercept (s) or -1 if failed
   */
  gcc_pure
  fixed SolutionGeneral(fixed distance, fixed dh) const;

  /**
   * Find time to intercept a target with a height band, set distance
   *
   * @param distance Lateral distance to travel (m)
   * @param altitude Altitude of observer (m)
   * @param base Height of base (m)
   * @param top  Height of top (m)
   * @param intercept_alt If intercept possible, this is the soonest height
   *
   * @return Time of intercept (s)
   */
  fixed SolutionVertical(fixed distance, fixed altitude,
                         fixed base, fixed top,
                         fixed &intercept_alt) const;

  /**
   * Find time to intercept a target with a distance band, set height
   *
   * @param distance_min Min distance to travel (m)
   * @param distance_max Max distance to travel (m)
   * @param altitude Altitude of observer (m)
   * @param h  Height of target (m)
   * @param intercept_distance If intercept possible, this is the distance to the soonest point
   *
   * @return Time of intercept (s)
   */
  fixed SolutionHorizontal(fixed distance_min, fixed distance_max,
                           fixed altitude, fixed h,
                           fixed &intercept_distance) const;

private:
  gcc_pure
  virtual bool SolutionExists(fixed distance_min, fixed distance_max,
                              fixed h_min, fixed h_max) const;
};

#endif

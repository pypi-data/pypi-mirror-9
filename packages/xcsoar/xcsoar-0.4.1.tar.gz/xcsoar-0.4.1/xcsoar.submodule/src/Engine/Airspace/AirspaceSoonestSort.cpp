#include "AirspaceSoonestSort.hpp"
#include "AirspaceAircraftPerformance.hpp"
#include "AbstractAirspace.hpp"

AirspaceInterceptSolution
AirspaceSoonestSort::solve_intercept(const AbstractAirspace &a,
                                     const FlatProjection &projection) const
{
  const GeoPoint loc = a.ClosestPoint(m_state.location, projection);

  AirspaceInterceptSolution sol =
    AirspaceInterceptSolution::Invalid();
  bool valid = a.Intercept(m_state, m_perf, sol, loc, loc);

  if (sol.elapsed_time > m_max_time) {
    valid = false;
  }
  if (!valid) {
    sol.elapsed_time = fixed(-1);
  }
  return sol;
}

fixed
AirspaceSoonestSort::metric(const AirspaceInterceptSolution& sol) const
{
  return sol.elapsed_time;
}

const AbstractAirspace *
AirspaceSoonestSort::find_nearest(const Airspaces &airspaces)
{
  const fixed range = m_perf.GetMaxSpeed()*m_max_time;
  return AirspaceNearestSort::find_nearest(airspaces, range);
}

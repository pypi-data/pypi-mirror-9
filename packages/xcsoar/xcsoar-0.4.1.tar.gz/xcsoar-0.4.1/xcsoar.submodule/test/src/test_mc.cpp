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

#include "test_debug.hpp"
#include "GlideSolvers/GlideSettings.hpp"
#include "GlideSolvers/GlidePolar.hpp"
#include "GlideSolvers/GlideState.hpp"
#include "GlideSolvers/GlideResult.hpp"
#include "GlideSolvers/MacCready.hpp"
#include "Navigation/Aircraft.hpp"
#include "OS/FileUtil.hpp"

#include <stdio.h>
#include <fstream>
#include <string>
#include <math.h>

const fixed Vmin(5.0);

static void
polar_mc(std::ofstream &ofile, const fixed mc)
{
  GlidePolar polar(mc);
  ofile << (double)mc << " " 
        << (double)polar.GetVBestLD() << " " 
        << (double)polar.GetBestLD() << " " 
        << (double)polar.GetVMin() << " " 
        << (double)polar.GetSMin() << " " 
        << (double)polar.GetVMax() << " " 
        << (double)polar.GetSMax() << "\n";
}

static void
basic_polar(const fixed mc)
{
  char bname[100];
  sprintf(bname,"output/results/res-polar-%02d-best.txt",(int)(mc*10));
  std::ofstream pfile("output/results/res-polar.txt");
  std::ofstream mfile(bname);

  GlidePolar polar(mc);
  for (fixed V= Vmin; V<= polar.GetVMax(); V+= fixed(0.25)) {
    pfile << (double)mc << " " 
          << (double)V << " " 
          << -(double)polar.SinkRate(V) << " " 
          << (double)(V/polar.SinkRate(V))
          << "\n";
  }

  mfile << (double)mc 
        << " " << 0
        << " " << (double)mc
        << " " << (double)polar.GetBestLD() 
        << "\n";
  mfile << (double)mc 
        << " " << (double)polar.GetVBestLD() 
        << " " << -(double)polar.GetSBestLD() 
        << " " << (double)polar.GetBestLD() 
        << "\n";
}


static void
test_glide_alt(const fixed h, const fixed W, const fixed Wangle,
               std::ostream &hfile)
{
  GlideSettings settings;
  settings.SetDefaults();

  GlidePolar polar(fixed(0));
  polar.SetMC(fixed(1));

  AircraftState ac;
  ac.wind.norm = fabs(W);
  if (negative(W)) {
    ac.wind.bearing = Angle::Degrees(fixed(180)+Wangle);
  } else {
    ac.wind.bearing = Angle::Degrees(Wangle);
  }
  ac.altitude = h;

  GeoVector vect(fixed(400.0), Angle::Zero());
  GlideState gs(vect, fixed(0), ac.altitude, ac.wind);
  GlideResult gr = MacCready::Solve(settings, polar, gs);
  hfile << (double)h << " " 
        << (double)gr.altitude_difference << " "
        << (double)gr.time_elapsed << " " 
        << (double)gr.v_opt << " " 
        << (double)W << " "
        << (double)Wangle << " "
        << "\n";
}

static void
test_glide_stf(const fixed h, const fixed W, const fixed Wangle, const fixed S,
               std::ostream &hfile)
{
  GlideSettings settings;
  settings.SetDefaults();

  GlidePolar polar(fixed(0));
  polar.SetMC(fixed(1));

  AircraftState ac;
  ac.wind.norm = fabs(W);
  if (negative(W)) {
    ac.wind.bearing = Angle::Degrees(fixed(180)+Wangle);
  } else {
    ac.wind.bearing = Angle::Degrees(Wangle);
  }
  ac.altitude = h;
  ac.netto_vario = S;

  GeoVector vect(fixed(400.0), Angle::Zero());
  GlideState gs(vect, fixed(0), ac.altitude, ac.wind);
  GlideResult gr = MacCready::Solve(settings, polar, gs);

  fixed Vstf = polar.SpeedToFly(ac, gr, false);

  hfile << (double)h << " " 
        << (double)gr.altitude_difference << " "
        << (double)gr.v_opt << " " 
        << (double)Vstf << " " 
        << (double)W << " "
        << (double)Wangle << " "
        << (double)ac.netto_vario << " "
        << "\n";
}

static bool
test_stf()
{
  { // variation with height
    std::ofstream hfile("output/results/res-polar-s0.txt");
    for (fixed h=fixed(0); h<fixed(40.0); h+= fixed(0.1)) {
      test_glide_stf(h,fixed(0),fixed(0),fixed(0),hfile);
    }
  }
  { // variation with S, below FG
    std::ofstream hfile("output/results/res-polar-s1.txt");
    for (fixed S=fixed(-4.0); S<fixed(4.0); S+= fixed(0.1)) {
      test_glide_stf(fixed(0), fixed(0),fixed(0),S, hfile);
    }
  }
  { // variation with S, above FG
    std::ofstream hfile("output/results/res-polar-s2.txt");
    for (fixed S=fixed(-4.0); S<fixed(4.0); S+= fixed(0.1)) {
      test_glide_stf(fixed(40), fixed(0),fixed(0),S, hfile);
    }
  }
  { // variation with S, below FG, wind
    std::ofstream hfile("output/results/res-polar-s3.txt");
    for (fixed S=fixed(-4.0); S<fixed(4.0); S+= fixed(0.1)) {
      test_glide_stf(fixed(0), fixed(10.0), fixed(0),S, hfile);
    }
  }
  { // variation with S, above FG, wind
    std::ofstream hfile("output/results/res-polar-s4.txt");
    for (fixed S=fixed(-4.0); S<fixed(4.0); S+= fixed(0.1)) {
      test_glide_stf(fixed(40), fixed(10.0), fixed(0), S, hfile);
    }
  }
  return true;
}

static bool
test_mc()
{
  {
    std::ofstream ofile("output/results/res-polar-m.txt");
    for (fixed mc=fixed(0); mc<fixed(5.0); mc+= fixed(0.1)) {
      basic_polar(mc);
      polar_mc(ofile, mc);
    }
  }

  {
    std::ofstream hfile("output/results/res-polar-h-00.txt");
    for (fixed h=fixed(0); h<fixed(40.0); h+= fixed(0.1)) {
      test_glide_alt(h, fixed(0), fixed(0), hfile);
    }
  }

  {
    std::ofstream hfile("output/results/res-polar-h-50.txt");
    for (fixed h=fixed(0); h<fixed(40.0); h+= fixed(0.1)) {
      test_glide_alt(h, fixed(5.0), fixed(0), hfile);
    }
  }

  {
    std::ofstream hfile("output/results/res-polar-w.txt");
    for (fixed w=fixed(-10.0); w<=fixed(10.0); w+= fixed(0.1)) {
      test_glide_alt(fixed(50.0), w, fixed(0), hfile);
    }
  }

  {
    std::ofstream hfile("output/results/res-polar-a.txt");
    for (fixed a=fixed(0); a<=fixed(360.0); a+= fixed(10)) {
      test_glide_alt(fixed(50.0), fixed(10.0), a, hfile);
    }
  }
  return true;
}

static void
test_glide_cb(const fixed h, const fixed W, const fixed Wangle,
              std::ostream &hfile)
{
  GlideSettings settings;
  settings.SetDefaults();

  GlidePolar polar(fixed(1));

  AircraftState ac;
  ac.wind.norm = fabs(W);
  if (negative(W)) {
    ac.wind.bearing = Angle::Degrees(fixed(180)+Wangle);
  } else {
    ac.wind.bearing = Angle::Degrees(Wangle);
  }
  ac.altitude = h;

  GeoVector vect(fixed(400.0), Angle::Zero());
  GlideState gs (vect, fixed(0), ac.altitude, ac.wind);
  GlideResult gr = MacCready::Solve(settings, polar, gs);

  gr.CalcDeferred();

  hfile << (double)W << " "
        << (double)Wangle << " "
        << (double)gr.vector.bearing.Degrees() << " "
        << (double)gr.cruise_track_bearing.Degrees() << " "
        << "\n";
}

static bool
test_cb()
{
  {
    std::ofstream hfile("output/results/res-polar-cb.txt");
    for (fixed a = fixed(0); a <= fixed(360.0); a+= fixed(10)) {
      test_glide_cb(fixed(0), fixed(10.0), a, hfile);
    }
  }
  return true;
}

int main() {

  plan_tests(3);

  Directory::Create(_T("output/results"));

  ok(test_mc(),"mc output",0);
  ok(test_stf(),"mc stf",0);
  ok(test_cb(),"cruise bearing",0);

  return exit_status();

}

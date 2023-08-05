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

#define ENABLE_SCREEN

#include "Main.hpp"
#include "Screen/SingleWindow.hpp"
#include "Screen/ButtonWindow.hpp"
#include "Screen/Timer.hpp"
#include "Screen/Canvas.hpp"
#include "Fonts.hpp"
#include "Look/TaskLook.hpp"
#include "Look/FinalGlideBarLook.hpp"
#include "Renderer/FinalGlideBarRenderer.hpp"
#include "NMEA/Derived.hpp"
#include "Geo/SpeedVector.hpp"
#include "Engine/GlideSolvers/GlideState.hpp"
#include "Engine/GlideSolvers/MacCready.hpp"
#include "Engine/GlideSolvers/GlideSettings.hpp"
#include "Engine/GlideSolvers/GlidePolar.hpp"

#ifdef USE_GDI
#include "ResourceLoader.hpp"
#endif

class FinalGlideBarWindow : public PaintWindow
{
  FinalGlideBarRenderer renderer;
  GlideState state;
  GlidePolar glide_polar;
  DerivedInfo calculated;

  GlideSettings glide_settings;

public:
  FinalGlideBarWindow(const FinalGlideBarLook &look, const TaskLook &task_look)
    :renderer(look, task_look),
     state(GeoVector(fixed(100), Angle::Zero()),
           fixed(1000), fixed(1000),
           SpeedVector(Angle::Zero(), fixed(0)))
  {
    glide_polar = GlidePolar(fixed(0));

    calculated.task_stats.total.solution_remaining =
      MacCready::Solve(glide_settings, glide_polar, state);

    calculated.task_stats.total.solution_mc0 =
      MacCready::Solve(glide_settings, glide_polar, state);

    calculated.task_stats.task_valid = true;
  }

  fixed GetAltitudeDifference() {
    return calculated.task_stats.total.solution_remaining.altitude_difference;
  }

  fixed GetAltitudeDifference0() {
    return calculated.task_stats.total.solution_mc0.altitude_difference;
  }

  void SetAltitudeDifference(fixed altitude_difference) {
    state.altitude_difference = altitude_difference;

    calculated.task_stats.total.solution_remaining =
      MacCready::Solve(glide_settings, glide_polar, state);
  }

  void SetAltitudeDifference0(fixed altitude_difference0) {
    state.altitude_difference = altitude_difference0;

    calculated.task_stats.total.solution_mc0 =
      MacCready::Solve(glide_settings, glide_polar, state);
  }

protected:
  virtual void OnPaint(Canvas &canvas) override {
    canvas.ClearWhite();
    renderer.Draw(canvas, canvas.GetRect(), calculated, glide_settings, true);
  }
};

class TestWindow : public SingleWindow
{
  ButtonWindow close_button;
  FinalGlideBarWindow final_glide;
  fixed step;
  fixed mc_mc0_step;

  WindowTimer timer;

  enum {
    ID_START = 100,
    ID_CLOSE
  };

public:
  TestWindow(const FinalGlideBarLook &look, const TaskLook &task_look)
    :final_glide(look, task_look), step(fixed(10)), mc_mc0_step(fixed(100)), timer(*this)
  {
    timer.Schedule(100);
  }

  ~TestWindow() {
    timer.Cancel();
  }


  void Create(PixelSize size) {
    SingleWindow::Create(_T("RunFinalGlideBarRenderer"),
                         size);

    const PixelRect rc = GetClientRect();

    WindowStyle with_border;
    with_border.Border();

    final_glide.Create(*this, rc, with_border);

    PixelRect button_rc = rc;
    button_rc.top = button_rc.bottom - 30;
    close_button.Create(*this, _T("Close"), ID_CLOSE, button_rc);
  }

protected:
  virtual bool OnCommand(unsigned id, unsigned code) override {
    switch (id) {
    case ID_CLOSE:
      Close();
      return true;
    }

    return SingleWindow::OnCommand(id, code);
  }

  virtual bool OnTimer(WindowTimer &_timer) override {
    if (_timer == timer) {
      fixed altitude_difference = final_glide.GetAltitudeDifference();
      fixed altitude_difference0 = final_glide.GetAltitudeDifference0();

      if (altitude_difference >= fixed(600) ) {
        step = fixed(-10);
      } else if (altitude_difference <= fixed(-600)) {
        step = fixed(10);

        if (altitude_difference0 > fixed(600)) {
          mc_mc0_step = fixed(-100);
        } else if (altitude_difference0 <= altitude_difference) {
          mc_mc0_step = fixed(100);
        }
 
        altitude_difference0 += mc_mc0_step;
      } 

      altitude_difference += step;
      altitude_difference0 += step;

      final_glide.SetAltitudeDifference(altitude_difference);
      final_glide.SetAltitudeDifference0(altitude_difference0);

      final_glide.Invalidate();

      return true;
    }

    return SingleWindow::OnTimer(_timer);
  }
};

static void
Main()
{
  FinalGlideBarLook final_glide_look;
  final_glide_look.Initialise(normal_font);

  TaskLook task_look;
  task_look.Initialise();

  TestWindow window(final_glide_look, task_look);
  window.Create({60, 320});

  window.Show();
  window.RunEventLoop();
}

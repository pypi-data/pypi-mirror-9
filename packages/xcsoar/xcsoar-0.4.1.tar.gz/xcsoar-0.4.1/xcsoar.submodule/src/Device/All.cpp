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

#include "Device/All.hpp"
#include "Device/List.hpp"
#include "Device/Descriptor.hpp"

void
devTick()
{
  for (DeviceDescriptor *i : device_list) {
    DeviceDescriptor &device = *i;
    device.OnSysTicker();
  }
}

void
AllDevicesAutoReopen(OperationEnvironment &env)
{
  for (DeviceDescriptor *i : device_list) {
    DeviceDescriptor &d = *i;
    d.AutoReopen(env);
  }
}

void
AllDevicesPutMacCready(fixed mac_cready, OperationEnvironment &env)
{
  for (DeviceDescriptor *i : device_list)
    i->PutMacCready(mac_cready, env);
}

void
AllDevicesPutBugs(fixed bugs, OperationEnvironment &env)
{
  for (DeviceDescriptor *i : device_list)
    i->PutBugs(bugs, env);
}

void
AllDevicesPutBallast(fixed fraction, fixed overload,
                     OperationEnvironment &env)
{
  for (DeviceDescriptor *i : device_list)
    i->PutBallast(fraction, overload, env);
}

void
AllDevicesPutVolume(unsigned volume, OperationEnvironment &env)
{
  for (DeviceDescriptor *i : device_list)
    i->PutVolume(volume, env);
}

void
AllDevicesPutActiveFrequency(RadioFrequency frequency,
                             const TCHAR *name,
                             OperationEnvironment &env)
{
  for (DeviceDescriptor *i : device_list)
    i->PutActiveFrequency(frequency, name, env);
}

void
AllDevicesPutStandbyFrequency(RadioFrequency frequency,
                              const TCHAR *name,
                              OperationEnvironment &env)
{
  for (DeviceDescriptor *i : device_list)
    i->PutStandbyFrequency(frequency, name, env);
}

void
AllDevicesPutQNH(const AtmosphericPressure &pres,
                 OperationEnvironment &env)
{
  for (DeviceDescriptor *i : device_list)
    i->PutQNH(pres, env);
}

void
AllDevicesNotifySensorUpdate(const MoreData &basic)
{
  for (DeviceDescriptor *i : device_list)
    i->OnSensorUpdate(basic);
}

void
AllDevicesNotifyCalculatedUpdate(const MoreData &basic,
                                 const DerivedInfo &calculated)
{
  for (DeviceDescriptor *i : device_list)
    i->OnCalculatedUpdate(basic, calculated);
}

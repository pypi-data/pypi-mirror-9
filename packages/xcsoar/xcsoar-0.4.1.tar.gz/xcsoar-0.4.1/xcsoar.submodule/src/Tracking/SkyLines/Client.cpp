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

#include "Client.hpp"
#include "Protocol.hpp"
#include "OS/ByteOrder.hpp"
#include "NMEA/Info.hpp"
#include "Util/CRC.hpp"

#ifdef HAVE_SKYLINES_TRACKING_HANDLER
#include "IO/Async/IOThread.hpp"
#include "Util/UTF8.hpp"
#include "Util/ConvertString.hpp"

#include <string>

void
SkyLinesTracking::Client::SetIOThread(IOThread *_io_thread)
{
  if (socket.IsDefined() && io_thread != nullptr && handler != nullptr)
    io_thread->LockRemove(socket.Get());

  io_thread = _io_thread;

  if (socket.IsDefined() && io_thread != nullptr && handler != nullptr)
    io_thread->LockAdd(socket.Get(), IOThread::READ, *this);
}

void
SkyLinesTracking::Client::SetHandler(Handler *_handler)
{
  if (socket.IsDefined() && io_thread != nullptr && handler != nullptr)
    io_thread->LockRemove(socket.Get());

  handler = _handler;

  if (socket.IsDefined() && io_thread != nullptr && handler != nullptr)
    io_thread->LockAdd(socket.Get(), IOThread::READ, *this);
}

#endif

bool
SkyLinesTracking::Client::Open(const SocketAddress &_address)
{
  assert(_address.IsDefined());

  Close();

  address = _address;
  if (!socket.CreateUDP())
    return false;

#ifdef HAVE_SKYLINES_TRACKING_HANDLER
  if (io_thread != nullptr && handler != nullptr)
    io_thread->LockAdd(socket.Get(), IOThread::READ, *this);
#endif

  return true;
}

void
SkyLinesTracking::Client::Close()
{
  if (!socket.IsDefined())
    return;

#ifdef HAVE_SKYLINES_TRACKING_HANDLER
  if (io_thread != nullptr && handler != nullptr)
    io_thread->LockRemove(socket.Get());
#endif

  socket.Close();
}

bool
SkyLinesTracking::Client::SendFix(const NMEAInfo &basic)
{
  assert(basic.time_available);

  if (key == 0 || !socket.IsDefined())
    return false;

  FixPacket packet;
  packet.header.magic = ToBE32(MAGIC);
  packet.header.crc = 0;
  packet.header.type = ToBE16(Type::FIX);
  packet.header.key = ToBE64(key);
  packet.flags = 0;

  packet.time = ToBE32(uint32_t(basic.time * 1000));
  packet.reserved = 0;

  if (basic.location_available) {
    packet.flags |= ToBE32(FixPacket::FLAG_LOCATION);
    ::GeoPoint location = basic.location;
    location.Normalize();
    packet.location.latitude = ToBE32(int(location.latitude.Degrees() * 1000000));
    packet.location.longitude = ToBE32(int(location.longitude.Degrees() * 1000000));
  } else
    packet.location.latitude = packet.location.longitude = 0;

  if (basic.track_available) {
    packet.flags |= ToBE32(FixPacket::FLAG_TRACK);
    packet.track = ToBE16(uint16_t(basic.track.AsBearing().Degrees()));
  } else
    packet.track = 0;

  if (basic.ground_speed_available) {
    packet.flags |= ToBE32(FixPacket::FLAG_GROUND_SPEED);
    packet.ground_speed = ToBE16(uint16_t(basic.ground_speed * 16));
  } else
    packet.ground_speed = 0;

  if (basic.airspeed_available) {
    packet.flags |= ToBE32(FixPacket::FLAG_AIRSPEED);
    packet.airspeed = ToBE16(uint16_t(basic.indicated_airspeed * 16));
  } else
    packet.airspeed = 0;

  if (basic.baro_altitude_available) {
    packet.flags |= ToBE32(FixPacket::FLAG_ALTITUDE);
    packet.altitude = ToBE16(int(basic.baro_altitude));
  } else if (basic.gps_altitude_available) {
    packet.flags |= ToBE32(FixPacket::FLAG_ALTITUDE);
    packet.altitude = ToBE16(int(basic.gps_altitude));
  } else
    packet.altitude = 0;

  if (basic.total_energy_vario_available) {
    packet.flags |= ToBE32(FixPacket::FLAG_VARIO);
    packet.vario = ToBE16(int(basic.total_energy_vario * 256));
  } else if (basic.netto_vario_available) {
    packet.flags |= ToBE32(FixPacket::FLAG_VARIO);
    packet.vario = ToBE16(int(basic.netto_vario * 256));
  } else if (basic.noncomp_vario_available) {
    packet.flags |= ToBE32(FixPacket::FLAG_VARIO);
    packet.vario = ToBE16(int(basic.noncomp_vario * 256));
  } else
    packet.vario = 0;

  if (basic.engine_noise_level_available) {
    packet.flags |= ToBE32(FixPacket::FLAG_ENL);
    packet.engine_noise_level = ToBE16(basic.engine_noise_level);
  } else
    packet.engine_noise_level = 0;

  packet.header.crc = ToBE16(UpdateCRC16CCITT(&packet, sizeof(packet), 0));

  return socket.Write(&packet, sizeof(packet), address) == sizeof(packet);
}

bool
SkyLinesTracking::Client::SendPing(uint16_t id)
{
  if (key == 0 || !socket.IsDefined())
    return false;

  PingPacket packet;
  packet.header.magic = ToBE32(MAGIC);
  packet.header.crc = 0;
  packet.header.type = ToBE16(Type::PING);
  packet.header.key = ToBE64(key);
  packet.id = ToBE16(id);
  packet.reserved = 0;
  packet.reserved2 = 0;

  packet.header.crc = ToBE16(UpdateCRC16CCITT(&packet, sizeof(packet), 0));

  return socket.Write(&packet, sizeof(packet), address) == sizeof(packet);
}

bool
SkyLinesTracking::Client::SendTrafficRequest(bool followees, bool club)
{
  if (key == 0 || !socket.IsDefined())
    return false;

  TrafficRequestPacket packet;
  packet.header.magic = ToBE32(MAGIC);
  packet.header.crc = 0;
  packet.header.type = ToBE16(Type::TRAFFIC_REQUEST);
  packet.header.key = ToBE64(key);
  packet.flags = ToBE32((followees ? packet.FLAG_FOLLOWEES : 0)
                        | (club ? packet.FLAG_CLUB : 0));
  packet.reserved = 0;

  packet.header.crc = ToBE16(UpdateCRC16CCITT(&packet, sizeof(packet), 0));

  return socket.Write(&packet, sizeof(packet), address) == sizeof(packet);
}

bool
SkyLinesTracking::Client::SendUserNameRequest(uint32_t user_id)
{
  if (key == 0 || !socket.IsDefined())
    return false;

  UserNameRequestPacket packet;
  packet.header.magic = ToBE32(MAGIC);
  packet.header.crc = 0;
  packet.header.type = ToBE16(Type::USER_NAME_REQUEST);
  packet.header.key = ToBE64(key);
  packet.user_id = ToBE32(user_id);
  packet.reserved = 0;

  packet.header.crc = ToBE16(UpdateCRC16CCITT(&packet, sizeof(packet), 0));

  return socket.Write(&packet, sizeof(packet), address) == sizeof(packet);
}

#ifdef HAVE_SKYLINES_TRACKING_HANDLER

inline void
SkyLinesTracking::Client::OnTrafficReceived(const TrafficResponsePacket &packet,
                                            size_t length)
{
  const unsigned n = packet.traffic_count;
  const TrafficResponsePacket::Traffic *traffic =
    (const TrafficResponsePacket::Traffic *)(&packet + 1);

  if (length != sizeof(packet) + n * sizeof(*traffic))
    return;

  const TrafficResponsePacket::Traffic *end = traffic + n;
  for (; traffic != end; ++traffic)
    handler->OnTraffic(FromBE32(traffic->pilot_id),
                       FromBE32(traffic->time),
                       ::GeoPoint(Angle::Degrees(fixed(FromBE32(traffic->location.longitude)) / 1000000),
                                  Angle::Degrees(fixed(FromBE32(traffic->location.latitude)) / 1000000)),
                       FromBE16(traffic->altitude));
}

inline void
SkyLinesTracking::Client::OnUserNameReceived(const UserNameResponsePacket &packet,
                                             size_t length)
{
  if (length != sizeof(packet) + packet.name_length)
    return;

  /* the name follows the UserNameResponsePacket object */
  const char *_name = (const char *)(&packet + 1);
  const std::string name(_name, packet.name_length);
  if (!ValidateUTF8(name.c_str()))
    return;

  UTF8ToWideConverter tname(name.c_str());
  handler->OnUserName(FromBE32(packet.user_id), tname);
}

inline void
SkyLinesTracking::Client::OnDatagramReceived(void *data, size_t length)
{
  Header &header = *(Header *)data;
  if (length < sizeof(header))
    return;

  const uint16_t received_crc = FromBE16(header.crc);
  header.crc = 0;

  const uint16_t calculated_crc = UpdateCRC16CCITT(data, length, 0);
  if (received_crc != calculated_crc)
    return;

  const ACKPacket &ack = *(const ACKPacket *)data;
  const TrafficResponsePacket &traffic = *(const TrafficResponsePacket *)data;
  const UserNameResponsePacket &user_name =
    *(const UserNameResponsePacket *)data;

  switch ((Type)FromBE16(header.type)) {
  case PING:
  case FIX:
  case TRAFFIC_REQUEST:
  case USER_NAME_REQUEST:
    break;

  case ACK:
    handler->OnAck(FromBE16(ack.id));
    break;

  case TRAFFIC_RESPONSE:
    OnTrafficReceived(traffic, length);
    break;

  case USER_NAME_RESPONSE:
    OnUserNameReceived(user_name, length);
    break;
  }
}

bool
SkyLinesTracking::Client::OnFileEvent(int fd, unsigned mask)
{
  if (!socket.IsDefined())
    return false;

  uint8_t buffer[4096];
  ssize_t nbytes;
  SocketAddress source_address;

  while ((nbytes = socket.Read(buffer, sizeof(buffer), source_address)) > 0)
    if (source_address == address)
      OnDatagramReceived(buffer, nbytes);

  return true;
}

#endif

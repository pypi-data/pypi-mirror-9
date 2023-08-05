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

#include "Tracking/SkyLines/Client.hpp"
#include "NMEA/Info.hpp"
#include "OS/Args.hpp"
#include "Util/NumberParser.hpp"
#include "Util/StringUtil.hpp"
#include "DebugReplay.hpp"

#ifdef HAVE_SKYLINES_TRACKING_HANDLER
#include "IO/Async/GlobalIOThread.hpp"

class Handler : public SkyLinesTracking::Handler {
  Mutex mutex;
  Cond cond;

  bool done;

public:
  Handler():done(false) {}

  bool Wait(unsigned timeout_ms=5000) {
    const ScopeLock protect(mutex);
    return done || (cond.Wait(mutex, timeout_ms) && done);
  }

protected:
  void Done() {
    const ScopeLock protect(mutex);
    done = true;
    cond.Broadcast();
  }

public:
  virtual void OnAck(unsigned id) override {
    printf("received ack %u\n", id);
    Done();
  }

  virtual void OnTraffic(unsigned pilot_id, unsigned time_of_day_ms,
                         const GeoPoint &location, int altitude) override {
    BrokenTime time = BrokenTime::FromSecondOfDay(time_of_day_ms / 1000);

    printf("received traffic pilot=%u time=%02u:%02u:%02u location=%f/%f altitude=%d\n",
           pilot_id, time.hour, time.minute, time.second,
           (double)location.longitude.Degrees(),
           (double)location.latitude.Degrees(),
           altitude);
    Done();
  }
};

#endif

int
main(int argc, char *argv[])
{
  Args args(argc, argv, "HOST KEY");
  const char *host = args.ExpectNext();
  const char *key = args.ExpectNext();

  SocketAddress address;
  if (!address.Lookup(host, "5597", SOCK_DGRAM)) {
    fprintf(stderr, "Failed to look up: %s\n", host);
    return EXIT_FAILURE;
  }

#ifdef HAVE_SKYLINES_TRACKING_HANDLER
  InitialiseIOThread();
#endif

  SkyLinesTracking::Client client;

#ifdef HAVE_SKYLINES_TRACKING_HANDLER
  client.SetIOThread(io_thread);

  Handler handler;
  client.SetHandler(&handler);
#endif

  client.SetKey(ParseUint64(key, NULL, 16));
  if (!client.Open(address)) {
    fprintf(stderr, "Failed to create client\n");
    return EXIT_FAILURE;
  }

  if (args.IsEmpty() || StringIsEqual(args.PeekNext(), "fix")) {
    NMEAInfo basic;
    basic.Reset();
    basic.UpdateClock();
    basic.time = fixed(1);
    basic.time_available.Update(basic.clock);

    return client.SendFix(basic) ? EXIT_SUCCESS : EXIT_FAILURE;
  } else if (StringIsEqual(args.PeekNext(), "ping")) {
    client.SendPing(1);

#ifdef HAVE_SKYLINES_TRACKING_HANDLER
    handler.Wait();
#endif
  } else if (StringIsEqual(args.PeekNext(), "traffic")) {
    client.SendTrafficRequest(true, true);

#ifdef HAVE_SKYLINES_TRACKING_HANDLER
    handler.Wait();
#endif
  } else {
    DebugReplay *replay = CreateDebugReplay(args);
    if (replay == NULL)
      return EXIT_FAILURE;

    while (replay->Next()) {
      client.SendFix(replay->Basic());
      usleep(100000);
    }
  }

#ifdef HAVE_SKYLINES_TRACKING_HANDLER
  client.Close();
  DeinitialiseIOThread();
#endif

  return EXIT_SUCCESS;
}

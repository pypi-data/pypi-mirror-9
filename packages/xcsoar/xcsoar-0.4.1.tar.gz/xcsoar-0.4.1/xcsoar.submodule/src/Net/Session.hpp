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

#ifndef NET_SESSION_HPP
#define NET_SESSION_HPP

#include "Net/Features.hpp"

#ifdef HAVE_WININET
#include "Net/WinINet/WinINet.hpp"
#endif

#ifdef HAVE_CURL
#include "Net/CURL/Multi.hpp"
#endif

namespace Net {
  class Session {
#ifdef HAVE_WININET
    /** Internal session handle */
    WinINet::SessionHandle handle;
#endif

#ifdef HAVE_CURL
    CurlMulti multi;
#endif

  public:
#ifdef HAVE_WININET
    friend class Connection;
    friend class Request;
#endif

#ifndef HAVE_CURL
    /**
     * Opens a session that can be used for
     * connections and registers the necessary callback.
     */
    Session();
#endif

    /**
     * Was the session created successfully
     * @return True if session was created successfully
     */
#ifdef HAVE_CURL
    bool Error() const {
      return !multi.IsDefined();
    }

    bool Add(CURL *easy) {
      return multi.Add(easy);
    }

    void Remove(CURL *easy) {
      return multi.Remove(easy);
    }

    bool Select(int timeout_ms);

    CURLMcode Perform() {
      return multi.Perform();
    }

    CURLcode InfoRead(const CURL *easy) {
      return multi.InfoRead(easy);
    }
#else
    bool Error() const;
#endif
  };
}

#endif

#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2011, 2012, 2014 SMHI

# Author(s):

#   Martin Raspaud <martin.raspaud@smhi.se>

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""Manage other's subscriptions.
"""
import logging
from datetime import datetime, timedelta 

import time
# pylint: disable=E0611
from zmq import REQ, REP, LINGER, POLLIN, NOBLOCK, Poller
# pylint: enable=E0611

from posttroll import context
from posttroll.address_receiver import AddressReceiver
from posttroll.message import Message


logger = logging.getLogger(__name__)

class TimeoutError(BaseException):
    """A timeout.
    """
    pass

### Client functions.

def get_pub_addresses(names=None, timeout=10):
    """Get the address of the publisher for a given list of publisher *names*.
    """
    addrs = []
    if names is None:
        names = ["", ]
    for name in names:
        then = datetime.now() + timedelta(seconds=timeout)
        while datetime.now() < then:
            addrs += get_pub_address(name)
            if addrs:
                break
            time.sleep(.5)
    return addrs

def get_pub_address(name, timeout=10):
    """Get the address of the publisher for a given publisher *name*.
    """

    # Socket to talk to server
    socket = context.socket(REQ)
    try:
        socket.setsockopt(LINGER, timeout*1000)
        socket.connect("tcp://localhost:5555")

        poller = Poller()
        poller.register(socket, POLLIN)


        message = Message("/oper/ns", "request", {"service": name})
        socket.send(str(message))

        # Get the reply.
        sock = poller.poll(timeout=timeout * 1000)
        if sock:
            if sock[0][0] == socket:
                message = Message.decode(socket.recv(NOBLOCK))
                return message.data
        else:
            raise TimeoutError("Didn't get an address after %d seconds."
                               %timeout)
    finally:
        socket.close()

### Server part.

def get_active_address(name, arec):
    """Get the addresses of the active modules for a given publisher *name*.
    """
    addrs = arec.get(name)
    if addrs:
        return Message("/oper/ns", "info", addrs)
    else:
        return Message("/oper/ns", "info", "")


class NameServer(object):
    """The name server.
    """
    def __init__(self, max_age=timedelta(minutes=10)):
        self.loop = True
        self.listener = None
        self._max_age = max_age

    def run(self, *args):
        """Run the listener and answer to requests.
        """
        del args

        arec = AddressReceiver(max_age=self._max_age)
        arec.start()
        port = 5555

        try:
            self.listener = context.socket(REP)
            self.listener.bind("tcp://*:"+str(port))
            poller = Poller()
            poller.register(self.listener, POLLIN)
            while self.loop:
                socks = dict(poller.poll(1000))
                if socks:
                    if socks.get(self.listener) == POLLIN:
                        msg = self.listener.recv()
                else:
                    continue
                logger.debug("Replying to request: " + str(msg))
                msg = Message.decode(msg)
                self.listener.send_unicode(str(get_active_address(
                    msg.data["service"], arec)))
        except KeyboardInterrupt:
            # Needed to stop the nameserver.
            pass
        finally:
            arec.stop()
            self.listener.close()

    def stop(self):
        """Stop the name server.
        """
        self.listener.setsockopt(LINGER, 0)
        self.loop = False

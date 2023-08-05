#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2011, 2012, 2013, 2014.

# Author(s):

#   Martin Raspaud    <martin.raspaud@smhi.se>
#   Lars Ø. Rasmussen <ras@dmi.dk>

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

"""Simple library to subscribe to messages.
"""
import logging
from datetime import datetime, timedelta
from urlparse import urlsplit

import time
# pylint: disable=E0611
from zmq import (SUB, Poller, LINGER,
                 POLLIN, SUBSCRIBE, PULL, NOBLOCK, ZMQError)
# pylint: enable=E0611
from posttroll import context
from posttroll.message import Message, _MAGICK
from posttroll.ns import get_pub_address


logger = logging.getLogger(__name__)

class Subscriber(object):
    """Subscriber

    Subscribes to *addresses* for *topics*, and perform address translation of
    *translate* is true. The function *message_filter* can be used to
    discriminate some messages on the subscriber side. *topics* on the other
    hand performs filtering on the publishing side (from zeromq 3).

    Example::

        from posttroll.subscriber import Subscriber, get_pub_address

        addr = get_pub_address(service, timeout=2)
        sub = Subscriber([addr], 'my_topic')
        try:
            for msg in sub(timeout=2):
                print "Consumer got", msg

        except KeyboardInterrupt:
            print "terminating consumer..."
            sub.close()

    """
    def __init__(self, addresses, topics='', message_filter=None,
                 translate=False):
        self._topics = self._magickfy_topics(topics)
        self._filter = message_filter
        self._translate = translate

        self.sub_addr = {}
        self.addr_sub = {}
        self.poller = None

        self._hooks = []
        self._hooks_cb = {}

        self.update(addresses)

        self.poller = Poller()
        self._loop = True

    def add(self, address, topics=None):
        """Add *address* to the subscribing list for *topics*.

        It topics is None we will subscibe to already specified topics.
        """
        if address in self.addresses:
            return False

        topics = self._magickfy_topics(topics) or self._topics
        logger.info("Subscriber adding address " + str(address)
                    + " with topics " + str(topics))
        subscriber = context.socket(SUB)
        for t__ in topics:
            subscriber.setsockopt(SUBSCRIBE, t__)
        subscriber.connect(address)
        self.sub_addr[subscriber] = address
        self.addr_sub[address] = subscriber
        if self.poller:
            self.poller.register(subscriber, POLLIN)
        return True

    def remove(self, address):
        """Remove *address* from the subscribing list for *topics*.
        """
        try:
            subscriber = self.addr_sub[address]
        except KeyError:
            return False
        logger.info("Subscriber removing address " + str(address))
        if self.poller:
            self.poller.unregister(subscriber)
        del self.addr_sub[address]
        del self.sub_addr[subscriber]
        subscriber.close()
        return True

    def update(self, addresses):
        """Updating with a set of addresses.
        """
        if isinstance(addresses, (str, unicode)):
            addresses = [addresses,]
        s0_, s1_ = set(self.addresses), set(addresses)
        sr_, sa_ = s0_.difference(s1_), s1_.difference(s0_)
        for a__ in sr_:
            self.remove(a__)
        for a__ in sa_:
            self.add(a__)
        return bool(sr_ or sa_)

    def add_hook_sub(self, address, topics, callback):
        """Specify a *callback* in the same stream (thread) as the main receive
        loop. The callback will be called with the received messages from the
        specified subscription.

        Good for operations, which is required to be done in the same thread as
        the main recieve loop (e.q operations on the underlying sockets).
        """
        logger.info("Subscriber adding SUB hook " + str(address)
                    + " for topics " + str(topics))
        socket = context.socket(SUB)
        for t__ in self._magickfy_topics(topics):
            socket.setsockopt(SUBSCRIBE, t__)
        socket.connect(address)
        self._add_hook(socket, callback)

    def add_hook_pull(self, address, callback):
        """Same as above, but with a PULL socket.
        (e.g good for pushed 'inproc' messages from another thread).
        """
        logger("Subscriber adding PULL hook " + str(address))
        socket = context.socket(PULL)
        socket.connect(address)
        self._add_hook(socket, callback)

    def _add_hook(self, socket, callback):
        """Generic hook. The passed socket has to be "receive only".
        """
        self._hooks.append(socket)
        self._hooks_cb[socket] = callback
        if self.poller:
            self.poller.register(socket, POLLIN)

    @property
    def addresses(self):
        """Get the addresses
        """
        return self.sub_addr.values()

    @property
    def subscribers(self):
        """Get the subscribers
        """
        return self.sub_addr.keys()

    def recv(self, timeout=None):
        """Receive, optionally with *timeout* in seconds.
        """
        if timeout:
            timeout *= 1000.

        for sub in self.subscribers + self._hooks:
            self.poller.register(sub, POLLIN)
        self._loop = True
        try:
            while self._loop:
                try:
                    socks = dict(self.poller.poll(timeout=timeout))
                    if socks:
                        for sub in self.subscribers:
                            if sub in socks and socks[sub] == POLLIN:
                                m__ = Message.decode(sub.recv(NOBLOCK))
                                if not self._filter or self._filter(m__):
                                    if self._translate:
                                        url = urlsplit(self.sub_addr[sub])
                                        host = url[1].split(":")[0]
                                        m__.sender = (m__.sender.split("@")[0]
                                                      + "@" + host)
                                    yield m__

                        for sub in self._hooks:
                            if sub in socks and socks[sub] == POLLIN:
                                m__ = Message.decode(sub.recv(NOBLOCK))
                                self._hooks_cb[sub](m__)
                    else:
                        # timeout
                        yield None
                except ZMQError, err:
                    logger.exception("Receive failed " + str(err))
        finally:
            for sub in self.subscribers + self._hooks:
                self.poller.unregister(sub)

    def __call__(self, **kwargs):
        return self.recv(**kwargs)

    def stop(self):
        """Stop the subscriber.
        """
        self._loop = False

    def close(self):
        """Close the subscriber: stop it and close the local subscribers.
        """
        self.stop()
        for sub in self.subscribers + self._hooks:
            sub.setsockopt(LINGER, 0)
            sub.close()

    @staticmethod
    def _magickfy_topics(topics):
        """Add the magick to the topics if missing.
        """
        # If topic does not start with messages._MAGICK (pytroll:/), it will be
        # prepended.
        if topics is None:
            return None
        if isinstance(topics, (str, unicode)):
            topics = [topics,]
        ts_ = []
        for t__ in topics:
            if not t__.startswith(_MAGICK):
                if t__ and t__[0] == '/':
                    t__ = _MAGICK + t__
                else:
                    t__ = _MAGICK + '/' + t__
            ts_.append(t__)
        return ts_

    def __del__(self):
        for sub in self.subscribers + self._hooks:
            try:
                sub.close()
            except:
                pass


class NSSubscriber(object):
    """Automatically subscribe to *services* (requesting addresses from the
    nameserver. If *topics* are specified, filter the messages through the
    beginning of the subject. *addr_listener* allows to add new services on the
    fly as they appear on the network. Additional *addresses* to subscribe to
    can be specified, and address translation can be performed if *translate*
    is set to True (False by default). The *timeout* here is specified in
    seconds.

    Note: 'services = None', means no services, and 'services =""' means all
    services.
    """

    def __init__(self, services=None, topics=_MAGICK, addr_listener=False,
                 addresses=None, timeout=10, translate=False):
        """ Note: services = None, means no services
                  services = "", means all services
        """

        self._services = _to_array(services)
        self._topics = _to_array(topics)
        self._addresses = _to_array(addresses)

        self._timeout = timeout
        self._translate = translate

        self._subscriber = None
        self._addr_listener = addr_listener

    def start(self):
        """Start the subscriber.
        """
        def _get_addr_loop(service, timeout):
            """Try to get the address of *service* until for *timeout* seconds.
            """
            then = datetime.now() + timedelta(seconds=timeout)
            while datetime.now() < then:
                addrs = get_pub_address(service)
                if addrs:
                    return [addr["URI"] for addr in addrs]
                time.sleep(1)
            return []

        # Search for addresses corresponding to service.
        for service in self._services:
            addr = _get_addr_loop(service, self._timeout)
            if not addr:
                logger.warning("Can't get any address for " + service)
            else:
                logger.debug("Got address for " + str(service)
                             + ": " + str(addr))
            self._addresses.extend(addr)

        # Subscribe to those services and topics.
        logger.debug("Subscribing to topics " + str(self._topics))
        self._subscriber = Subscriber(self._addresses,
                                      self._topics,
                                      translate=self._translate)

        if self._addr_listener:
            self._addr_listener = _AddressListener(self._subscriber,
                                                   self._services)

        return self._subscriber

    def stop(self):
        """Stop the subscriber.
        """
        if self._subscriber is not None:
            self._subscriber.close()
            self._subscriber = None



class Subscribe(NSSubscriber):
    """Subscriber context. See :class:`NSSubscriber` for initialization
    parameters.

    Example::

        from posttroll.subscriber import Subscribe

        with Subscribe("a_service", "my_topic",) as sub:
            for msg in sub.recv():
                print msg

    """
    def __enter__(self):
        return self.start()

    def __exit__(self, exc_type, exc_val, exc_tb):
        return self.stop()

def _to_array(obj):
    """Convert *obj* to list if not already one.
    """
    if isinstance(obj, (str, unicode)):
        return [obj,]
    if obj is None:
        return []
    return obj

class _AddressListener(object):
    """Listener for new addresses of interest.
    """
    def __init__(self, subscriber, services=""):
        if isinstance(services, (str, unicode)):
            services = [services,]
        self.services = services
        self.subscriber = subscriber
        self.subscriber.add_hook_sub("tcp://localhost:16543",
                                     ["pytroll://address",],
                                     self.handle_msg)

    def handle_msg(self, msg):
        """handle the message *msg*.
        """
        addr_ = msg.data["URI"]
        status = msg.data.get('status', True)
        if status:
            service = msg.data.get('service')
            for service in self.services:
                if not service or service in service:
                    logger.debug("Adding address " + str(addr_)
                                 + str(service))
                    self.subscriber.add(addr_)
                    break
        else:
            logger.debug("Removing address " + str(addr_))
            self.subscriber.remove(addr_)

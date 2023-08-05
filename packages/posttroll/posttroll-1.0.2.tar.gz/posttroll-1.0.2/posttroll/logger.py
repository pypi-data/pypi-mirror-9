#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2012, 2014, 2015 Martin Raspaud

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

"""Logger for pytroll system.
"""


# TODO: remove old hanging subscriptions

from posttroll.subscriber import Subscribe
from posttroll.publisher import NoisyPublisher
from posttroll.message import Message
from threading import Thread

import copy
import logging
import logging.handlers

logger = logging.getLogger(__name__)


class PytrollFormatter(logging.Formatter):

    """Formats a pytroll message inside a log record.
    """

    def __init__(self, fmt, datefmt):
        logging.Formatter.__init__(self, fmt, datefmt)

    def format(self, record):
        subject = "/".join(("log", record.levelname, str(record.name)))
        mesg = Message(subject, "log." + str(record.levelname).lower(),
                       record.getMessage())
        return str(mesg)


class PytrollHandler(logging.Handler):

    """Sends the record through a pytroll publisher.
    """

    def __init__(self, name, port=0):
        logging.Handler.__init__(self)
        self._publisher = NoisyPublisher(name, port)
        self._publisher.start()

    def emit(self, record):
        message = self.format(record)
        self._publisher.send(message)

    def close(self):
        self._publisher.stop()
        logging.Handler.close(self)


BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(8)

COLORS = {
    'WARNING': YELLOW,
    'INFO': GREEN,
    'DEBUG': BLUE,
    'CRITICAL': MAGENTA,
    'ERROR': RED
}

COLOR_SEQ = "\033[1;%dm"
RESET_SEQ = "\033[0m"


class ColoredFormatter(logging.Formatter):

    """Adds a color for the levelname.
    """

    def __init__(self, msg, use_color=True):
        logging.Formatter.__init__(self, msg)
        self.use_color = use_color

    def format(self, record):
        levelname = record.levelname
        if self.use_color and levelname in COLORS:
            levelname_color = (COLOR_SEQ % (30 + COLORS[levelname])
                               + levelname + RESET_SEQ)
            record2 = copy.copy(record)
            record2.levelname = levelname_color
        return logging.Formatter.format(self, record2)


# logging.basicConfig(format='[%(asctime)s %(levelname)s] %(message)s',
#                    level=logging.DEBUG)


class Logger(object):

    """The logging machine.

    Contains a thread listening to incomming messages, and a thread logging.
    """

    def __init__(self,
                 (nameserver_address, nameserver_port)=("localhost", 16543)):
        del nameserver_address, nameserver_port
        self.log_thread = Thread(target=self.log)
        self.loop = True

    def start(self):
        """Starts the logging.
        """
        self.log_thread.start()

    def log(self):
        """Log stuff.
        """
        with Subscribe(services=[""], addr_listener=True) as sub:
            for msg in sub.recv(1):
                if msg:
                    if msg.type in ["log.debug", "log.info",
                                    "log.warning", "log.error",
                                    "log.critical"]:
                        getattr(logger, msg.type[4:])(msg.subject + " " +
                                                      msg.sender + " " +
                                                      str(msg.data) + " " +
                                                      str(msg.time))

                    elif msg.binary:
                        logger.debug(msg.subject + " " +
                                     msg.sender + " " +
                                     msg.type + " " +
                                     "[binary] " +
                                     str(msg.time))
                    else:
                        logger.debug(msg.subject + " " +
                                     msg.sender + " " +
                                     msg.type + " " +
                                     str(msg.data) + " " +
                                     str(msg.time))
                if not self.loop:
                    logger.info("Stop logging")
                    break

    def stop(self):
        """Stop the machine.
        """
        self.loop = False


def run():
    """Main function
    """
    import argparse

    global logger

    parser = argparse.ArgumentParser()
    parser.add_argument("-r", "--rotated", help="Time rotated log file")
    parser.add_argument("-v", "--verbose", help="print debug messages too",
                        action="store_true")
    parser.add_argument("-s", "--server", help="server to listen to",
                        default="localhost")
    parser.add_argument("-p", "--port", help="port to listen to",
                        default=16543,
                        type=int)
    opts = parser.parse_args()

    if opts.verbose:
        loglevel = logging.DEBUG
    else:
        loglevel = logging.INFO

    if opts.rotated:
        handler = logging.handlers.TimedRotatingFileHandler(opts.rotated,
                                                            when="midnight",
                                                            backupCount=7)
    else:
        handler = logging.StreamHandler()

    logger = logging.getLogger("pytroll")
    logger.setLevel(loglevel)

    handler.setLevel(loglevel)

    formatter = ColoredFormatter("[%(asctime)s %(levelname)-19s] %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    import time
    try:
        tlogger = Logger((opts.server, opts.port))
        #logger = Logger(("safe", 16543))
        tlogger.start()
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        tlogger.stop()
        print ("Thanks for using pytroll/logger. "
               "See you soon on www.pytroll.org!")

if __name__ == '__main__':
    run()

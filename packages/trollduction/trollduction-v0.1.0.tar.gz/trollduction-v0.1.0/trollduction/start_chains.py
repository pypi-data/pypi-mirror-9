#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2012, 2013, 2014 Martin Raspaud

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

"""Start trollstalker and trollduction chains.

TODO:
 - Support chains that wait for messages, not files

"""

from ConfigParser import ConfigParser
import os
from urlparse import urlparse
import pyinotify
import fnmatch
import shutil
import logging, logging.handlers
import subprocess
import time
import glob
import sys
from trollduction import Trollduction
logger = logging.getLogger(__name__)

### Config management

def read_config(filename):
    """Read the config file called *filename*.
    """
    cp_ = ConfigParser()
    cp_.read(filename)

    res = {}

    for section in cp_.sections():
        if section == "default":
            continue
        res[section] = dict(cp_.items(section))

    return res


def reload_config(filename):
    """Rebuild chains if needed (if the configuration changed) from *filename*.
    """
    if os.path.abspath(filename) != os.path.abspath(cmd_args.config_file):
        return

    logger.debug("New config file detected! " + filename)

    new_chains = read_config(filename)

    old_glob = []

    for key, val in new_chains.iteritems():
        if key in chains:
            identical = True
            for key2, val2 in new_chains[key].iteritems():
                if ((key2 not in chains[key]) or
                    (chains[key][key2] != val2)):
                    identical = False
                    break
            if not identical:
                chains[key]["notifier"].stop()
                chains[key]["producer"].shutdown()
                chains[key] = val
                chains[key]["notifier"] = create_notifier(val)
                # create logger too!
                chains[key]["notifier"].start()
                old_glob.append(urlparse(val["origin"]).path)
                chains[key]["producer"] = Trollduction(val["config"])
                chains[key]["producer"].start()
                logger.debug("Updated " + key)
        else:
            # notifier
            chains[key] = val
            chains[key]["notifier"] = create_notifier(val)
            chains[key]["notifier"].start()
            old_glob.append(urlparse(val["origin"]).path)
            # create logger too!
            # batch producer
            chains[key]["producer"] = Trollduction(val["config"])
            chains[key]["producer"].start()
            logger.debug("Added " + key)
    for key in set(chains.keys()) - set(new_chains.keys()):
        chains[key]["notifier"].stop()
        del chains[key]
        logger.debug("Removed " + key)

    logger.debug("Reloaded config from " + filename)
    if old_glob:
        fnames = []
        for pattern in old_glob:
            fnames += glob.glob(os.path.join(pattern, "*"))
        if fnames:
            time.sleep(3)
            logger.debug("Touching old files")
            for fname in fnames:
                if os.path.exists(fname):
                    fp_ = open(fname, "ab")
                    fp_.close()
        old_glob = []

### Generic event handler

class EventHandler(pyinotify.ProcessEvent):
    """Handle events with a generic *fun* function.
    """

    def __init__(self, fun, *args, **kwargs):
        pyinotify.ProcessEvent.__init__(self, *args, **kwargs)
        self._fun = fun

    def process_IN_CLOSE_WRITE(self, event):
        """On closing after writing.
        """
        self._fun(event.pathname)

    def process_IN_CREATE(self, event):
        """On closing after linking.
        """
        try:
            if os.stat(event.pathname).st_nlink > 1:
                self._fun(event.pathname)
        except OSError:
            return

    def process_IN_MOVED_TO(self, event):
        """On closing after moving.
        """
        self._fun(event.pathname)



from trollstalker import create_notifier as cnot

def create_notifier(attrs):
    """Create a notifier from the specified configuration attributes *attrs*.
    """
    print attrs
    print "create a new trollstalker instance"
    url = urlparse(attrs["origin"])
    return cnot(attrs["file_tags"], int(attrs["publish_port"]),
                attrs["filepattern_cfg"], url.path)

def terminate(chains):
    for chain in chains.itervalues():
        chain["notifier"].stop()
        chain["producer"].shutdown()
    logger.info("Shutting down.")
    print ("Thank you for using pytroll/move_it."
           " See you soon on pytroll.org!")
    time.sleep(1)
    sys.exit(0)

if __name__ == '__main__':
    import argparse
    import signal

    parser = argparse.ArgumentParser()
    parser.add_argument("config_file", help="The configuration file to run on.")
    parser.add_argument("-l", "--log",
                        help="The file to log to. stdout otherwise.")
    cmd_args = parser.parse_args()

    log_format = "[%(asctime)s %(levelname)-8s] %(name)s: %(message)s"
    logger = logging.getLogger('')
    logger.setLevel(logging.DEBUG)

    if cmd_args.log:
        fh = logging.handlers.TimedRotatingFileHandler(
            os.path.join(cmd_args.log),
            "midnight",
            backupCount=7)
    else:
        fh = logging.StreamHandler()

    formatter = logging.Formatter(log_format)
    fh.setFormatter(formatter)

    logger.addHandler(fh)

    pyinotify.log.handlers = [fh]

    logger = logging.getLogger('move_it')
    logger.setLevel(logging.DEBUG)

    logger.info("Starting up")
    chains = {}

    mask = (pyinotify.IN_CLOSE_WRITE |
            pyinotify.IN_MOVED_TO |
            pyinotify.IN_CREATE)
    watchman = pyinotify.WatchManager()

    notifier = pyinotify.Notifier(watchman, EventHandler(reload_config))
    watchman.add_watch(os.path.dirname(cmd_args.config_file), mask)

    def chains_stop(*args):
        """Stop everything.
        """
        del args
        terminate(chains)

    signal.signal(signal.SIGTERM, chains_stop)

    try:
        reload_config(cmd_args.config_file)
        notifier.loop()
    except:
        logger.exception("Something went wrong")
    finally:
        logger.info("Shutting down")
        chains_stop()


#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2013, 2014

# Author(s):

#   Panu Lahtinen <panu.lahtinen@fmi.fi>
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

'''Listener module for Trollduction.'''

from posttroll.subscriber import NSSubscriber
from Queue import Queue
from threading import Thread
import time
import logging

logger = logging.getLogger(__name__)


class ListenerContainer(object):

    '''Container for listener instance
    '''

    def __init__(self, topics=None):
        self.listener = None
        self.queue = None
        self.thread = None

        if topics is not None:
            # Create queue for the messages
            self.queue = Queue()  # Pipe()

            # Create a Listener instance
            self.listener = Listener(topics=topics, queue=self.queue)
            # Start Listener instance into a new daemonized thread.
            self.thread = Thread(target=self.listener.run)
            self.thread.setDaemon(True)
            self.thread.start()

    def restart_listener(self, topics):
        '''Restart listener after configuration update.
        '''
        if self.listener is not None:
            if self.listener.running:
                self.stop()
        self.__init__(topics=topics)

    def stop(self):
        '''Stop listener.'''
        logger.debug("Stopping listener.")
        self.listener.stop()
        self.thread.join()
        self.thread = None
        logger.debug("Listener stopped.")


class Listener(object):

    '''PyTroll listener class for reading messages for Trollduction
    '''

    def __init__(self, topics=None, queue=None):
        '''Init Listener object
        '''
        self.topics = topics
        self.queue = queue
        self.subscriber = None
        self.recv = None
        self.create_subscriber()
        self.running = False

    def create_subscriber(self):
        '''Create a subscriber instance using specified addresses and
        message types.
        '''
        if self.subscriber is None:
            if self.topics:
                self.subscriber = NSSubscriber("", self.topics,
                                               addr_listener=True)
                self.recv = self.subscriber.start().recv

    def add_to_queue(self, msg):
        '''Add message to queue
        '''
        self.queue.put(msg)

    def run(self):
        '''Run listener
        '''

        self.running = True

        for msg in self.recv(1):
            if msg is None:
                if self.running:
                    continue
                else:
                    break

            self.add_to_queue(msg)

    def stop(self):
        '''Stop subscriber and delete the instance
        '''
        self.running = False
        time.sleep(1)
        self.subscriber.stop()
        self.subscriber = None

    def restart(self):
        '''Restart subscriber
        '''
        self.stop()
        self.create_subscriber()
        self.run()

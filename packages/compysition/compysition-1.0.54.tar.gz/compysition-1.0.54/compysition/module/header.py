#!/usr/bin/env python
#
# -*- coding: utf-8 -*-
#
#  header.py
#
#  Copyright 2014 Adam Fiebig <fiebig.adam@gmail.com>
#  Originally based on 'wishbone' project by smetj
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#
#

from compysition import Actor


class Header(Actor):

    '''**Adds information to event headers.**


    Parameters:

        - name(str)
           |  The name of the module.

        - size(int)
           |  The default max length of each queue.

        - frequency(int)
           |  The frequency in seconds to generate metrics.

        - key(str)(self.name)
           |  The header key to store the information.

        - header(dict)({})
           |  The data to store.

        - expr(str)(None)
           |  printf-style String Formatting.
           |  Expects event["data"] to be a dictionary.


    Queues:

        - inbox
           |  Incoming events.

        - outbox
           |  Outgoing events.
    '''

    def __init__(self, name, key=None, header={}, expr=None, *args, **kwargs):
        Actor.__init__(self, name, *args, **kwargs)
        if key is None:
            self.key = name
        else:
            self.key = key

        self.header = header
        self.expr = expr

        if expr is None:
            self.addHeader = self.__doHeader
        else:
            self.addHeader = self.__doPrintf

    def consume(self, event):
        event = self.addHeader(event)
        self.send_event(event)

    def __doHeader(self, event):
        event["header"][self.key] = self.header
        return event

    def __doPrintf(self, event, *args, **kwargs):
        try:
            return self.expr % event["data"]
        except Exception as err:
            self.logger.error("String replace failed.  Reason: %s" % (err))
            return event

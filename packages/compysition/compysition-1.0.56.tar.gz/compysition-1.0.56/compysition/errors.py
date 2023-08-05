#!/usr/bin/env python
#
# -*- coding: utf-8 -*-
#
#  error.py
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


class QueueLocked(Exception):
    pass

"""
class QueueEmpty(Exception):
    def __init__(self, message, waitUntilFull, waitUntilContent):
        Exception.__init__(self, message)
        self.waitUntilFull = waitUntilFull
        self.waitUntilContent = waitUntilContent
"""
class QueueEmpty(Exception):
    def __init__(self, message):
        Exception.__init__(self, message)

"""
class QueueFull(Exception):
    def __init__(self, message, waitUntilEmpty, waitUntilFree):
        Exception.__init__(self, message)
        self.waitUntilEmpty = waitUntilEmpty
        self.waitUntilFree = waitUntilFree
"""

class QueueFull(Exception):
    def __init__(self, message):
        Exception.__init__(self, message)

class QueueMissing(Exception):
    pass


class QueueOccupied(Exception):
    pass


class QueueConnected(Exception):
    pass


class SetupError(Exception):
    pass


class ReservedName(Exception):
    pass


class ModuleInitFailure(Exception):
    pass


class NoSuchModule(Exception):
    pass

class NoConnectedQueues(Exception):
    pass

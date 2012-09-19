# -*- coding: utf-8 -*-
#
# papyon - a python client library for Msn
#
# Copyright (C) 2012 the emesene team
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

class Signal(object):

    def connect(self, signal, slot, *args):
        ''' connects a signal, returns an integer that identifies it '''
        raise NotImplementedError

    def disconnect(self, sig_id):
        ''' disconnects a signal given its id '''
        raise NotImplementedError

    def emit(self, signal, *args):
        ''' emits a signal '''
        raise NotImplementedError

    def notify(self, prop):
        ''' notifies a certain property has changed
            similar to gobjects' notify::property '''
        raise NotImplementedError

import gobject

class GObject(Signal, gobject.GObject):
    
    def connect(self, signal, slot, *args):
        ''' connects a signal, returns an integer that identifies it '''
        gobject.GObject.connect(self, signal, slot, *args)

    def disconnect(self, sig_id):
        ''' disconnects a signal given its id '''
        if sig_id is not None:
            gobject.GObject.disconnect(self, sig_id)

    def emit(self, signal, *args):
        ''' emits a signal '''
        gobject.GObject.emit(self, signal, *args)

    def notify(self, prop):
        ''' notifies a certain property has changed
            similar to gobjects' notify::property '''
        gobject.GObject.notify(self, prop)

def type_register(what):
    gobject.type_register(what)

SIGNAL_RUN_FIRST = gobject.SIGNAL_RUN_FIRST
SIGNAL_RUN_LAST = gobject.SIGNAL_RUN_LAST
TYPE_NONE = gobject.TYPE_NONE
TYPE_INT = gobject.TYPE_INT
TYPE_STRING = gobject.TYPE_STRING
TYPE_PYOBJECT = gobject.TYPE_PYOBJECT
TYPE_UINT = gobject.TYPE_UINT
TYPE_BOOLEAN = gobject.TYPE_BOOLEAN
TYPE_ULONG = gobject.TYPE_ULONG
G_MAXUINT = gobject.G_MAXUINT
PARAM_READABLE = gobject.PARAM_READABLE

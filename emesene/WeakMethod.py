# -*- coding: utf-8 -*-

#    This file is part of emesene.
#
#    emesene is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 3 of the License, or
#    (at your option) any later version.
#
#    emesene is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with emesene; if not, write to the Free Software
#    Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

# http://code.activestate.com/recipes/81253/

import weakref

class WeakMethodBound(object):

    def __init__(self, f):
        self.f = weakref.ref(f.im_func)
        self.c = weakref.ref(f.im_self)

    def __call__(self, *arg):
        if self.c() is None:
            raise TypeError('Method called on dead object')

        self.f()(self.c(), *arg)

    def __eq__(self, other):
        return self.f == other.f and self.c == other.c

class WeakMethodFree(object):

    def __init__(self, f):
        self.f = weakref.ref(f)

    def __call__(self, *arg):
        if self.f() is None:
            raise TypeError('Function no longer exist')

        self.f()(*arg)

    def __eq__(self, other):
        return self.f == other.f

def WeakMethod(f):
    try:
        f.im_func
    except AttributeError:
        return WeakMethodFree(f)

    return WeakMethodBound(f)

# http://stackoverflow.com/a/1364959
class CallbackWrapper(object):
    def __init__(self, sender, callback):
        self.weak_obj = weakref.ref(callback.im_self)
        self.weak_fun = weakref.ref(callback.im_func)
        self.sender = sender
        self.handle = None

    def __call__(self, *things):
        obj = self.weak_obj()
        fun = self.weak_fun()
        if obj is not None and fun is not None:
            return fun(obj, *things)
        elif self.handle is not None:
            self.sender.disconnect(self.handle)
            self.handle = None
            self.sender = None

def weak_connect(sender, signal, callback):
    wrapper = CallbackWrapper(sender, callback)
    wrapper.handle = sender.connect(signal, wrapper)
    return wrapper

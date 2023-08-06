# Copyright 2015 Sean Vig
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from pywayland.interface import Interface, InterfaceMeta
from .surface import Surface

import six


@six.add_metaclass(InterfaceMeta)
class Touch(Interface):
    """touchscreen input device

    The wl_touch interface represents a touchscreen
    associated with a seat.

    Touch interactions can consist of one or more contacts.
    For each contact, a series of events is generated, starting
    with a down event, followed by zero or more motion events,
    and ending with an up event. Events relating to the same
    contact point can be identified by the ID of the sequence.
    """
    name = "wl_touch"
    version = 3


@Touch.request("3", [])
def release(self):
    """release the touch object"""
    self._marshal(0)
    self._destroy()


@Touch.event("uuoiff", [None, None, Surface, None, None, None])
def down(self, serial, time, surface, id, x, y):
    """touch down event and beginning of a touch sequence

    A new touch point has appeared on the surface. This touch point is
    assigned a unique @id. Future events from this touchpoint reference
    this ID. The ID ceases to be valid after a touch up event and may be
    re-used in the future.

    :param serial:
    :type serial: `uint`
    :param time: timestamp with millisecond granularity
    :type time: `uint`
    :param surface:
    :type surface: :class:`Surface`
    :param id: the unique ID of this touch point
    :type id: `int`
    :param x: x coordinate in surface-relative coordinates
    :type x: `fixed`
    :param y: y coordinate in surface-relative coordinates
    :type y: `fixed`
    """
    self._post_event(0, serial, time, surface, id, x, y)


@Touch.event("uui", [None, None, None])
def up(self, serial, time, id):
    """end of a touch event sequence

    The touch point has disappeared. No further events will be sent for
    this touchpoint and the touch point's ID is released and may be
    re-used in a future touch down event.

    :param serial:
    :type serial: `uint`
    :param time: timestamp with millisecond granularity
    :type time: `uint`
    :param id: the unique ID of this touch point
    :type id: `int`
    """
    self._post_event(1, serial, time, id)


@Touch.event("uiff", [None, None, None, None])
def motion(self, time, id, x, y):
    """update of touch point coordinates

    A touchpoint has changed coordinates.

    :param time: timestamp with millisecond granularity
    :type time: `uint`
    :param id: the unique ID of this touch point
    :type id: `int`
    :param x: x coordinate in surface-relative coordinates
    :type x: `fixed`
    :param y: y coordinate in surface-relative coordinates
    :type y: `fixed`
    """
    self._post_event(2, time, id, x, y)


@Touch.event("", [])
def frame(self):
    """end of touch frame event

    Indicates the end of a contact point list.
    """
    self._post_event(3)


@Touch.event("", [])
def cancel(self):
    """touch session cancelled

    Sent if the compositor decides the touch stream is a global
    gesture. No further events are sent to the clients from that
    particular gesture. Touch cancellation applies to all touch points
    currently active on this client's surface. The client is
    responsible for finalizing the touch points, future touch points on
    this surface may re-use the touch point ID.
    """
    self._post_event(4)


Touch._gen_c()

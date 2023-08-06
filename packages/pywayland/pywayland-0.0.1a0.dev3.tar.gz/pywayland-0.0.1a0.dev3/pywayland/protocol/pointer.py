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

import enum
import six


@six.add_metaclass(InterfaceMeta)
class Pointer(Interface):
    """Pointer input device

    The :class:`Pointer` interface represents one or more input devices,
    such as mice, which control the pointer location and pointer_focus
    of a seat.

    The :class:`Pointer` interface generates motion, enter and leave
    events for the surfaces that the pointer is located over,
    and button and axis events for button presses, button releases
    and scrolling.
    """
    name = "wl_pointer"
    version = 3

    error = enum.Enum("error", {
        "role": 0,
    })

    button_state = enum.Enum("button_state", {
        "released": 0,
        "pressed": 1,
    })

    axis = enum.Enum("axis", {
        "vertical_scroll": 0,
        "horizontal_scroll": 1,
    })


@Pointer.request("u?oii", [None, Surface, None, None])
def set_cursor(self, serial, surface, hotspot_x, hotspot_y):
    """Set the pointer surface

    Set the pointer surface, i.e., the surface that contains the
    pointer image (cursor). This request gives the surface the role
    of a cursor. If the surface already has another role, it raises
    a protocol error.

    The cursor actually changes only if the pointer
    focus for this device is one of the requesting client's surfaces
    or the surface parameter is the current pointer surface. If
    there was a previous surface set with this request it is
    replaced. If surface is NULL, the pointer image is hidden.

    The parameters hotspot_x and hotspot_y define the position of
    the pointer surface relative to the pointer location. Its
    top-left corner is always at (x, y) - (hotspot_x, hotspot_y),
    where (x, y) are the coordinates of the pointer location, in surface
    local coordinates.

    On surface.attach requests to the pointer surface, hotspot_x
    and hotspot_y are decremented by the x and y parameters
    passed to the request. Attach must be confirmed by
    :func:`Surface.commit() <pywayland.protocol.surface.Surface.commit>` as usual.

    The hotspot can also be updated by passing the currently set
    pointer surface to this request with new values for hotspot_x
    and hotspot_y.

    The current and pending input regions of the :class:`~pywayland.protocol.surface.Surface` are
    cleared, and :func:`Surface.set_input_region() <pywayland.protocol.surface.Surface.set_input_region>` is ignored until the
    :class:`~pywayland.protocol.surface.Surface` is no longer used as the cursor. When the use as a
    cursor ends, the current and pending input regions become
    undefined, and the :class:`~pywayland.protocol.surface.Surface` is unmapped.

    :param serial: serial of the enter event
    :type serial: `uint`
    :param surface:
    :type surface: :class:`~pywayland.protocol.surface.Surface` or `None`
    :param hotspot_x: x coordinate in surface-relative coordinates
    :type hotspot_x: `int`
    :param hotspot_y: y coordinate in surface-relative coordinates
    :type hotspot_y: `int`
    """
    self._marshal(0, serial, surface, hotspot_x, hotspot_y)


@Pointer.request("3", [])
def release(self):
    """Release the pointer object"""
    self._marshal(1)
    self._destroy()


@Pointer.event("uoff", [None, Surface, None, None])
def enter(self, serial, surface, surface_x, surface_y):
    """Enter event

    Notification that this seat's pointer is focused on a certain
    surface.

    When an seat's focus enters a surface, the pointer image
    is undefined and a client should respond to this event by setting
    an appropriate pointer image with the set_cursor request.

    :param serial:
    :type serial: `uint`
    :param surface:
    :type surface: :class:`~pywayland.protocol.surface.Surface`
    :param surface_x: x coordinate in surface-relative coordinates
    :type surface_x: `fixed`
    :param surface_y: y coordinate in surface-relative coordinates
    :type surface_y: `fixed`
    """
    self._post_event(0, serial, surface, surface_x, surface_y)


@Pointer.event("uo", [None, Surface])
def leave(self, serial, surface):
    """Leave event

    Notification that this seat's pointer is no longer focused on
    a certain surface.

    The leave notification is sent before the enter notification
    for the new focus.

    :param serial:
    :type serial: `uint`
    :param surface:
    :type surface: :class:`~pywayland.protocol.surface.Surface`
    """
    self._post_event(1, serial, surface)


@Pointer.event("uff", [None, None, None])
def motion(self, time, surface_x, surface_y):
    """Pointer motion event

    Notification of pointer location change. The arguments
    surface_x and surface_y are the location relative to the
    focused surface.

    :param time: timestamp with millisecond granularity
    :type time: `uint`
    :param surface_x: x coordinate in surface-relative coordinates
    :type surface_x: `fixed`
    :param surface_y: y coordinate in surface-relative coordinates
    :type surface_y: `fixed`
    """
    self._post_event(2, time, surface_x, surface_y)


@Pointer.event("uuuu", [None, None, None, None])
def button(self, serial, time, button, state):
    """Pointer button event

    Mouse button click and release notifications.

    The location of the click is given by the last motion or
    enter event.
    The time argument is a timestamp with millisecond
    granularity, with an undefined base.

    :param serial:
    :type serial: `uint`
    :param time: timestamp with millisecond granularity
    :type time: `uint`
    :param button:
    :type button: `uint`
    :param state:
    :type state: `uint`
    """
    self._post_event(3, serial, time, button, state)


@Pointer.event("uuf", [None, None, None])
def axis(self, time, axis, value):
    """Axis event

    Scroll and other axis notifications.

    For scroll events (vertical and horizontal scroll axes), the
    value parameter is the length of a vector along the specified
    axis in a coordinate space identical to those of motion events,
    representing a relative movement along the specified axis.

    For devices that support movements non-parallel to axes multiple
    axis events will be emitted.

    When applicable, for example for touch pads, the server can
    choose to emit scroll events where the motion vector is
    equivalent to a motion event vector.

    When applicable, clients can transform its view relative to the
    scroll distance.

    :param time: timestamp with millisecond granularity
    :type time: `uint`
    :param axis:
    :type axis: `uint`
    :param value:
    :type value: `fixed`
    """
    self._post_event(4, time, axis, value)


Pointer._gen_c()

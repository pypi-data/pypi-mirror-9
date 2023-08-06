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
class Keyboard(Interface):
    """Keyboard input device

    The :class:`Keyboard` interface represents one or more keyboards
    associated with a seat.
    """
    name = "wl_keyboard"
    version = 4

    keymap_format = enum.Enum("keymap_format", {
        "no_keymap": 0,
        "xkb_v1": 1,
    })

    key_state = enum.Enum("key_state", {
        "released": 0,
        "pressed": 1,
    })


@Keyboard.request("3", [])
def release(self):
    """Release the keyboard object"""
    self._marshal(0)
    self._destroy()


@Keyboard.event("uhu", [None, None, None])
def keymap(self, format, fd, size):
    """Keyboard mapping

    This event provides a file descriptor to the client which can be
    memory-mapped to provide a keyboard mapping description.

    :param format:
    :type format: `uint`
    :param fd:
    :type fd: `fd`
    :param size:
    :type size: `uint`
    """
    self._post_event(0, format, fd, size)


@Keyboard.event("uoa", [None, Surface, None])
def enter(self, serial, surface, keys):
    """Enter event

    Notification that this seat's keyboard focus is on a certain
    surface.

    :param serial:
    :type serial: `uint`
    :param surface:
    :type surface: :class:`~pywayland.protocol.surface.Surface`
    :param keys: the currently pressed keys
    :type keys: `array`
    """
    self._post_event(1, serial, surface, keys)


@Keyboard.event("uo", [None, Surface])
def leave(self, serial, surface):
    """Leave event

    Notification that this seat's keyboard focus is no longer on
    a certain surface.

    The leave notification is sent before the enter notification
    for the new focus.

    :param serial:
    :type serial: `uint`
    :param surface:
    :type surface: :class:`~pywayland.protocol.surface.Surface`
    """
    self._post_event(2, serial, surface)


@Keyboard.event("uuuu", [None, None, None, None])
def key(self, serial, time, key, state):
    """Key event

    A key was pressed or released.
    The time argument is a timestamp with millisecond
    granularity, with an undefined base.

    :param serial:
    :type serial: `uint`
    :param time: timestamp with millisecond granularity
    :type time: `uint`
    :param key:
    :type key: `uint`
    :param state:
    :type state: `uint`
    """
    self._post_event(3, serial, time, key, state)


@Keyboard.event("uuuuu", [None, None, None, None, None])
def modifiers(self, serial, mods_depressed, mods_latched, mods_locked, group):
    """Modifier and group state

    Notifies clients that the modifier and/or group state has
    changed, and it should update its local state.

    :param serial:
    :type serial: `uint`
    :param mods_depressed:
    :type mods_depressed: `uint`
    :param mods_latched:
    :type mods_latched: `uint`
    :param mods_locked:
    :type mods_locked: `uint`
    :param group:
    :type group: `uint`
    """
    self._post_event(4, serial, mods_depressed, mods_latched, mods_locked, group)


@Keyboard.event("4ii", [None, None])
def repeat_info(self, rate, delay):
    """Repeat rate and delay

    Informs the client about the keyboard's repeat rate and delay.

    This event is sent as soon as the :class:`Keyboard` object has been created,
    and is guaranteed to be received by the client before any key press
    event.

    Negative values for either rate or delay are illegal. A rate of zero
    will disable any repeating (regardless of the value of delay).

    This event can be sent later on as well with a new value if necessary,
    so clients should continue listening for the event past the creation
    of :class:`Keyboard`.

    :param rate: the rate of repeating keys in characters per second
    :type rate: `int`
    :param delay: delay in milliseconds since key down until repeating starts
    :type delay: `int`
    """
    self._post_event(5, rate, delay)


Keyboard._gen_c()

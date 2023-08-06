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
from .keyboard import Keyboard
from .pointer import Pointer
from .touch import Touch

import enum
import six


@six.add_metaclass(InterfaceMeta)
class Seat(Interface):
    """group of input devices

    A seat is a group of keyboards, pointer and touch devices. This
    object is published as a global during start up, or when such a
    device is hot plugged.  A seat typically has a pointer and
    maintains a keyboard focus and a pointer focus.
    """
    name = "wl_seat"
    version = 4

    capability = enum.Enum("capability", {
        "pointer": 1,
        "keyboard": 2,
        "touch": 4,
    })


@Seat.request("n", [Pointer])
def get_pointer(self):
    """return pointer object

    The ID provided will be initialized to the wl_pointer interface
    for this seat.

    This request only takes effect if the seat has the pointer
    capability.

    :returns: :class:`Pointer`
    """
    id = self._marshal_constructor(0, Pointer)
    return id


@Seat.request("n", [Keyboard])
def get_keyboard(self):
    """return keyboard object

    The ID provided will be initialized to the wl_keyboard interface
    for this seat.

    This request only takes effect if the seat has the keyboard
    capability.

    :returns: :class:`Keyboard`
    """
    id = self._marshal_constructor(1, Keyboard)
    return id


@Seat.request("n", [Touch])
def get_touch(self):
    """return touch object

    The ID provided will be initialized to the wl_touch interface
    for this seat.

    This request only takes effect if the seat has the touch
    capability.

    :returns: :class:`Touch`
    """
    id = self._marshal_constructor(2, Touch)
    return id


@Seat.event("u", [None])
def capabilities(self, capabilities):
    """seat capabilities changed

    This is emitted whenever a seat gains or loses the pointer,
    keyboard or touch capabilities.  The argument is a capability
    enum containing the complete set of capabilities this seat has.

    :param capabilities:
    :type capabilities: `uint`
    """
    self._post_event(0, capabilities)


@Seat.event("2s", [None])
def name(self, name):
    """unique identifier for this seat

    In a multiseat configuration this can be used by the client to help
    identify which physical devices the seat represents. Based on
    the seat configuration used by the compositor.

    :param name:
    :type name: `string`
    """
    self._post_event(1, name)


Seat._gen_c()

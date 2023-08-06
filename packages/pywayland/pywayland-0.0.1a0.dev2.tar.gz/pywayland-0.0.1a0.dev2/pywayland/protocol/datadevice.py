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
from .dataoffer import DataOffer
from .datasource import DataSource
from .surface import Surface

import enum
import six


@six.add_metaclass(InterfaceMeta)
class DataDevice(Interface):
    """data transfer device

    There is one wl_data_device per seat which can be obtained
    from the global wl_data_device_manager singleton.

    A wl_data_device provides access to inter-client data transfer
    mechanisms such as copy-and-paste and drag-and-drop.
    """
    name = "wl_data_device"
    version = 2

    error = enum.Enum("error", {
        "role": 0,
    })


@DataDevice.request("?oo?ou", [DataSource, Surface, Surface, None])
def start_drag(self, source, origin, icon, serial):
    """start drag-and-drop operation

    This request asks the compositor to start a drag-and-drop
    operation on behalf of the client.

    The source argument is the data source that provides the data
    for the eventual data transfer. If source is NULL, enter, leave
    and motion events are sent only to the client that initiated the
    drag and the client is expected to handle the data passing
    internally.

    The origin surface is the surface where the drag originates and
    the client must have an active implicit grab that matches the
    serial.

    The icon surface is an optional (can be NULL) surface that
    provides an icon to be moved around with the cursor.  Initially,
    the top-left corner of the icon surface is placed at the cursor
    hotspot, but subsequent wl_surface.attach request can move the
    relative position. Attach requests must be confirmed with
    wl_surface.commit as usual. The icon surface is given the role of
    a drag-and-drop icon. If the icon surface already has another role,
    it raises a protocol error.

    The current and pending input regions of the icon wl_surface are
    cleared, and wl_surface.set_input_region is ignored until the
    wl_surface is no longer used as the icon surface. When the use
    as an icon ends, the current and pending input regions become
    undefined, and the wl_surface is unmapped.

    :param source:
    :type source: :class:`DataSource` or `None`
    :param origin:
    :type origin: :class:`Surface`
    :param icon:
    :type icon: :class:`Surface` or `None`
    :param serial: serial of the implicit grab on the origin
    :type serial: `uint`
    """
    self._marshal(0, source, origin, icon, serial)


@DataDevice.request("?ou", [DataSource, None])
def set_selection(self, source, serial):
    """copy data to the selection

    This request asks the compositor to set the selection
    to the data from the source on behalf of the client.

    To unset the selection, set the source to NULL.

    :param source:
    :type source: :class:`DataSource` or `None`
    :param serial: serial of the event that triggered this request
    :type serial: `uint`
    """
    self._marshal(1, source, serial)


@DataDevice.request("2", [])
def release(self):
    """destroy data device

    This request destroys the data device.
    """
    self._marshal(2)
    self._destroy()


@DataDevice.event("n", [DataOffer])
def data_offer(self, id):
    """introduce a new wl_data_offer

    The data_offer event introduces a new wl_data_offer object,
    which will subsequently be used in either the
    data_device.enter event (for drag-and-drop) or the
    data_device.selection event (for selections).  Immediately
    following the data_device_data_offer event, the new data_offer
    object will send out data_offer.offer events to describe the
    mime types it offers.

    :param id:
    :type id: :class:`DataOffer`
    """
    self._post_event(0, id)


@DataDevice.event("uoff?o", [None, Surface, None, None, DataOffer])
def enter(self, serial, surface, x, y, id):
    """initiate drag-and-drop session

    This event is sent when an active drag-and-drop pointer enters
    a surface owned by the client.  The position of the pointer at
    enter time is provided by the x and y arguments, in surface
    local coordinates.

    :param serial:
    :type serial: `uint`
    :param surface:
    :type surface: :class:`Surface`
    :param x:
    :type x: `fixed`
    :param y:
    :type y: `fixed`
    :param id:
    :type id: :class:`DataOffer` or `None`
    """
    self._post_event(1, serial, surface, x, y, id)


@DataDevice.event("", [])
def leave(self):
    """end drag-and-drop session

    This event is sent when the drag-and-drop pointer leaves the
    surface and the session ends.  The client must destroy the
    wl_data_offer introduced at enter time at this point.
    """
    self._post_event(2)


@DataDevice.event("uff", [None, None, None])
def motion(self, time, x, y):
    """drag-and-drop session motion

    This event is sent when the drag-and-drop pointer moves within
    the currently focused surface. The new position of the pointer
    is provided by the x and y arguments, in surface local
    coordinates.

    :param time: timestamp with millisecond granularity
    :type time: `uint`
    :param x:
    :type x: `fixed`
    :param y:
    :type y: `fixed`
    """
    self._post_event(3, time, x, y)


@DataDevice.event("", [])
def drop(self):
    """end drag-and-drag session successfully

    The event is sent when a drag-and-drop operation is ended
    because the implicit grab is removed.
    """
    self._post_event(4)


@DataDevice.event("?o", [DataOffer])
def selection(self, id):
    """advertise new selection

    The selection event is sent out to notify the client of a new
    wl_data_offer for the selection for this device.  The
    data_device.data_offer and the data_offer.offer events are
    sent out immediately before this event to introduce the data
    offer object.  The selection event is sent to a client
    immediately before receiving keyboard focus and when a new
    selection is set while the client has keyboard focus.  The
    data_offer is valid until a new data_offer or NULL is received
    or until the client loses keyboard focus.  The client must
    destroy the previous selection data_offer, if any, upon receiving
    this event.

    :param id:
    :type id: :class:`DataOffer` or `None`
    """
    self._post_event(5, id)


DataDevice._gen_c()

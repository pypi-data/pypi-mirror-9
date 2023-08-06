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

import enum
import six


@six.add_metaclass(InterfaceMeta)
class Output(Interface):
    """Compositor output region

    An output describes part of the compositor geometry.  The
    compositor works in the 'compositor coordinate system' and an
    output corresponds to rectangular area in that space that is
    actually visible.  This typically corresponds to a monitor that
    displays part of the compositor space.  This object is published
    as global during start up, or when a monitor is hotplugged.
    """
    name = "wl_output"
    version = 2

    subpixel = enum.Enum("subpixel", {
        "unknown": 0,
        "none": 1,
        "horizontal_rgb": 2,
        "horizontal_bgr": 3,
        "vertical_rgb": 4,
        "vertical_bgr": 5,
    })

    transform = enum.Enum("transform", {
        "normal": 0,
        "90": 1,
        "180": 2,
        "270": 3,
        "flipped": 4,
        "flipped_90": 5,
        "flipped_180": 6,
        "flipped_270": 7,
    })

    mode = enum.Enum("mode", {
        "current": 0x1,
        "preferred": 0x2,
    })


@Output.event("iiiiissi", [None, None, None, None, None, None, None, None])
def geometry(self, x, y, physical_width, physical_height, subpixel, make, model, transform):
    """Properties of the output

    The geometry event describes geometric properties of the output.
    The event is sent when binding to the output object and whenever
    any of the properties change.

    :param x: x position within the global compositor space
    :type x: `int`
    :param y: y position within the global compositor space
    :type y: `int`
    :param physical_width: width in millimeters of the output
    :type physical_width: `int`
    :param physical_height: height in millimeters of the output
    :type physical_height: `int`
    :param subpixel: subpixel orientation of the output
    :type subpixel: `int`
    :param make: textual description of the manufacturer
    :type make: `string`
    :param model: textual description of the model
    :type model: `string`
    :param transform: transform that maps framebuffer to output
    :type transform: `int`
    """
    self._post_event(0, x, y, physical_width, physical_height, subpixel, make, model, transform)


@Output.event("uiii", [None, None, None, None])
def mode(self, flags, width, height, refresh):
    """Advertise available modes for the output

    The mode event describes an available mode for the output.

    The event is sent when binding to the output object and there
    will always be one mode, the current mode.  The event is sent
    again if an output changes mode, for the mode that is now
    current.  In other words, the current mode is always the last
    mode that was received with the current flag set.

    The size of a mode is given in physical hardware units of
    the output device. This is not necessarily the same as
    the output size in the global compositor space. For instance,
    the output may be scaled, as described in :func:`Output.scale`,
    or transformed , as described in :func:`Output.transform`.

    :param flags: bitfield of mode flags
    :type flags: `uint`
    :param width: width of the mode in hardware units
    :type width: `int`
    :param height: height of the mode in hardware units
    :type height: `int`
    :param refresh: vertical refresh rate in mHz
    :type refresh: `int`
    """
    self._post_event(1, flags, width, height, refresh)


@Output.event("2", [])
def done(self):
    """Sent all information about output

    This event is sent after all other properties has been
    sent after binding to the output object and after any
    other property changes done after that. This allows
    changes to the output properties to be seen as
    atomic, even if they happen via multiple events.
    """
    self._post_event(2)


@Output.event("2i", [None])
def scale(self, factor):
    """Output scaling properties

    This event contains scaling geometry information
    that is not in the geometry event. It may be sent after
    binding the output object or if the output scale changes
    later. If it is not sent, the client should assume a
    scale of 1.

    A scale larger than 1 means that the compositor will
    automatically scale surface buffers by this amount
    when rendering. This is used for very high resolution
    displays where applications rendering at the native
    resolution would be too small to be legible.

    It is intended that scaling aware clients track the
    current output of a surface, and if it is on a scaled
    output it should use :func:`Surface.set_buffer_scale() <pywayland.protocol.surface.Surface.set_buffer_scale>` with
    the scale of the output. That way the compositor can
    avoid scaling the surface, and the client can supply
    a higher detail image.

    :param factor: scaling factor of output
    :type factor: `int`
    """
    self._post_event(3, factor)


Output._gen_c()

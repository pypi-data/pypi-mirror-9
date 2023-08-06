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
from .output import Output
from .seat import Seat
from .surface import Surface

import enum
import six


@six.add_metaclass(InterfaceMeta)
class ShellSurface(Interface):
    """desktop-style metadata interface

    An interface that may be implemented by a wl_surface, for
    implementations that provide a desktop-style user interface.

    It provides requests to treat surfaces like toplevel, fullscreen
    or popup windows, move, resize or maximize them, associate
    metadata like title and class, etc.

    On the server side the object is automatically destroyed when
    the related wl_surface is destroyed.  On client side,
    wl_shell_surface_destroy() must be called before destroying
    the wl_surface object.
    """
    name = "wl_shell_surface"
    version = 1

    resize = enum.Enum("resize", {
        "none": 0,
        "top": 1,
        "bottom": 2,
        "left": 4,
        "top_left": 5,
        "bottom_left": 6,
        "right": 8,
        "top_right": 9,
        "bottom_right": 10,
    })

    transient = enum.Enum("transient", {
        "inactive": 0x1,
    })

    fullscreen_method = enum.Enum("fullscreen_method", {
        "default": 0,
        "scale": 1,
        "driver": 2,
        "fill": 3,
    })


@ShellSurface.request("u", [None])
def pong(self, serial):
    """respond to a ping event

    A client must respond to a ping event with a pong request or
    the client may be deemed unresponsive.

    :param serial: serial of the ping event
    :type serial: `uint`
    """
    self._marshal(0, serial)


@ShellSurface.request("ou", [Seat, None])
def move(self, seat, serial):
    """start an interactive move

    Start a pointer-driven move of the surface.

    This request must be used in response to a button press event.
    The server may ignore move requests depending on the state of
    the surface (e.g. fullscreen or maximized).

    :param seat: the wl_seat whose pointer is used
    :type seat: :class:`Seat`
    :param serial: serial of the implicit grab on the pointer
    :type serial: `uint`
    """
    self._marshal(1, seat, serial)


@ShellSurface.request("ouu", [Seat, None, None])
def resize(self, seat, serial, edges):
    """start an interactive resize

    Start a pointer-driven resizing of the surface.

    This request must be used in response to a button press event.
    The server may ignore resize requests depending on the state of
    the surface (e.g. fullscreen or maximized).

    :param seat: the wl_seat whose pointer is used
    :type seat: :class:`Seat`
    :param serial: serial of the implicit grab on the pointer
    :type serial: `uint`
    :param edges: which edge or corner is being dragged
    :type edges: `uint`
    """
    self._marshal(2, seat, serial, edges)


@ShellSurface.request("", [])
def set_toplevel(self):
    """make the surface a toplevel surface

    Map the surface as a toplevel surface.

    A toplevel surface is not fullscreen, maximized or transient.
    """
    self._marshal(3)


@ShellSurface.request("oiiu", [Surface, None, None, None])
def set_transient(self, parent, x, y, flags):
    """make the surface a transient surface

    Map the surface relative to an existing surface.

    The x and y arguments specify the locations of the upper left
    corner of the surface relative to the upper left corner of the
    parent surface, in surface local coordinates.

    The flags argument controls details of the transient behaviour.

    :param parent:
    :type parent: :class:`Surface`
    :param x:
    :type x: `int`
    :param y:
    :type y: `int`
    :param flags:
    :type flags: `uint`
    """
    self._marshal(4, parent, x, y, flags)


@ShellSurface.request("uu?o", [None, None, Output])
def set_fullscreen(self, method, framerate, output):
    """make the surface a fullscreen surface

    Map the surface as a fullscreen surface.

    If an output parameter is given then the surface will be made
    fullscreen on that output. If the client does not specify the
    output then the compositor will apply its policy - usually
    choosing the output on which the surface has the biggest surface
    area.

    The client may specify a method to resolve a size conflict
    between the output size and the surface size - this is provided
    through the method parameter.

    The framerate parameter is used only when the method is set
    to "driver", to indicate the preferred framerate. A value of 0
    indicates that the app does not care about framerate.  The
    framerate is specified in mHz, that is framerate of 60000 is 60Hz.

    A method of "scale" or "driver" implies a scaling operation of
    the surface, either via a direct scaling operation or a change of
    the output mode. This will override any kind of output scaling, so
    that mapping a surface with a buffer size equal to the mode can
    fill the screen independent of buffer_scale.

    A method of "fill" means we don't scale up the buffer, however
    any output scale is applied. This means that you may run into
    an edge case where the application maps a buffer with the same
    size of the output mode but buffer_scale 1 (thus making a
    surface larger than the output). In this case it is allowed to
    downscale the results to fit the screen.

    The compositor must reply to this request with a configure event
    with the dimensions for the output on which the surface will
    be made fullscreen.

    :param method:
    :type method: `uint`
    :param framerate:
    :type framerate: `uint`
    :param output:
    :type output: :class:`Output` or `None`
    """
    self._marshal(5, method, framerate, output)


@ShellSurface.request("ouoiiu", [Seat, None, Surface, None, None, None])
def set_popup(self, seat, serial, parent, x, y, flags):
    """make the surface a popup surface

    Map the surface as a popup.

    A popup surface is a transient surface with an added pointer
    grab.

    An existing implicit grab will be changed to owner-events mode,
    and the popup grab will continue after the implicit grab ends
    (i.e. releasing the mouse button does not cause the popup to
    be unmapped).

    The popup grab continues until the window is destroyed or a
    mouse button is pressed in any other clients window. A click
    in any of the clients surfaces is reported as normal, however,
    clicks in other clients surfaces will be discarded and trigger
    the callback.

    The x and y arguments specify the locations of the upper left
    corner of the surface relative to the upper left corner of the
    parent surface, in surface local coordinates.

    :param seat: the wl_seat whose pointer is used
    :type seat: :class:`Seat`
    :param serial: serial of the implicit grab on the pointer
    :type serial: `uint`
    :param parent:
    :type parent: :class:`Surface`
    :param x:
    :type x: `int`
    :param y:
    :type y: `int`
    :param flags:
    :type flags: `uint`
    """
    self._marshal(6, seat, serial, parent, x, y, flags)


@ShellSurface.request("?o", [Output])
def set_maximized(self, output):
    """make the surface a maximized surface

    Map the surface as a maximized surface.

    If an output parameter is given then the surface will be
    maximized on that output. If the client does not specify the
    output then the compositor will apply its policy - usually
    choosing the output on which the surface has the biggest surface
    area.

    The compositor will reply with a configure event telling
    the expected new surface size. The operation is completed
    on the next buffer attach to this surface.

    A maximized surface typically fills the entire output it is
    bound to, except for desktop element such as panels. This is
    the main difference between a maximized shell surface and a
    fullscreen shell surface.

    The details depend on the compositor implementation.

    :param output:
    :type output: :class:`Output` or `None`
    """
    self._marshal(7, output)


@ShellSurface.request("s", [None])
def set_title(self, title):
    """set surface title

    Set a short title for the surface.

    This string may be used to identify the surface in a task bar,
    window list, or other user interface elements provided by the
    compositor.

    The string must be encoded in UTF-8.

    :param title:
    :type title: `string`
    """
    self._marshal(8, title)


@ShellSurface.request("s", [None])
def set_class(self, class_):
    """set surface class

    Set a class for the surface.

    The surface class identifies the general class of applications
    to which the surface belongs. A common convention is to use the
    file name (or the full path if it is a non-standard location) of
    the application's .desktop file as the class.

    :param class_:
    :type class_: `string`
    """
    self._marshal(9, class_)


@ShellSurface.event("u", [None])
def ping(self, serial):
    """ping client

    Ping a client to check if it is receiving events and sending
    requests. A client is expected to reply with a pong request.

    :param serial:
    :type serial: `uint`
    """
    self._post_event(0, serial)


@ShellSurface.event("uii", [None, None, None])
def configure(self, edges, width, height):
    """suggest resize

    The configure event asks the client to resize its surface.

    The size is a hint, in the sense that the client is free to
    ignore it if it doesn't resize, pick a smaller size (to
    satisfy aspect ratio or resize in steps of NxM pixels).

    The edges parameter provides a hint about how the surface
    was resized. The client may use this information to decide
    how to adjust its content to the new size (e.g. a scrolling
    area might adjust its content position to leave the viewable
    content unmoved).

    The client is free to dismiss all but the last configure
    event it received.

    The width and height arguments specify the size of the window
    in surface local coordinates.

    :param edges:
    :type edges: `uint`
    :param width:
    :type width: `int`
    :param height:
    :type height: `int`
    """
    self._post_event(1, edges, width, height)


@ShellSurface.event("", [])
def popup_done(self):
    """popup interaction is done

    The popup_done event is sent out when a popup grab is broken,
    that is, when the user clicks a surface that doesn't belong
    to the client owning the popup surface.
    """
    self._post_event(2)


ShellSurface._gen_c()

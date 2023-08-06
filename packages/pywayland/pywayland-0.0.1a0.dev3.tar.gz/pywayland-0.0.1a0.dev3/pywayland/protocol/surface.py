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
from .buffer import Buffer
from .callback import Callback
from .output import Output
from .region import Region

import enum
import six


@six.add_metaclass(InterfaceMeta)
class Surface(Interface):
    """An onscreen surface

    A surface is a rectangular area that is displayed on the screen.
    It has a location, size and pixel contents.

    The size of a surface (and relative positions on it) is described
    in surface local coordinates, which may differ from the buffer
    local coordinates of the pixel content, in case a buffer_transform
    or a buffer_scale is used.

    A surface without a "role" is fairly useless, a compositor does
    not know where, when or how to present it. The role is the
    purpose of a :class:`Surface`. Examples of roles are a cursor for a
    pointer (as set by :func:`Pointer.set_cursor() <pywayland.protocol.pointer.Pointer.set_cursor>`), a drag icon
    (:func:`DataDevice.start_drag() <pywayland.protocol.datadevice.DataDevice.start_drag>`), a sub-surface
    (:func:`Subcompositor.get_subsurface() <pywayland.protocol.subcompositor.Subcompositor.get_subsurface>`), and a window as defined by a
    shell protocol (e.g. :func:`Shell.get_shell_surface() <pywayland.protocol.shell.Shell.get_shell_surface>`).

    A surface can have only one role at a time. Initially a
    :class:`Surface` does not have a role. Once a :class:`Surface` is given a
    role, it is set permanently for the whole lifetime of the
    :class:`Surface` object. Giving the current role again is allowed,
    unless explicitly forbidden by the relevant interface
    specification.

    Surface roles are given by requests in other interfaces such as
    :func:`Pointer.set_cursor() <pywayland.protocol.pointer.Pointer.set_cursor>`. The request should explicitly mention
    that this request gives a role to a :class:`Surface`. Often, this
    request also creates a new protocol object that represents the
    role and adds additional functionality to :class:`Surface`. When a
    client wants to destroy a :class:`Surface`, they must destroy this 'role
    object' before the :class:`Surface`.

    Destroying the role object does not remove the role from the
    :class:`Surface`, but it may stop the :class:`Surface` from "playing the role".
    For instance, if a :class:`~pywayland.protocol.subsurface.Subsurface` object is destroyed, the :class:`Surface`
    it was created for will be unmapped and forget its position and
    z-order. It is allowed to create a :class:`~pywayland.protocol.subsurface.Subsurface` for the same
    :class:`Surface` again, but it is not allowed to use the :class:`Surface` as
    a cursor (cursor is a different role than sub-surface, and role
    switching is not allowed).
    """
    name = "wl_surface"
    version = 3

    error = enum.Enum("error", {
        "invalid_scale": 0,
        "invalid_transform": 1,
    })


@Surface.request("", [])
def destroy(self):
    """Delete surface

    Deletes the surface and invalidates its object ID.
    """
    self._marshal(0)
    self._destroy()


@Surface.request("?oii", [Buffer, None, None])
def attach(self, buffer, x, y):
    """Set the surface contents

    Set a buffer as the content of this surface.

    The new size of the surface is calculated based on the buffer
    size transformed by the inverse buffer_transform and the
    inverse buffer_scale. This means that the supplied buffer
    must be an integer multiple of the buffer_scale.

    The x and y arguments specify the location of the new pending
    buffer's upper left corner, relative to the current buffer's upper
    left corner, in surface local coordinates. In other words, the
    x and y, combined with the new surface size define in which
    directions the surface's size changes.

    Surface contents are double-buffered state, see :func:`Surface.commit`.

    The initial surface contents are void; there is no content.
    :func:`Surface.attach` assigns the given :class:`~pywayland.protocol.buffer.Buffer` as the pending
    :class:`~pywayland.protocol.buffer.Buffer`. :func:`Surface.commit` makes the pending :class:`~pywayland.protocol.buffer.Buffer` the new
    surface contents, and the size of the surface becomes the size
    calculated from the :class:`~pywayland.protocol.buffer.Buffer`, as described above. After commit,
    there is no pending buffer until the next attach.

    Committing a pending :class:`~pywayland.protocol.buffer.Buffer` allows the compositor to read the
    pixels in the :class:`~pywayland.protocol.buffer.Buffer`. The compositor may access the pixels at
    any time after the :func:`Surface.commit` request. When the compositor
    will not access the pixels anymore, it will send the
    :func:`Buffer.release() <pywayland.protocol.buffer.Buffer.release>` event. Only after receiving :func:`Buffer.release() <pywayland.protocol.buffer.Buffer.release>`,
    the client may re-use the :class:`~pywayland.protocol.buffer.Buffer`. A :class:`~pywayland.protocol.buffer.Buffer` that has been
    attached and then replaced by another attach instead of committed
    will not receive a release event, and is not used by the
    compositor.

    Destroying the :class:`~pywayland.protocol.buffer.Buffer` after :func:`Buffer.release() <pywayland.protocol.buffer.Buffer.release>` does not change
    the surface contents. However, if the client destroys the
    :class:`~pywayland.protocol.buffer.Buffer` before receiving the :func:`Buffer.release() <pywayland.protocol.buffer.Buffer.release>` event, the surface
    contents become undefined immediately.

    If :func:`Surface.attach` is sent with a NULL :class:`~pywayland.protocol.buffer.Buffer`, the
    following :func:`Surface.commit` will remove the surface content.

    :param buffer:
    :type buffer: :class:`~pywayland.protocol.buffer.Buffer` or `None`
    :param x:
    :type x: `int`
    :param y:
    :type y: `int`
    """
    self._marshal(1, buffer, x, y)


@Surface.request("iiii", [None, None, None, None])
def damage(self, x, y, width, height):
    """Mark part of the surface damaged

    This request is used to describe the regions where the pending
    buffer is different from the current surface contents, and where
    the surface therefore needs to be repainted. The pending buffer
    must be set by :func:`Surface.attach` before sending damage. The
    compositor ignores the parts of the damage that fall outside of
    the surface.

    Damage is double-buffered state, see :func:`Surface.commit`.

    The damage rectangle is specified in surface local coordinates.

    The initial value for pending damage is empty: no damage.
    :func:`Surface.damage` adds pending damage: the new pending damage
    is the union of old pending damage and the given rectangle.

    :func:`Surface.commit` assigns pending damage as the current damage,
    and clears pending damage. The server will clear the current
    damage as it repaints the surface.

    :param x:
    :type x: `int`
    :param y:
    :type y: `int`
    :param width:
    :type width: `int`
    :param height:
    :type height: `int`
    """
    self._marshal(2, x, y, width, height)


@Surface.request("n", [Callback])
def frame(self):
    """Request a frame throttling hint

    Request a notification when it is a good time start drawing a new
    frame, by creating a frame callback. This is useful for throttling
    redrawing operations, and driving animations.

    When a client is animating on a :class:`Surface`, it can use the 'frame'
    request to get notified when it is a good time to draw and commit the
    next frame of animation. If the client commits an update earlier than
    that, it is likely that some updates will not make it to the display,
    and the client is wasting resources by drawing too often.

    The frame request will take effect on the next :func:`Surface.commit`.
    The notification will only be posted for one frame unless
    requested again. For a :class:`Surface`, the notifications are posted in
    the order the frame requests were committed.

    The server must send the notifications so that a client
    will not send excessive updates, while still allowing
    the highest possible update rate for clients that wait for the reply
    before drawing again. The server should give some time for the client
    to draw and commit after sending the frame callback events to let them
    hit the next output refresh.

    A server should avoid signalling the frame callbacks if the
    surface is not visible in any way, e.g. the surface is off-screen,
    or completely obscured by other opaque surfaces.

    The object returned by this request will be destroyed by the
    compositor after the callback is fired and as such the client must not
    attempt to use it after that point.

    The callback_data passed in the callback is the current time, in
    milliseconds, with an undefined base.

    :returns: :class:`~pywayland.protocol.callback.Callback`
    """
    callback = self._marshal_constructor(3, Callback)
    return callback


@Surface.request("?o", [Region])
def set_opaque_region(self, region):
    """Set opaque region

    This request sets the region of the surface that contains
    opaque content.

    The opaque region is an optimization hint for the compositor
    that lets it optimize out redrawing of content behind opaque
    regions.  Setting an opaque region is not required for correct
    behaviour, but marking transparent content as opaque will result
    in repaint artifacts.

    The opaque region is specified in surface local coordinates.

    The compositor ignores the parts of the opaque region that fall
    outside of the surface.

    Opaque region is double-buffered state, see :func:`Surface.commit`.

    :func:`Surface.set_opaque_region` changes the pending opaque region.
    :func:`Surface.commit` copies the pending region to the current region.
    Otherwise, the pending and current regions are never changed.

    The initial value for opaque region is empty. Setting the pending
    opaque region has copy semantics, and the :class:`~pywayland.protocol.region.Region` object can be
    destroyed immediately. A NULL :class:`~pywayland.protocol.region.Region` causes the pending opaque
    region to be set to empty.

    :param region:
    :type region: :class:`~pywayland.protocol.region.Region` or `None`
    """
    self._marshal(4, region)


@Surface.request("?o", [Region])
def set_input_region(self, region):
    """Set input region

    This request sets the region of the surface that can receive
    pointer and touch events.

    Input events happening outside of this region will try the next
    surface in the server surface stack. The compositor ignores the
    parts of the input region that fall outside of the surface.

    The input region is specified in surface local coordinates.

    Input region is double-buffered state, see :func:`Surface.commit`.

    :func:`Surface.set_input_region` changes the pending input region.
    :func:`Surface.commit` copies the pending region to the current region.
    Otherwise the pending and current regions are never changed,
    except cursor and icon surfaces are special cases, see
    :func:`Pointer.set_cursor() <pywayland.protocol.pointer.Pointer.set_cursor>` and :func:`DataDevice.start_drag() <pywayland.protocol.datadevice.DataDevice.start_drag>`.

    The initial value for input region is infinite. That means the
    whole surface will accept input. Setting the pending input region
    has copy semantics, and the :class:`~pywayland.protocol.region.Region` object can be destroyed
    immediately. A NULL :class:`~pywayland.protocol.region.Region` causes the input region to be set
    to infinite.

    :param region:
    :type region: :class:`~pywayland.protocol.region.Region` or `None`
    """
    self._marshal(5, region)


@Surface.request("", [])
def commit(self):
    """Commit pending surface state

    Surface state (input, opaque, and damage regions, attached buffers,
    etc.) is double-buffered. Protocol requests modify the pending
    state, as opposed to current state in use by the compositor. Commit
    request atomically applies all pending state, replacing the current
    state. After commit, the new pending state is as documented for each
    related request.

    On commit, a pending :class:`~pywayland.protocol.buffer.Buffer` is applied first, all other state
    second. This means that all coordinates in double-buffered state are
    relative to the new :class:`~pywayland.protocol.buffer.Buffer` coming into use, except for
    :func:`Surface.attach` itself. If there is no pending :class:`~pywayland.protocol.buffer.Buffer`, the
    coordinates are relative to the current surface contents.

    All requests that need a commit to become effective are documented
    to affect double-buffered state.

    Other interfaces may add further double-buffered surface state.
    """
    self._marshal(6)


@Surface.request("2i", [None])
def set_buffer_transform(self, transform):
    """Sets the buffer transformation

    This request sets an optional transformation on how the compositor
    interprets the contents of the buffer attached to the surface. The
    accepted values for the transform parameter are the values for
    :func:`Output.transform() <pywayland.protocol.output.Output.transform>`.

    Buffer transform is double-buffered state, see :func:`Surface.commit`.

    A newly created surface has its buffer transformation set to normal.

    :func:`Surface.set_buffer_transform` changes the pending buffer
    transformation. :func:`Surface.commit` copies the pending buffer
    transformation to the current one. Otherwise, the pending and current
    values are never changed.

    The purpose of this request is to allow clients to render content
    according to the output transform, thus permiting the compositor to
    use certain optimizations even if the display is rotated. Using
    hardware overlays and scanning out a client buffer for fullscreen
    surfaces are examples of such optimizations. Those optimizations are
    highly dependent on the compositor implementation, so the use of this
    request should be considered on a case-by-case basis.

    Note that if the transform value includes 90 or 270 degree rotation,
    the width of the buffer will become the surface height and the height
    of the buffer will become the surface width.

    If transform is not one of the values from the
    :func:`Output.transform() <pywayland.protocol.output.Output.transform>` enum the invalid_transform protocol error
    is raised.

    :param transform:
    :type transform: `int`
    """
    self._marshal(7, transform)


@Surface.request("3i", [None])
def set_buffer_scale(self, scale):
    """Sets the buffer scaling factor

    This request sets an optional scaling factor on how the compositor
    interprets the contents of the buffer attached to the window.

    Buffer scale is double-buffered state, see :func:`Surface.commit`.

    A newly created surface has its buffer scale set to 1.

    :func:`Surface.set_buffer_scale` changes the pending buffer scale.
    :func:`Surface.commit` copies the pending buffer scale to the current one.
    Otherwise, the pending and current values are never changed.

    The purpose of this request is to allow clients to supply higher
    resolution buffer data for use on high resolution outputs. Its
    intended that you pick the same	buffer scale as the scale of the
    output that the surface is displayed on.This means the compositor
    can avoid scaling when rendering the surface on that output.

    Note that if the scale is larger than 1, then you have to attach
    a buffer that is larger (by a factor of scale in each dimension)
    than the desired surface size.

    If scale is not positive the invalid_scale protocol error is
    raised.

    :param scale:
    :type scale: `int`
    """
    self._marshal(8, scale)


@Surface.event("o", [Output])
def enter(self, output):
    """Surface enters an output

    This is emitted whenever a surface's creation, movement, or resizing
    results in some part of it being within the scanout region of an
    output.

    Note that a surface may be overlapping with zero or more outputs.

    :param output:
    :type output: :class:`~pywayland.protocol.output.Output`
    """
    self._post_event(0, output)


@Surface.event("o", [Output])
def leave(self, output):
    """Surface leaves an output

    This is emitted whenever a surface's creation, movement, or resizing
    results in it no longer having any part of it within the scanout region
    of an output.

    :param output:
    :type output: :class:`~pywayland.protocol.output.Output`
    """
    self._post_event(1, output)


Surface._gen_c()

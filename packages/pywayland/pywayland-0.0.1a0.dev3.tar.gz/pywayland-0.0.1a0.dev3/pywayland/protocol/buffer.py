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

import six


@six.add_metaclass(InterfaceMeta)
class Buffer(Interface):
    """Content for a :class:`~pywayland.protocol.surface.Surface`

    A buffer provides the content for a :class:`~pywayland.protocol.surface.Surface`. Buffers are
    created through factory interfaces such as :class:`~pywayland.protocol.drm.Drm`, :class:`~pywayland.protocol.shm.Shm` or
    similar. It has a width and a height and can be attached to a
    :class:`~pywayland.protocol.surface.Surface`, but the mechanism by which a client provides and
    updates the contents is defined by the buffer factory interface.
    """
    name = "wl_buffer"
    version = 1


@Buffer.request("", [])
def destroy(self):
    """Destroy a buffer

    Destroy a buffer. If and how you need to release the backing
    storage is defined by the buffer factory interface.

    For possible side-effects to a surface, see :func:`Surface.attach() <pywayland.protocol.surface.Surface.attach>`.
    """
    self._marshal(0)
    self._destroy()


@Buffer.event("", [])
def release(self):
    """Compositor releases buffer

    Sent when this :class:`Buffer` is no longer used by the compositor.
    The client is now free to re-use or destroy this buffer and its
    backing storage.

    If a client receives a release event before the frame callback
    requested in the same :func:`Surface.commit() <pywayland.protocol.surface.Surface.commit>` that attaches this
    :class:`Buffer` to a surface, then the client is immediately free to
    re-use the buffer and its backing storage, and does not need a
    second buffer for the next surface content update. Typically
    this is possible, when the compositor maintains a copy of the
    :class:`~pywayland.protocol.surface.Surface` contents, e.g. as a GL texture. This is an important
    optimization for GL(ES) compositors with :class:`~pywayland.protocol.shm.Shm` clients.
    """
    self._post_event(0)


Buffer._gen_c()

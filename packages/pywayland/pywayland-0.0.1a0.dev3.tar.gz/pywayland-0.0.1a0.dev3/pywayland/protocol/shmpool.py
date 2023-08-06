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

import six


@six.add_metaclass(InterfaceMeta)
class ShmPool(Interface):
    """A shared memory pool

    The :class:`ShmPool` object encapsulates a piece of memory shared
    between the compositor and client.  Through the :class:`ShmPool`
    object, the client can allocate shared memory :class:`~pywayland.protocol.buffer.Buffer` objects.
    All objects created through the same pool share the same
    underlying mapped memory. Reusing the mapped memory avoids the
    setup/teardown overhead and is useful when interactively resizing
    a surface or for many small buffers.
    """
    name = "wl_shm_pool"
    version = 1


@ShmPool.request("niiiiu", [Buffer, None, None, None, None, None])
def create_buffer(self, offset, width, height, stride, format):
    """Create a buffer from the pool

    Create a :class:`~pywayland.protocol.buffer.Buffer` object from the pool.

    The buffer is created offset bytes into the pool and has
    width and height as specified.  The stride arguments specifies
    the number of bytes from beginning of one row to the beginning
    of the next.  The format is the pixel format of the buffer and
    must be one of those advertised through the :func:`Shm.format() <pywayland.protocol.shm.Shm.format>` event.

    A buffer will keep a reference to the pool it was created from
    so it is valid to destroy the pool immediately after creating
    a buffer from it.

    :param offset:
    :type offset: `int`
    :param width:
    :type width: `int`
    :param height:
    :type height: `int`
    :param stride:
    :type stride: `int`
    :param format:
    :type format: `uint`
    :returns: :class:`~pywayland.protocol.buffer.Buffer`
    """
    id = self._marshal_constructor(0, Buffer, offset, width, height, stride, format)
    return id


@ShmPool.request("", [])
def destroy(self):
    """Destroy the pool

    Destroy the shared memory pool.

    The mmapped memory will be released when all
    buffers that have been created from this pool
    are gone.
    """
    self._marshal(1)
    self._destroy()


@ShmPool.request("i", [None])
def resize(self, size):
    """Change the size of the pool mapping

    This request will cause the server to remap the backing memory
    for the pool from the file descriptor passed when the pool was
    created, but using the new size.  This request can only be
    used to make the pool bigger.

    :param size:
    :type size: `int`
    """
    self._marshal(2, size)


ShmPool._gen_c()

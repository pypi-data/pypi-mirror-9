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
from .shmpool import ShmPool

import enum
import six


@six.add_metaclass(InterfaceMeta)
class Shm(Interface):
    """shared memory support

    A global singleton object that provides support for shared
    memory.

    Clients can create wl_shm_pool objects using the create_pool
    request.

    At connection setup time, the wl_shm object emits one or more
    format events to inform clients about the valid pixel formats
    that can be used for buffers.
    """
    name = "wl_shm"
    version = 1

    error = enum.Enum("error", {
        "invalid_format": 0,
        "invalid_stride": 1,
        "invalid_fd": 2,
    })

    format = enum.Enum("format", {
        "argb8888": 0,
        "xrgb8888": 1,
        "c8": 0x20203843,
        "rgb332": 0x38424752,
        "bgr233": 0x38524742,
        "xrgb4444": 0x32315258,
        "xbgr4444": 0x32314258,
        "rgbx4444": 0x32315852,
        "bgrx4444": 0x32315842,
        "argb4444": 0x32315241,
        "abgr4444": 0x32314241,
        "rgba4444": 0x32314152,
        "bgra4444": 0x32314142,
        "xrgb1555": 0x35315258,
        "xbgr1555": 0x35314258,
        "rgbx5551": 0x35315852,
        "bgrx5551": 0x35315842,
        "argb1555": 0x35315241,
        "abgr1555": 0x35314241,
        "rgba5551": 0x35314152,
        "bgra5551": 0x35314142,
        "rgb565": 0x36314752,
        "bgr565": 0x36314742,
        "rgb888": 0x34324752,
        "bgr888": 0x34324742,
        "xbgr8888": 0x34324258,
        "rgbx8888": 0x34325852,
        "bgrx8888": 0x34325842,
        "abgr8888": 0x34324241,
        "rgba8888": 0x34324152,
        "bgra8888": 0x34324142,
        "xrgb2101010": 0x30335258,
        "xbgr2101010": 0x30334258,
        "rgbx1010102": 0x30335852,
        "bgrx1010102": 0x30335842,
        "argb2101010": 0x30335241,
        "abgr2101010": 0x30334241,
        "rgba1010102": 0x30334152,
        "bgra1010102": 0x30334142,
        "yuyv": 0x56595559,
        "yvyu": 0x55595659,
        "uyvy": 0x59565955,
        "vyuy": 0x59555956,
        "ayuv": 0x56555941,
        "nv12": 0x3231564e,
        "nv21": 0x3132564e,
        "nv16": 0x3631564e,
        "nv61": 0x3136564e,
        "yuv410": 0x39565559,
        "yvu410": 0x39555659,
        "yuv411": 0x31315559,
        "yvu411": 0x31315659,
        "yuv420": 0x32315559,
        "yvu420": 0x32315659,
        "yuv422": 0x36315559,
        "yvu422": 0x36315659,
        "yuv444": 0x34325559,
        "yvu444": 0x34325659,
    })


@Shm.request("nhi", [ShmPool, None, None])
def create_pool(self, fd, size):
    """create a shm pool

    Create a new wl_shm_pool object.

    The pool can be used to create shared memory based buffer
    objects.  The server will mmap size bytes of the passed file
    descriptor, to use as backing memory for the pool.

    :param fd:
    :type fd: `fd`
    :param size:
    :type size: `int`
    :returns: :class:`ShmPool`
    """
    id = self._marshal_constructor(0, ShmPool, fd, size)
    return id


@Shm.event("u", [None])
def format(self, format):
    """pixel format description

    Informs the client about a valid pixel format that
    can be used for buffers. Known formats include
    argb8888 and xrgb8888.

    :param format:
    :type format: `uint`
    """
    self._post_event(0, format)


Shm._gen_c()

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
class Region(Interface):
    """Region interface

    A region object describes an area.

    Region objects are used to describe the opaque and input
    regions of a surface.
    """
    name = "wl_region"
    version = 1


@Region.request("", [])
def destroy(self):
    """Destroy region

    Destroy the region.  This will invalidate the object ID.
    """
    self._marshal(0)
    self._destroy()


@Region.request("iiii", [None, None, None, None])
def add(self, x, y, width, height):
    """Add rectangle to region

    Add the specified rectangle to the region.

    :param x:
    :type x: `int`
    :param y:
    :type y: `int`
    :param width:
    :type width: `int`
    :param height:
    :type height: `int`
    """
    self._marshal(1, x, y, width, height)


@Region.request("iiii", [None, None, None, None])
def subtract(self, x, y, width, height):
    """Subtract rectangle from region

    Subtract the specified rectangle from the region.

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


Region._gen_c()

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
from .region import Region
from .surface import Surface

import six


@six.add_metaclass(InterfaceMeta)
class Compositor(Interface):
    """the compositor singleton

    A compositor.  This object is a singleton global.  The
    compositor is in charge of combining the contents of multiple
    surfaces into one displayable output.
    """
    name = "wl_compositor"
    version = 3


@Compositor.request("n", [Surface])
def create_surface(self):
    """create new surface

    Ask the compositor to create a new surface.

    :returns: :class:`Surface`
    """
    id = self._marshal_constructor(0, Surface)
    return id


@Compositor.request("n", [Region])
def create_region(self):
    """create new region

    Ask the compositor to create a new region.

    :returns: :class:`Region`
    """
    id = self._marshal_constructor(1, Region)
    return id


Compositor._gen_c()

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
from .shellsurface import ShellSurface
from .surface import Surface

import enum
import six


@six.add_metaclass(InterfaceMeta)
class Shell(Interface):
    """create desktop-style surfaces

    This interface is implemented by servers that provide
    desktop-style user interfaces.

    It allows clients to associate a wl_shell_surface with
    a basic surface.
    """
    name = "wl_shell"
    version = 1

    error = enum.Enum("error", {
        "role": 0,
    })


@Shell.request("no", [ShellSurface, Surface])
def get_shell_surface(self, surface):
    """create a shell surface from a surface

    Create a shell surface for an existing surface. This gives
    the wl_surface the role of a shell surface. If the wl_surface
    already has another role, it raises a protocol error.

    Only one shell surface can be associated with a given surface.

    :param surface:
    :type surface: :class:`Surface`
    :returns: :class:`ShellSurface`
    """
    id = self._marshal_constructor(0, ShellSurface, surface)
    return id


Shell._gen_c()

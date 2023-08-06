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
from .subsurface import Subsurface
from .surface import Surface

import enum
import six


@six.add_metaclass(InterfaceMeta)
class Subcompositor(Interface):
    """Sub-surface compositing

    The global interface exposing sub-surface compositing capabilities.
    A :class:`~pywayland.protocol.surface.Surface`, that has sub-surfaces associated, is called the
    parent surface. Sub-surfaces can be arbitrarily nested and create
    a tree of sub-surfaces.

    The root surface in a tree of sub-surfaces is the main
    surface. The main surface cannot be a sub-surface, because
    sub-surfaces must always have a parent.

    A main surface with its sub-surfaces forms a (compound) window.
    For window management purposes, this set of :class:`~pywayland.protocol.surface.Surface` objects is
    to be considered as a single window, and it should also behave as
    such.

    The aim of sub-surfaces is to offload some of the compositing work
    within a window from clients to the compositor. A prime example is
    a video player with decorations and video in separate :class:`~pywayland.protocol.surface.Surface`
    objects. This should allow the compositor to pass YUV video buffer
    processing to dedicated overlay hardware when possible.
    """
    name = "wl_subcompositor"
    version = 1

    error = enum.Enum("error", {
        "bad_surface": 0,
    })


@Subcompositor.request("", [])
def destroy(self):
    """Unbind from the subcompositor interface

    Informs the server that the client will not be using this
    protocol object anymore. This does not affect any other
    objects, :class:`~pywayland.protocol.subsurface.Subsurface` objects included.
    """
    self._marshal(0)
    self._destroy()


@Subcompositor.request("noo", [Subsurface, Surface, Surface])
def get_subsurface(self, surface, parent):
    """Give a surface the role sub-surface

    Create a sub-surface interface for the given surface, and
    associate it with the given parent surface. This turns a
    plain :class:`~pywayland.protocol.surface.Surface` into a sub-surface.

    The to-be sub-surface must not already have another role, and it
    must not have an existing :class:`~pywayland.protocol.subsurface.Subsurface` object. Otherwise a protocol
    error is raised.

    :param surface: the surface to be turned into a sub-surface
    :type surface: :class:`~pywayland.protocol.surface.Surface`
    :param parent: the parent surface
    :type parent: :class:`~pywayland.protocol.surface.Surface`
    :returns: :class:`~pywayland.protocol.subsurface.Subsurface` -- the new subsurface object id
    """
    id = self._marshal_constructor(1, Subsurface, surface, parent)
    return id


Subcompositor._gen_c()

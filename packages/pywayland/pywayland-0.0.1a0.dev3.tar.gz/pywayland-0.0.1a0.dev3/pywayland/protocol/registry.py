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
class Registry(Interface):
    """Global registry object

    The global registry object.  The server has a number of global
    objects that are available to all clients.  These objects
    typically represent an actual object in the server (for example,
    an input device) or they are singleton objects that provide
    extension functionality.

    When a client creates a registry object, the registry object
    will emit a global event for each global currently in the
    registry.  Globals come and go as a result of device or
    monitor hotplugs, reconfiguration or other events, and the
    registry will send out global and global_remove events to
    keep the client up to date with the changes.  To mark the end
    of the initial burst of events, the client can use the
    :func:`Display.sync() <pywayland.protocol.display.Display.sync>` request immediately after calling
    :func:`Display.get_registry() <pywayland.protocol.display.Display.get_registry>`.

    A client can bind to a global object by using the bind
    request.  This creates a client-side handle that lets the object
    emit events to the client and lets the client invoke requests on
    the object.
    """
    name = "wl_registry"
    version = 1


@Registry.request("usun", [None, None, None, None])
def bind(self, name, interface, version):
    """Bind an object to the display

    Binds a new, client-created object to the server using the
    specified name as the identifier.

    :param name: unique name for the object
    :type name: `uint`
    :param interface: Interface name
    :type interface: `string`
    :param version: Interface version
    :type version: `int`
    :returns: :class:`pywayland.client.proxy.Proxy` of specified Interface
    """
    id = self._marshal_constructor(0, interface, name, interface.name, version)
    return id


@Registry.event("usu", [None, None, None])
def global_(self, name, interface, version):
    """Announce global object

    Notify the client of global objects.

    The event notifies the client that a global object with
    the given name is now available, and it implements the
    given version of the given interface.

    :param name:
    :type name: `uint`
    :param interface:
    :type interface: `string`
    :param version:
    :type version: `uint`
    """
    self._post_event(0, name, interface, version)


@Registry.event("u", [None])
def global_remove(self, name):
    """Announce removal of global object

    Notify the client of removed global objects.

    This event notifies the client that the global identified
    by name is no longer available.  If the client bound to
    the global using the bind request, the client should now
    destroy that object.

    The object remains valid and requests to the object will be
    ignored until the client destroys it, to avoid races between
    the global going away and a client sending a request to it.

    :param name:
    :type name: `uint`
    """
    self._post_event(1, name)


Registry._gen_c()

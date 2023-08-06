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
from .callback import Callback
from .registry import Registry

import enum
import six


@six.add_metaclass(InterfaceMeta)
class Display(Interface):
    """Core global object

    The core global object.  This is a special singleton object.  It
    is used for internal Wayland protocol features.
    """
    name = "wl_display"
    version = 1

    error = enum.Enum("error", {
        "invalid_object": 0,
        "invalid_method": 1,
        "no_memory": 2,
    })


@Display.request("n", [Callback])
def sync(self):
    """Asynchronous roundtrip

    The sync request asks the server to emit the 'done' event
    on the returned :class:`~pywayland.protocol.callback.Callback` object.  Since requests are
    handled in-order and events are delivered in-order, this can
    be used as a barrier to ensure all previous requests and the
    resulting events have been handled.

    The object returned by this request will be destroyed by the
    compositor after the callback is fired and as such the client must not
    attempt to use it after that point.

    The callback_data passed in the callback is the event serial.

    :returns: :class:`~pywayland.protocol.callback.Callback`
    """
    callback = self._marshal_constructor(0, Callback)
    return callback


@Display.request("n", [Registry])
def get_registry(self):
    """Get global registry object

    This request creates a registry object that allows the client
    to list and bind the global objects available from the
    compositor.

    :returns: :class:`~pywayland.protocol.registry.Registry`
    """
    registry = self._marshal_constructor(1, Registry)
    return registry


@Display.event("ous", [None, None, None])
def error(self, object_id, code, message):
    """Fatal error event

    The error event is sent out when a fatal (non-recoverable)
    error has occurred.  The object_id argument is the object
    where the error occurred, most often in response to a request
    to that object.  The code identifies the error and is defined
    by the object interface.  As such, each interface defines its
    own set of error codes.  The message is an brief description
    of the error, for (debugging) convenience.

    :param object_id:
    :type object_id: `object`
    :param code:
    :type code: `uint`
    :param message:
    :type message: `string`
    """
    self._post_event(0, object_id, code, message)


@Display.event("u", [None])
def delete_id(self, id):
    """Acknowledge object id deletion

    This event is used internally by the object ID management
    logic.  When a client deletes an object, the server will send
    this event to acknowledge that it has seen the delete request.
    When the client receive this event, it will know that it can
    safely reuse the object ID.

    :param id:
    :type id: `uint`
    """
    self._post_event(1, id)


Display._gen_c()

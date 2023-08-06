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
class Callback(Interface):
    """callback object

    Clients can handle the 'done' event to get notified when
    the related request is done.
    """
    name = "wl_callback"
    version = 1


@Callback.event("u", [None])
def done(self, callback_data):
    """done event

    Notify the client when the related request is done.

    :param callback_data: request-specific data for the wl_callback
    :type callback_data: `uint`
    """
    self._post_event(0, callback_data)


Callback._gen_c()

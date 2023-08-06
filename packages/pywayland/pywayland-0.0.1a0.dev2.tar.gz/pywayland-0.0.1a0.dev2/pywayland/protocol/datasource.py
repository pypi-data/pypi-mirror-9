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
class DataSource(Interface):
    """offer to transfer data

    The wl_data_source object is the source side of a wl_data_offer.
    It is created by the source client in a data transfer and
    provides a way to describe the offered data and a way to respond
    to requests to transfer the data.
    """
    name = "wl_data_source"
    version = 1


@DataSource.request("s", [None])
def offer(self, mime_type):
    """add an offered mime type

    This request adds a mime type to the set of mime types
    advertised to targets.  Can be called several times to offer
    multiple types.

    :param mime_type:
    :type mime_type: `string`
    """
    self._marshal(0, mime_type)


@DataSource.request("", [])
def destroy(self):
    """destroy the data source

    Destroy the data source.
    """
    self._marshal(1)
    self._destroy()


@DataSource.event("?s", [None])
def target(self, mime_type):
    """a target accepts an offered mime type

    Sent when a target accepts pointer_focus or motion events.  If
    a target does not accept any of the offered types, type is NULL.

    Used for feedback during drag-and-drop.

    :param mime_type:
    :type mime_type: `string` or `None`
    """
    self._post_event(0, mime_type)


@DataSource.event("sh", [None, None])
def send(self, mime_type, fd):
    """send the data

    Request for data from the client.  Send the data as the
    specified mime type over the passed file descriptor, then
    close it.

    :param mime_type:
    :type mime_type: `string`
    :param fd:
    :type fd: `fd`
    """
    self._post_event(1, mime_type, fd)


@DataSource.event("", [])
def cancelled(self):
    """selection was cancelled

    This data source has been replaced by another data source.
    The client should clean up and destroy this data source.
    """
    self._post_event(2)


DataSource._gen_c()

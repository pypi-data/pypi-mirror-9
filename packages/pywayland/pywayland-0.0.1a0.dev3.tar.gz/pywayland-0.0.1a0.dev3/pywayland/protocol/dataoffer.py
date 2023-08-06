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
class DataOffer(Interface):
    """Offer to transfer data

    A :class:`DataOffer` represents a piece of data offered for transfer
    by another client (the source client).  It is used by the
    copy-and-paste and drag-and-drop mechanisms.  The offer
    describes the different mime types that the data can be
    converted to and provides the mechanism for transferring the
    data directly from the source client.
    """
    name = "wl_data_offer"
    version = 1


@DataOffer.request("u?s", [None, None])
def accept(self, serial, mime_type):
    """Accept one of the offered mime types

    Indicate that the client can accept the given mime type, or
    NULL for not accepted.

    Used for feedback during drag-and-drop.

    :param serial:
    :type serial: `uint`
    :param mime_type:
    :type mime_type: `string` or `None`
    """
    self._marshal(0, serial, mime_type)


@DataOffer.request("sh", [None, None])
def receive(self, mime_type, fd):
    """Request that the data is transferred

    To transfer the offered data, the client issues this request
    and indicates the mime type it wants to receive.  The transfer
    happens through the passed file descriptor (typically created
    with the pipe system call).  The source client writes the data
    in the mime type representation requested and then closes the
    file descriptor.

    The receiving client reads from the read end of the pipe until
    EOF and then closes its end, at which point the transfer is
    complete.

    :param mime_type:
    :type mime_type: `string`
    :param fd:
    :type fd: `fd`
    """
    self._marshal(1, mime_type, fd)


@DataOffer.request("", [])
def destroy(self):
    """Destroy data offer

    Destroy the data offer.
    """
    self._marshal(2)
    self._destroy()


@DataOffer.event("s", [None])
def offer(self, mime_type):
    """Advertise offered mime type

    Sent immediately after creating the :class:`DataOffer` object.  One
    event per offered mime type.

    :param mime_type:
    :type mime_type: `string`
    """
    self._post_event(0, mime_type)


DataOffer._gen_c()

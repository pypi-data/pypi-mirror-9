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
from .datadevice import DataDevice
from .datasource import DataSource
from .seat import Seat

import six


@six.add_metaclass(InterfaceMeta)
class DataDeviceManager(Interface):
    """data transfer interface

    The wl_data_device_manager is a singleton global object that
    provides access to inter-client data transfer mechanisms such as
    copy-and-paste and drag-and-drop.  These mechanisms are tied to
    a wl_seat and this interface lets a client get a wl_data_device
    corresponding to a wl_seat.
    """
    name = "wl_data_device_manager"
    version = 2


@DataDeviceManager.request("n", [DataSource])
def create_data_source(self):
    """create a new data source

    Create a new data source.

    :returns: :class:`DataSource`
    """
    id = self._marshal_constructor(0, DataSource)
    return id


@DataDeviceManager.request("no", [DataDevice, Seat])
def get_data_device(self, seat):
    """create a new data device

    Create a new data device for a given seat.

    :param seat:
    :type seat: :class:`Seat`
    :returns: :class:`DataDevice`
    """
    id = self._marshal_constructor(1, DataDevice, seat)
    return id


DataDeviceManager._gen_c()

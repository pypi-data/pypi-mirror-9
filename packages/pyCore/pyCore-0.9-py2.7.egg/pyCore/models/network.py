"""
Copyright (c) 2014 Maciej Nabozny

This file is part of OverCluster project.

OverCluster is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

from pyCore.utils import request, check_version, VersionException
from pyCore.models.lease import Lease
from pyCore.models.base_model import BaseModel


class Network(BaseModel):
    def __str__(self):
        return self.id


    def delete(self):
        """
        Release network
        """
        request(self.oc_address, '/api/network/delete/', {'token': self.token,
                                                           'network_id': self.id}, self.debug)


    def release(self):
        print "Network.release: this method is obsolete. Use Network.delete"
        self.delete()

    def edit(self, **kwargs):
        for key in kwargs.keys():
            if hasattr(self, key):
                setattr(self, key, kwargs[key])
                request(self.oc_address, '/api/network/edit/', {'token': self.token,
                                                                'network_id': self.id,
                                                                key: kwargs[key]}, self.debug)


    def lease_list(self):
        """
        List leases inside this network
        :return: List of Lease objects
        """
        check_version(self.oc_address, self.token, '1.3')
        leases = request(self.oc_address, '/api/lease/get_list/', {'token': self.token,
                                                                   'network_id': self.id}, self.debug)

        return [Lease(self.oc_address, self.token, lease, self.debug) for lease in leases]


    def lease_create(self, address):
        """
        Create new lease in network
        """
        check_version(self.oc_address, self.token, '1.3')
        l_dict = request(self.oc_address, '/api/lease/create/', {'token': self.token,
                                                                 'address': address,
                                                                 'network_id': self.id}, self.debug)
        return Lease(self.oc_address, self.token, l_dict, self.debug)
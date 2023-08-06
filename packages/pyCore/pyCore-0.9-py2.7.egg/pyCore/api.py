"""
Copyright (c) 2014 Marta Nabozny

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

from utils import request, check_version

from pyCore.models import Template
from pyCore.models import VM
from pyCore.models import Image
from pyCore.models import Network
from pyCore.models import NetworkPool
from pyCore.models import Lease
import importlib


class Api():
    oc_address = None
    token = None
    debug = False
    
    def __init__(self, address, token, debug=False):
        self.token = token
        self.oc_address = address
        self.debug = debug

        api_modules = request(self.oc_address, '/api/api/list_api_modules/', {'token': self.token}, self.debug)
        available_extensions = importlib.import_module('pyCore.extensions')
        for extension in api_modules:
            try:
                ext_model = importlib.import_module('pyCore.extensions.%s.api' % extension)

                ext = ext_model.Api(self)
                setattr(self, extension, ext)
            except:
                continue



    def get_api(self):
        return request(self.oc_address, 'api/api/get_list/', {'token': self.token}, self.debug)


    def list_functions(self):
        return request(self.oc_address, 'api/api/list_functions/', {'token': self.token}, self.debug)


    def list_api_modules(self):
        return request(self.oc_address, 'api/api/list_api_modules/', {'token': self.token}, self.debug)


    def list_ci_modules(self):
        return request(self.oc_address, 'api/api/list_ci_modules/', {'token': self.token}, self.debug)


    def core_version(self):
        return request(self.oc_address, 'api/api/core_version/', {'token': self.token}, self.debug)


    def vm_list(self):
        vms = request(self.oc_address, '/api/vm/get_list/', {'token': self.token}, self.debug)
        return [VM(self.oc_address, self.token, vm, self.debug) for vm in vms]


    def vm_create(self,
                  name,
                  description,
                  template,
                  base_image):
        vm = request(self.oc_address, "/api/vm/create/", {'token': self.token,
                                                       'name': name,
                                                       'description': description,
                                                       'template_id': template.id,
                                                       'base_image_id': base_image.id}, self.debug)
        return VM(self.oc_address, self.token, vm, self.debug)


    def vm_by_id(self, id):
        vm = request(self.oc_address, '/api/vm/get_by_id/', {'token': self.token,
                                                          'vm_id': id}, self.debug)
        return VM(self.oc_address, self.token, vm, self.debug)


    def image_list(self, type=None, access=None, prohibited_states=['deleted']):
        images = request(self.oc_address, '/api/image/get_list/', {'token': self.token,
                                                                'type': type,
                                                                'access': access,
                                                                'prohibited_states': prohibited_states}, self.debug)
        return [Image(self.oc_address, self.token, image, self.debug) for image in images]


    def image_create(self, name, description, size, image_type, disk_controller='virtio', access='private', format='raw'):
        image = request(self.oc_address, '/api/image/create/', {'token': self.token,
                                                             'name': name,
                                                             'description': description,
                                                             'size': size,
                                                             'image_type':image_type,
                                                             'disk_controller': disk_controller,
                                                             'access' : access,
                                                             'format': format}, self.debug)
        return Image(self.oc_address, self.token, image, self.debug)


    def image_by_id(self, id):
        image = request(self.oc_address, '/api/image/get_by_id/', {'token': self.token,
                                                                'image_id': id}, self.debug)
        return Image(self.oc_address, self.token, image, self.debug)


    def supported_disk_controllers(self):
        r = request(self.oc_address, '/api/image/get_disk_controllers/', {'token': self.token}, self.debug)
        return r


    def supported_video_devices(self):
        r = request(self.oc_address, '/api/image/get_video_devices/', {'token': self.token}, self.debug)
        return r


    def supported_network_devices(self):
        r = request(self.oc_address, '/api/image/get_network_devices/', {'token': self.token}, self.debug)
        return r


    def supported_image_types(self):
        r = request(self.oc_address, '/api/image/get_image_types/', {'token': self.token}, self.debug)
        return r


    def supported_image_formats(self):
        r = request(self.oc_address, '/api/image/get_image_formats/', {'token': self.token}, self.debug)
        return r


    def template_list(self):
        templates = request(self.oc_address, '/api/template/get_list/', {'token': self.token}, self.debug)
        return [Template(self.oc_address, self.token, template, self.debug) for template in templates]


    def template_by_id(self, id):
        template = request(self.oc_address, '/api/template/get_by_id/', {'token': self.token,
                                                                         'template_id': id}, self.debug)
        return Template(self.oc_address, self.token, template, self.debug)



    def network_create(self, mask, name, isolated=False, address=None):
        n_dict = request(self.oc_address, '/api/network/create/', {'token': self.token,
                                                                    'mask': mask,
                                                                    'name': name,
                                                                    'address': address,
                                                                    'isolated': isolated}, self.debug)
        return Network(self.oc_address, self.token, n_dict, self.debug)


    def network_request(self, mask, name, isolated=False):
        print "Api.network_request: This method is obsolete. Use network_create"
        self.network_create(mask, name, isolated)


    def network_by_id(self, id):
        n_dict = request(self.oc_address, '/api/network/get_by_id/', {'token': self.token,
                                                                      'network_id': id}, self.debug)
        return Network(self.oc_address, self.token, n_dict, self.debug)


    def network_pool_list(self):
        pools = request(self.oc_address, '/api/network/get_pool_list/', {'token': self.token}, self.debug)
        return [NetworkPool(self.oc_address, self.token, n, self.debug) for n in pools]


    def network_list(self):
        networks = request(self.oc_address, '/api/network/get_list/', {'token': self.token}, self.debug)
        return [Network(self.oc_address, self.token, network, self.debug) for network in networks]


    def lease_by_id(self, id):
        lease = request(self.oc_address, '/api/lease/get_by_id/', {'token': self.token,
                                                                   'lease_id': id}, self.debug)
        return Lease(self.oc_address, self.token, lease, self.debug)


    def lease_list(self):
        """
        List leases inside this network
        :return: List of Lease objects
        """
        check_version(self.address, self.token, '1.3')
        leases = request(self.oc_address, '/api/lease/get_list/', {'token': self.token}, self.debug)

        return [Lease(self.oc_address, self.token, lease, self.debug) for lease in leases]

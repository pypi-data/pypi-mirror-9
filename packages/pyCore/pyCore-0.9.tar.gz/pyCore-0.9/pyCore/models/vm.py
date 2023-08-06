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

from pyCore.utils import request
from pyCore.models.template import Template
from pyCore.models.image import Image
from pyCore.models.base_model import BaseModel
from pyCore.models.task import Task
from pyCore.models.lease import Lease

class VM(BaseModel):
    def __init__(self, *args, **kwargs):
        super(VM, self).__init__(*args, **kwargs)
        self.template = Template(self.oc_address, self.token, self.template)
        self.base_image = Image(self.oc_address, self.token, self.base_image)

        t = []
        for task in self.tasks:
            t.append(Task(self.oc_address, self.token, task, self.debug))
        self.tasks = t

        d = []
        for disk in self.disks:
            d.append(Image(self.oc_address, self.token, disk, self.debug))
        self.disks = d

        l = []
        for lease in self.leases:
            l.append(Lease(self.oc_address, self.token, lease, self.debug))
        self.leases = l

    def __str__(self):
        return self.name
        
    def reset(self):
        request(self.oc_address, '/api/vm/reset/', {'token': self.token,
                                                    'vm_id': self.id}, self.debug)
        
    def poweroff(self):
        request(self.oc_address, '/api/vm/poweroff/', {'token': self.token,
                                                       'vm_id': self.id}, self.debug)
        
    def shutdown(self):
        request(self.oc_address, '/api/vm/shutdown/', {'token': self.token,
                                                       'vm_id': self.id}, self.debug)
        
    def cleanup(self):
        request(self.oc_address, '/api/vm/cleanup/', {'token': self.token,
                                                      'vm_id': self.id}, self.debug)
        
    def start(self):
        request(self.oc_address, '/api/vm/start/', {'token': self.token,
                                                    'vm_id': self.id}, self.debug)

    def save_image(self):
        request(self.oc_address, '/api/vm/save_image/', {'token': self.token,
                                                         'vm_id': self.id}, self.debug)

    def cancel_tasks(self):
        request(self.oc_address, '/api/vm/cancel_tasks/', {'token': self.token,
                                                           'vm_id': self.id}, self.debug)

    def console(self, enable):
        request(self.oc_address, '/api/vm/console/', {'token': self.token,
                                                     'vm_id': self.id,
                                                     'enable': enable}, self.debug)

    def edit(self, **kwargs):
        for key in kwargs.keys():
            if hasattr(self, key):
                setattr(self, key, kwargs[key])
                request(self.oc_address, '/api/vm/edit/', {'token': self.token,
                                                           'vm_id': self.id,
                                                           key: kwargs[key]}, self.debug)

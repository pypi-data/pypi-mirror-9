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

from pyCore.utils import request, calc_hash
from pyCore.models.base_model import BaseModel

class Token(BaseModel):
    def __init__(self, address, login, password, seed, token_dict, debug=False):
        self.login = login
        self.password = password
        self.oc_address = address
        self.seed = seed
        self.debug = debug

        self.token = None
        tokens = request(self.oc_address, '/user/token/get_list/', {'login': self.login,
                                                                 'pw_hash': calc_hash(self.password, self.seed),
                                                                 'name': 'pycloud'}, self.debug)
        if len(tokens) == 0:
            self.token = request(self.oc_address, '/user/token/create/', {'login': self.login,
                                                                  'pw_hash': calc_hash(self.password, self.seed),
                                                                  'name': 'pycloud'}, self.debug)['token']
        else:
            self.token = tokens[0]['token']

        BaseModel.__init__(self, self.oc_address, self.token, token_dict)


    def __str__(self):
        return self.id

    def delete(self):
        request(self.oc_address, '/user/token/delete/', {'login': self.login,
                                                      'pw_hash': calc_hash(self.password, self.seed),
                                                      'token_id': self.id}, self.debug)


    def edit(self, **kwargs):
        for key in kwargs.keys():
            if hasattr(self, key):
                setattr(self, key, kwargs[key])
                request(self.oc_address, '/user/token/edit/', {'login': self.login,
                                                               'pw_hash': calc_hash(self.password, self.seed),
                                                               'vm_id': self.id,
                                                               key: kwargs[key]}, self.debug)

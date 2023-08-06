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

class Token():
    def __init__(self, parent_model):
        self.parent_model = parent_model

    def enable(self, enable):
        request(self.parent_model.oc_address, '/coreDav/webdav/enable/', {'login': self.parent_model.login,
                                           'pw_hash': calc_hash(self.parent_model.password, self.parent_model.seed),
                                           'token_id': self.parent_model.id,
                                           'enable': enable})

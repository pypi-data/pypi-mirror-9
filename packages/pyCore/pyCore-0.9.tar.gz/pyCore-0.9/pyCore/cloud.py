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

from utils import request, calc_hash
from api import Api
from pyCore.models.token import Token
import datetime

class Cloud():
    """
    Basic class for operations on user's account in OverCluster.
    """
    oc_address = None
    login = None
    password = None
    seed = None
    debug = False

    def __init__(self, address, login, password, debug=False):
        self.oc_address = address
        self.login = login
        self.password = password
        self.debug = debug
        self.seed = request(self.oc_address, '/user/user/get_seed/', {'login': self.login}, debug)["seed"]

    def get_api(self):
        """
        Generate API object and fetch token for it's instance to manage all non-user
        functions in cloud. Api class could be generated without calling this
        function, unless you have valid token.
        """
        token = None
        tokens = request(self.oc_address, '/user/token/get_list/', {'login': self.login,
                                                                 'pw_hash': calc_hash(self.password, self.seed),
                                                                 'name': 'pycloud'}, self.debug)
        if len(tokens) == 0:
            token = request(self.oc_address, '/user/token/create/', {'login': self.login,
                                                                  'pw_hash': calc_hash(self.password, self.seed),
                                                                  'name': 'pycloud'}, self.debug)['token']
        else:
            token = tokens[0]['token']

        return Api(self.oc_address, token, self.debug)

    @staticmethod
    def register(address, login, password, name, surname, email, debug=False):
        """
        Register new user account
        """
        request(address, '/user/user/register/', {'login':login,
                                                  'password': password,
                                                  'name':name,
                                                  'surname': surname,
                                                  'email': email}, debug)
        return Cloud(address, login, password, debug)

    def token_by_id(self, token_id):
        token = request(self.oc_address, '/user/token/get/', {'login': self.login,
                                                           'pw_hash': calc_hash(self.password, self.seed),
                                                           'token_id': token_id}, self.debug)
        return Token(self.oc_address, self.login, self.password, self.seed, token, self.debug)


    def token_list(self):
        tokens = request(self.oc_address, '/user/token/get_list/', {'login': self.login,
                                                                 'pw_hash': calc_hash(self.password, self.seed)}, self.debug)
        token_list = []
        for token in tokens:
            token_list.append(Token(self.oc_address, self.login, self.password, self.seed, token, self.debug))

        return token_list

    def token_create(self, name='', function_filter='', token_valid_to=datetime.datetime.now()+datetime.timedelta(1)):
        token = request(self.oc_address, '/user/token/create/', {'login': self.login,
                                                              'pw_hash': calc_hash(self.password, self.seed),
                                                              'name': name,
                                                              'function_filter': function_filter,
                                                              'token_valid_to': str(token_valid_to)}, self.debug)

        return Token(self.oc_address, self.login, self.password, self.seed, token, self.debug)
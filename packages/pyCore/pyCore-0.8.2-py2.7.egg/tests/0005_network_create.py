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


import settings
from pyCore import Cloud
import time

api = None
cloud = None
network_private = None
network_public = None
leases = None

def setup_module(module):
    global cloud
    global api

    cloud = Cloud(settings.address, settings.login, settings.password)
    api = cloud.get_api()


def teardown_module(module):
    pass

def setup_function(function):
    pass

def teardown_function(function):
    pass


def test_network_create():
    global api
    global network_private
    global network_public
    network_public = api.network_request(24, "Normal Network", False)
    network_private = api.network_request(24, "Isolated Network", True)


def test_list_leases():
    global network_private
    network_private.lease_list()


def test_network_release():
    global api
    global network_public
    global network_private

    network_private.release()
    network_public.release()


def test_create_test_network():
    global api
    networks = api.network_list()
    names = [network.name for network in networks]
    if not "Test public network" in names:
        api.network_request(24, "Test public network", False)
    if not "Test isolated network" in names:
        api.network_request(24, "Test isolated network", False)
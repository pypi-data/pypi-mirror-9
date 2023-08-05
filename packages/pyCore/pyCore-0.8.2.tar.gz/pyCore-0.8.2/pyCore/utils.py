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

import requests
import hashlib
import json

request_id = 0

def request(address, function, params, debug=False):
    global request_id
    request_id = request_id + 1

    data = json.dumps(params)
    if debug:
        print 'request (%d):\t%s( %s )' % (request_id, function, data)

    if address.endswith('/'):
        address = address[:-1]
    if function.startswith('/'):
        function = function[1:]

    resp = requests.post(address + '/' + function, data)

    r = json.loads(resp.text)


    if debug:
        print "response (%d):\t%s" % (request_id, r['status'])
        print "\t\t" + resp.text

    if r['status'] != 'ok':
        raise Exception(r['status'])
    else:
        return r['data']

def calc_hash(password, seed):
    return hashlib.sha1(password + seed).hexdigest()
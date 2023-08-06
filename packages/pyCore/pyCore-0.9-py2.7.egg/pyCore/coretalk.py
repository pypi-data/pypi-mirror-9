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

import importlib

from utils import request

def trigger(event):
    """
    Execute trigger on given event in vm
    """
    requests = request('http://core.cloudover.org:8001', '/coreTalkApi/vm/trigger/', {'event': event})
    for r in requests:
        module = importlib.import_module("pyCore.triggers.%s" % r['type'])
        module.trigger(r)
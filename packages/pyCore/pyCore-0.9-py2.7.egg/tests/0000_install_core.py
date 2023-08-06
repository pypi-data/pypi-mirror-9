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

import subprocess
import settings
import urllib2
import os

core_address = None

def ssh_call(hostname, username, command, expect_code=None):
    p = subprocess.Popen(['ssh', '%s@%s' % (username, hostname), command], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    p.wait()
    stdout = p.stdout.read()
    stderr = p.stderr.read()
    print '%s@%s' % (username, hostname) + ": " + command + ": " + stdout

    if expect_code != None and p.returncode != expect_code:
        print "STDOUT: " + stdout
        print "##################"
        print "STDERR: " + stderr
        print "##################"
        raise Exception('command %s failed' % command)

    return (p.returncode, stdout, stderr)


def setup_module(module):
    global core_address
    core_address = urllib2.urlparse.urlparse(settings.address).hostname


def teardown_module(module):
    pass


def setup_function(function):
    pass


def teardown_function(function):
    pass


def test_ssh_key():
    global core_address
    ssh_key = open(os.getenv("HOME") + '/.ssh/id_rsa.pub').read()
    subprocess.call(['ssh', 'root@' + core_address, 'if ! [ -d .ssh ] ; then mkdir .ssh ; fi ; chmod 700 .ssh ; echo "%s" >> .ssh/authorized_keys ; chmod 600 .ssh/authorized_keys' % ssh_key])


def test_apt_add():
    global core_address
    ssh_call(core_address, 'root', 'echo deb http://packages.cloudover.org/debian/ nightly main >> /etc/apt/sources.list')
    ssh_call(core_address, 'root', 'apt-get update', 0)


def test_install_extra():
    global core_address
    ssh_call(core_address, 'root', 'apt-get --yes --force-yes install ipython mc htop screen tcpdump traceroute', 0)


def test_install_storage():
    global core_address
    ssh_call(core_address, 'root', 'apt-get --yes --force-yes install overcluster-storage', 0)


def test_install_core():
    global core_address
    ssh_call(core_address, 'root', 'DEBIAN_FRONTEND=noninteractive apt-get --yes --force-yes install overcluster-core', 0)


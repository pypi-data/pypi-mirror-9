# Copyright 2013-2014 GRNET S.A. All rights reserved.
#
# Redistribution and use in source and binary forms, with or
# without modification, are permitted provided that the following
# conditions are met:
#
#   1. Redistributions of source code must retain the above
#      copyright notice, this list of conditions and the following
#      disclaimer.
#
#   2. Redistributions in binary form must reproduce the above
#      copyright notice, this list of conditions and the following
#      disclaimer in the documentation and/or other materials
#      provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY GRNET S.A. ``AS IS'' AND ANY EXPRESS
# OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL GRNET S.A OR
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF
# USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED
# AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#
# The views and conclusions contained in the software and
# documentation are those of the authors and should not be
# interpreted as representing official policies, either expressed
# or implied, of GRNET S.A.

from mock import patch, call
from unittest import TestCase
from itertools import product

from kamaki.clients import cyclades

img_ref = "1m4g3-r3f3r3nc3"
vm_name = "my new VM"
fid = 42
vm_recv = dict(server=dict(
    status="BUILD",
    updated="2013-03-01T10:04:00.637152+00:00",
    hostId="",
    name=vm_name,
    imageRef=img_ref,
    created="2013-03-01T10:04:00.087324+00:00",
    flavorRef=fid,
    adminPass="n0n3sh@11p@55",
    suspended=False,
    progress=0,
    id=31173,
    metadata=dict(os="debian", users="root")))
vm_list = dict(servers=[
    dict(name='n1', id=1),
    dict(name='n2', id=2)])
net_send = dict(network=dict(dhcp=False, name='someNet'))
net_recv = dict(network=dict(
    status="PENDING",
    updated="2013-03-05T15:04:51.758780+00:00",
    name="someNet",
    created="2013-03-05T15:04:51.758728+00:00",
    cidr6=None,
    id="2130",
    gateway6=None,
    public=False,
    dhcp=False,
    cidr="192.168.1.0/24",
    type="MAC_FILTERED",
    gateway=None,
    attachments=[dict(name='att1'), dict(name='att2')]))
net_list = dict(networks=[
    dict(id=1, name='n1'),
    dict(id=2, name='n2'),
    dict(id=3, name='n3')])
firewalls = dict(attachments=[
    dict(firewallProfile='50m3_pr0f1L3', otherStuff='57uff')])


class FR(object):
    """FR stands for Fake Response"""
    json = vm_recv
    headers = {}
    content = json
    status = None
    status_code = 200

rest_pkg = 'kamaki.clients.cyclades.CycladesComputeRestClient'
cyclades_pkg = 'kamaki.clients.cyclades.CycladesComputeClient'


class CycladesComputeRestClient(TestCase):

    def setUp(self):
        self.url = 'http://cyclades.example.com'
        self.token = 'cyc14d3s70k3n'
        self.client = cyclades.CycladesComputeRestClient(self.url, self.token)

    @patch('kamaki.clients.Client.get', return_value='ret')
    def test_servers_stats_get(self, get):
        server_id = 'server id'
        self.assertEqual(self.client.servers_stats_get(server_id), 'ret')
        get.assert_called_once_with(
            '/servers/%s/stats' % server_id, success=200)

    @patch('kamaki.clients.Client.get', return_value='ret')
    def test_servers_diagnostics_get(self, get):
        server_id = 'server id'
        self.assertEqual(
            self.client.servers_diagnostics_get(server_id), 'ret')
        get.assert_called_once_with(
            '/servers/%s/diagnostics' % server_id, success=200)


class CycladesNetworkClient(TestCase):

    """Set up a ComputesRest thorough test"""
    def setUp(self):
        self.url = 'http://network.example.com'
        self.token = 'n2tw0rk70k3n'
        self.client = cyclades.CycladesNetworkClient(self.url, self.token)

    def tearDown(self):
        FR.json = vm_recv
        del self.client

    @patch('kamaki.clients.Client.get', return_value=FR)
    def test_list_networks(self, get):
        FR.json = dict(networks='ret val')
        for detail in (True, None):
            self.assertEqual(self.client.list_networks(detail), 'ret val')
            path = '/networks/detail' if detail else '/networks'
            self.assertEqual(get.mock_calls[-1], call(path, success=200))

    @patch(
        'kamaki.clients.network.rest_api.NetworkRestClient.networks_post',
        return_value=FR())
    def test_create_network(self, networks_post):
        for name, shared in product((None, 'net name'), (None, True)):
            FR.json = dict(network='ret val')
            type = 'net type'
            self.assertEqual(
                self.client.create_network(type, name=name, shared=shared),
                'ret val')
            req = dict(type=type, admin_state_up=True)
            if name:
                req['name'] = name
            if shared:
                req['shared'] = shared
            expargs = dict(json_data=dict(network=req), success=201)
            self.assertEqual(networks_post.mock_calls[-1], call(**expargs))

    @patch(
        'kamaki.clients.network.rest_api.NetworkRestClient.ports_post',
        return_value=FR)
    def test_create_port(self, ports_post):
        network_id, device_id, FR.json = 'netid', 'devid', dict(port='ret v')
        for name, sec_grp, fixed_ips in product(
                ('port name', None),
                ([1, 2, 3], None),
                (
                    [dict(subnet_id='sid', ip_address='ipa')],
                    [dict(subnet_id='sid')], [dict(ip_address='ipa')],
                    None)):

            if fixed_ips:
                diff = set(['ip_address', ]).difference(fixed_ips[0])
                if diff:
                    self.assertRaises(
                        ValueError, self.client.create_port,
                        network_id, device_id,
                        name=name,
                        security_groups=sec_grp,
                        fixed_ips=fixed_ips)
                    continue
            self.assertEqual(
                self.client.create_port(
                    network_id, device_id,
                    name=name, security_groups=sec_grp, fixed_ips=fixed_ips),
                'ret v')
            req = dict(network_id=network_id, device_id=device_id)
            if sec_grp:
                req['security_groups'] = sec_grp
            if name:
                req['name'] = name
            if fixed_ips:
                req['fixed_ips'] = fixed_ips
            expargs = dict(json_data=dict(port=req), success=201)
            self.assertEqual(ports_post.mock_calls[-1], call(**expargs))


class CycladesComputeClient(TestCase):

    def assert_dicts_are_equal(self, d1, d2):
        for k, v in d1.items():
            self.assertTrue(k in d2)
            if isinstance(v, dict):
                self.assert_dicts_are_equal(v, d2[k])
            else:
                self.assertEqual(unicode(v), unicode(d2[k]))

    """Set up a Cyclades thorough test"""
    def setUp(self):
        self.url = 'http://cyclades.example.com'
        self.token = 'cyc14d3s70k3n'
        self.client = cyclades.CycladesComputeClient(self.url, self.token)

    def tearDown(self):
        FR.status_code = 200
        FR.json = vm_recv

    @patch('%s.servers_action_post' % cyclades_pkg, return_value=FR())
    def test_shutdown_server(self, SP):
        vm_id = vm_recv['server']['id']
        self.client.shutdown_server(vm_id)
        SP.assert_called_once_with(
            vm_id, json_data=dict(shutdown=dict()), success=202)

    @patch('%s.servers_action_post' % cyclades_pkg, return_value=FR())
    def test_start_server(self, SP):
        vm_id = vm_recv['server']['id']
        self.client.start_server(vm_id)
        SP.assert_called_once_with(
            vm_id, json_data=dict(start=dict()), success=202)

    @patch('%s.servers_action_post' % cyclades_pkg, return_value=FR())
    def test_get_server_console(self, SP):
        cnsl = dict(console=dict(info1='i1', info2='i2', info3='i3'))
        FR.json = cnsl
        vm_id, foo = vm_recv['server']['id'], self.client.get_server_console
        self.assertRaises(AssertionError, foo, vm_id, None)
        self.assertRaises(AssertionError, foo, vm_id, 'Invalid console type')
        for ctype in self.client.CONSOLE_TYPES:
            r = foo(vm_id, ctype)
            self.assertEqual(SP.mock_calls[-1], call(
                vm_id, json_data=dict(console=dict(type=ctype)), success=200))
            self.assert_dicts_are_equal(r, cnsl['console'])


clients_pkg = 'kamaki.clients.Client'


class CycladesBlockStorageRestClient(TestCase):

    def setUp(self):
        self.url = 'http://volumes.example.com'
        self.token = 'v01um3s70k3n'
        self.client = cyclades.rest_api.CycladesBlockStorageRestClient(
            self.url, self.token)

    @patch('%s.post' % clients_pkg)
    def test_volumes_post(self, post):
        keys = (
            'display_description', 'snapshot_id', 'imageRef',
            'volume_type', 'metadata', 'project')
        for args in product(
                ('dd', None), ('sn', None), ('ir', None),
                ('vt', None), ({'mk': 'mv'}, None), ('pid', None),
                ({'k1': 'v1', 'k2': 'v2'}, {'success': 1000}, {})):
            kwargs, server_id, display_name = args[-1], 'sid', 'dn'
            args = args[:-1]
            for err, size in ((TypeError, None), (ValueError, 'size')):
                self.assertRaises(
                    err, self.client.volumes_post,
                    size, server_id, display_name, *args, **kwargs)
            size = 42
            self.client.volumes_post(
                size, server_id, display_name, *args, **kwargs)
            volume = dict(
                size=int(size), server_id=server_id, display_name=display_name)
            for k, v in zip(keys, args):
                if v:
                    volume[k] = v
            success, jsondata = kwargs.pop('success', 202), dict(volume=volume)
            self.assertEqual(
                post.mock_calls[-1],
                call('/volumes', json=jsondata, success=success, **kwargs))

    @patch('%s.post' % clients_pkg)
    def test_volumes_action_post(self, post):
        for kwargs in ({'k1': 'v1', 'k2': 'v2'}, {'success': 1000}, {}):
            volume_id, project_id = 'vid', 'pid'
            self.client.volumes_action_post(volume_id, project_id, **kwargs)
            success = kwargs.pop('success', 200)
            self.assertEqual(post.mock_calls[-1], call(
                '/volumes/%s/action' % volume_id,
                json=project_id, success=success, **kwargs))


bsrest_pkg = 'kamaki.clients.cyclades.CycladesBlockStorageRestClient'


class CycladesBlockStorageClient(TestCase):

    def setUp(self):
        self.url = 'http://volumes.example.com'
        self.token = 'v01um3s70k3n'
        self.client = cyclades.CycladesBlockStorageClient(self.url, self.token)

    @patch('%s.volumes_post' % bsrest_pkg, return_value=FR())
    def test_create_volume(self, volumes_post):
        keys = (
            'display_description', 'snapshot_id', 'imageRef',
            'volume_type', 'metadata', 'project')
        FR.json, server_id, display_name = dict(volume='ret'), 'vid', 'dn'
        for args in product(
                ('dd', None), ('sn', None), ('ir', None),
                ('vt', None), ({'mk': 'mv'}, None), ('pid', None)):
            self.assertEqual(
                self.client.create_volume(42, server_id, display_name, *args),
                'ret')
            kwargs = dict(zip(keys, args))
            self.assertEqual(
                volumes_post.mock_calls[-1],
                call(42, server_id, display_name, **kwargs))

    @patch('%s.volumes_action_post' % bsrest_pkg, return_value=FR())
    def test_reassign_volume(self, volumes_action_post):
        volume_id, project_id = 'vid', 'pid'
        self.client.reassign_volume(volume_id, project_id)
        volumes_action_post.assert_called_once_with(
            volume_id, {"reassign": {"project": project_id}})

    @patch('%s.create_snapshot' % bsrest_pkg, return_value='ret')
    def test_create_snapshot(self, create_snapshot):
        keys = ('force', 'display_description')
        volume_id, display_name = 'vid', 'dn'
        for args in product((True, False, None), ('dd', None)):
            self.assertEqual(
                self.client.create_snapshot(volume_id, display_name, *args),
                'ret')
            kwargs = dict(zip(keys, args))
            self.assertEqual(
                create_snapshot.mock_calls[-1],
                call(volume_id, display_name=display_name, **kwargs))


if __name__ == '__main__':
    from sys import argv
    from kamaki.clients.test import runTestCase
    not_found = True
    if not argv[1:] or argv[1] == 'CycladesComputeClient':
        not_found = False
        runTestCase(CycladesNetworkClient, 'Cyclades Client', argv[2:])
    if not argv[1:] or argv[1] == 'CycladesNetworkClient':
        not_found = False
        runTestCase(CycladesNetworkClient, 'CycladesNetwork Client', argv[2:])
    if not argv[1:] or argv[1] == 'CycladesComputeRestClient':
        not_found = False
        runTestCase(CycladesComputeRestClient, 'CycladesRest Client', argv[2:])
    if not argv[1:] or argv[1] == 'CycladesBlockStorageRestClient':
        not_found = False
        runTestCase(
            CycladesBlockStorageRestClient,
            'Cyclades Block Storage Rest Client',
            argv[2:])
    if not argv[1:] or argv[1] == 'CycladesBlockStorageClient':
        not_found = False
        runTestCase(
            CycladesBlockStorageClient,
            'Cyclades Block Storage Client',
            argv[2:])
    if not_found:
        print('TestCase %s not found' % argv[1])

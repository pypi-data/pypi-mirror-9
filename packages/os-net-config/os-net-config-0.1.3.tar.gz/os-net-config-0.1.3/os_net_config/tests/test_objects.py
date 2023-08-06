# -*- coding: utf-8 -*-

# Copyright 2014 Red Hat, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import json
import six

from os_net_config import objects
from os_net_config.tests import base
from os_net_config import utils


class TestRoute(base.TestCase):

    def test_from_json(self):
        data = '{"next_hop": "172.19.0.1", "ip_netmask": "172.19.0.0/24"}'
        route = objects.Route.from_json(json.loads(data))
        self.assertEqual("172.19.0.1", route.next_hop)
        self.assertEqual("172.19.0.0/24", route.ip_netmask)
        self.assertEqual(False, route.default)

    def test_from_json_default_route(self):
        data = '{"next_hop": "172.19.0.1", "ip_netmask": "172.19.0.0/24", ' \
               '"default": true}'
        route = objects.Route.from_json(json.loads(data))
        self.assertEqual("172.19.0.1", route.next_hop)
        self.assertEqual("172.19.0.0/24", route.ip_netmask)
        self.assertEqual(True, route.default)

        data = '{"next_hop": "172.19.0.1", "ip_netmask": "172.19.0.0/24", ' \
               '"default": "true"}'
        route = objects.Route.from_json(json.loads(data))
        self.assertEqual("172.19.0.1", route.next_hop)
        self.assertEqual("172.19.0.0/24", route.ip_netmask)
        self.assertEqual(True, route.default)


class TestAddress(base.TestCase):

    def test_ipv4_address(self):
        address = objects.Address('192.168.1.1/24')
        self.assertEqual("192.168.1.1", address.ip)
        self.assertEqual("255.255.255.0", address.netmask)
        self.assertEqual(4, address.version)

    def test_ipv6_address(self):
        address = objects.Address('2001:abc:a::/64')
        self.assertEqual("2001:abc:a::", address.ip)
        self.assertEqual("ffff:ffff:ffff:ffff::", address.netmask)
        self.assertEqual(6, address.version)

    def test_from_json(self):
        data = '{"ip_netmask": "192.0.2.5/24"}'
        address = objects.Address.from_json(json.loads(data))
        self.assertEqual("192.0.2.5", address.ip)
        self.assertEqual("255.255.255.0", address.netmask)
        self.assertEqual(4, address.version)

    def test_from_json_invalid(self):
        self.assertRaises(objects.InvalidConfigException,
                          objects.Address.from_json,
                          {})
        data = '{"ip_netmask": false}'
        json_data = json.loads(data)
        self.assertRaises(objects.InvalidConfigException,
                          objects.Address.from_json,
                          json_data)


class TestInterface(base.TestCase):

    def test_interface_addresses(self):
        v4_addr = objects.Address('192.168.1.1/24')
        v6_addr = objects.Address('2001:abc:a::/64')
        interface = objects.Interface('foo', addresses=[v4_addr, v6_addr])
        self.assertEquals("192.168.1.1", interface.v4_addresses()[0].ip)
        self.assertEquals("2001:abc:a::", interface.v6_addresses()[0].ip)

    def test_from_json_dhcp(self):
        data = '{"type": "interface", "name": "em1", "use_dhcp": true}'
        interface = objects.object_from_json(json.loads(data))
        self.assertEqual("em1", interface.name)
        self.assertEqual(True, interface.use_dhcp)

    def test_from_json_dhcp_nic1(self):
        def dummy_numbered_nics(nic_mapping=None):
            return {"nic1": "em3"}
        self.stubs.Set(objects, '_numbered_nics', dummy_numbered_nics)

        data = '{"type": "interface", "name": "nic1", "use_dhcp": true}'
        interface = objects.object_from_json(json.loads(data))
        self.assertEqual("em3", interface.name)
        self.assertEqual(True, interface.use_dhcp)

    def test_from_json_with_addresses(self):
        data = """{
"type": "interface",
"name": "em1",
"use_dhcp": false,
"mtu": 1501,
"addresses": [{
    "ip_netmask": "192.0.2.1/24"
}],
"routes": [{
    "next_hop": "192.0.2.1",
    "ip_netmask": "192.0.2.1/24"
}]
}
"""
        interface = objects.object_from_json(json.loads(data))
        self.assertEqual("em1", interface.name)
        self.assertEqual(False, interface.use_dhcp)
        self.assertEqual(False, interface.use_dhcpv6)
        self.assertEqual(1501, interface.mtu)
        address1 = interface.v4_addresses()[0]
        self.assertEqual("192.0.2.1", address1.ip)
        self.assertEqual("255.255.255.0", address1.netmask)
        route1 = interface.routes[0]
        self.assertEqual("192.0.2.1", route1.next_hop)
        self.assertEqual("192.0.2.1/24", route1.ip_netmask)


class TestVlan(base.TestCase):

    def test_from_json_dhcp(self):
        data = '{"type": "vlan", "device": "em1", "vlan_id": 16,' \
               '"use_dhcp": true}'
        vlan = objects.object_from_json(json.loads(data))
        self.assertEqual("em1", vlan.device)
        self.assertEqual(16, vlan.vlan_id)
        self.assertEqual(True, vlan.use_dhcp)

    def test_from_json_dhcp_nic1(self):
        def dummy_numbered_nics(nic_mapping=None):
            return {"nic1": "em4"}
        self.stubs.Set(objects, '_numbered_nics', dummy_numbered_nics)

        data = '{"type": "vlan", "device": "nic1", "vlan_id": 16,' \
               '"use_dhcp": true}'
        vlan = objects.object_from_json(json.loads(data))
        self.assertEqual("em4", vlan.device)
        self.assertEqual(16, vlan.vlan_id)
        self.assertEqual(True, vlan.use_dhcp)


class TestBridge(base.TestCase):

    def test_from_json_dhcp(self):
        data = """{
"type": "ovs_bridge",
"name": "br-foo",
"use_dhcp": true,
"members": [{
    "type": "interface",
    "name": "em1"
}]
}
"""
        bridge = objects.object_from_json(json.loads(data))
        self.assertEqual("br-foo", bridge.name)
        self.assertEqual(True, bridge.use_dhcp)
        interface1 = bridge.members[0]
        self.assertEqual("em1", interface1.name)
        self.assertEqual(True, interface1.ovs_port)
        self.assertEqual("br-foo", interface1.bridge_name)

    def test_from_json_dhcp_with_nic1(self):
        def dummy_numbered_nics(nic_mapping=None):
            return {"nic1": "em5"}
        self.stubs.Set(objects, '_numbered_nics', dummy_numbered_nics)

        data = """{
"type": "ovs_bridge",
"name": "br-foo",
"use_dhcp": true,
"members": [{
    "type": "interface",
    "name": "nic1"
}]
}
"""
        bridge = objects.object_from_json(json.loads(data))
        self.assertEqual("br-foo", bridge.name)
        self.assertEqual(True, bridge.use_dhcp)
        interface1 = bridge.members[0]
        self.assertEqual("em5", interface1.name)
        self.assertEqual(True, interface1.ovs_port)
        self.assertEqual("br-foo", interface1.bridge_name)

    def test_from_json_primary_interface(self):
        data = """{
"type": "ovs_bridge",
"name": "br-foo",
"use_dhcp": true,
"members": [
    {
    "type": "interface",
    "name": "em1",
    "primary": "true"
    },
    {
    "type": "interface",
    "name": "em2"
    }]
}
"""
        bridge = objects.object_from_json(json.loads(data))
        self.assertEqual("br-foo", bridge.name)
        self.assertEqual(True, bridge.use_dhcp)
        self.assertEqual("em1", bridge.primary_interface_name)
        interface1 = bridge.members[0]
        self.assertEqual("em1", interface1.name)
        self.assertEqual(True, interface1.ovs_port)
        self.assertEqual(True, interface1.primary)
        self.assertEqual("br-foo", interface1.bridge_name)
        interface2 = bridge.members[1]
        self.assertEqual("em2", interface2.name)
        self.assertEqual(True, interface2.ovs_port)
        self.assertEqual("br-foo", interface2.bridge_name)


class TestBond(base.TestCase):

    def test_from_json_dhcp(self):
        data = """{
"type": "ovs_bond",
"name": "bond1",
"use_dhcp": true,
"members": [
    {
    "type": "interface",
    "name": "em1"
    },
    {
    "type": "interface",
    "name": "em2"
    }
]
}
"""
        bridge = objects.object_from_json(json.loads(data))
        self.assertEqual("bond1", bridge.name)
        self.assertEqual(True, bridge.use_dhcp)
        interface1 = bridge.members[0]
        self.assertEqual("em1", interface1.name)
        interface2 = bridge.members[1]
        self.assertEqual("em2", interface2.name)

    def test_from_json_dhcp_with_nic1_nic2(self):

        def dummy_numbered_nics(nic_mapping=None):
            return {"nic1": "em1", "nic2": "em2"}
        self.stubs.Set(objects, '_numbered_nics', dummy_numbered_nics)

        data = """{
"type": "ovs_bond",
"name": "bond1",
"use_dhcp": true,
"members": [
    {
    "type": "interface",
    "name": "nic1"
    },
    {
    "type": "interface",
    "name": "nic2"
    }
]
}
"""
        bridge = objects.object_from_json(json.loads(data))
        self.assertEqual("bond1", bridge.name)
        self.assertEqual(True, bridge.use_dhcp)
        interface1 = bridge.members[0]
        self.assertEqual("em1", interface1.name)
        interface2 = bridge.members[1]
        self.assertEqual("em2", interface2.name)


class TestNumberedNicsMapping(base.TestCase):

    # We want to test the function, not the dummy..
    stub_numbered_nics = False

    def tearDown(self):
        super(TestNumberedNicsMapping, self).tearDown()
        objects._NUMBERED_NICS = None

    def _stub_active_nics(self, nics):
        def dummy_ordered_active_nics():
            return nics
        self.stubs.Set(utils, 'ordered_active_nics', dummy_ordered_active_nics)

    def test_numbered_nics_default(self):
        self._stub_active_nics(['em1', 'em2'])
        expected = {'nic1': 'em1', 'nic2': 'em2'}
        self.assertEqual(expected, objects._numbered_nics())

    def test_numbered_nics_mapped(self):
        self._stub_active_nics(['em1', 'em2'])
        mapping = {'nic1': 'em2', 'nic2': 'em1'}
        expected = {'nic1': 'em2', 'nic2': 'em1'}
        self.assertEqual(expected, objects._numbered_nics(nic_mapping=mapping))

    def test_numbered_nics_mapped_partial(self):
        self._stub_active_nics(['em1', 'em2', 'em3', 'em4'])
        mapping = {'nic1': 'em2', 'nic2': 'em1'}
        expected = {'nic1': 'em2', 'nic2': 'em1', 'nic3': 'em3', 'nic4': 'em4'}
        self.assertEqual(expected, objects._numbered_nics(nic_mapping=mapping))

    def test_numbered_nics_map_error_notactive(self):
        self._stub_active_nics(['em1', 'em2'])
        mapping = {'nic1': 'em3', 'nic2': 'em1'}
        expected = {'nic2': 'em1'}
        self.assertEqual(expected, objects._numbered_nics(nic_mapping=mapping))

    def test_numbered_nics_map_error_duplicate(self):
        self._stub_active_nics(['em1', 'em2'])
        mapping = {'nic1': 'em1', 'nic2': 'em1'}
        err = self.assertRaises(objects.InvalidConfigException,
                                objects._numbered_nics, nic_mapping=mapping)
        expected = 'em1 already mapped, check mapping file for duplicates'
        self.assertIn(expected, six.text_type(err))

    def test_numbered_nics_map_mac(self):
        def dummy_interface_mac(name):
            mac_map = {'em1': '12:34:56:78:9a:bc',
                       'em2': '12:34:56:de:f0:12'}
            return mac_map[name]
        self.stubs.Set(utils, 'interface_mac', dummy_interface_mac)
        self._stub_active_nics(['em1', 'em2'])
        mapping = {'nic1': '12:34:56:de:f0:12', 'nic2': '12:34:56:78:9a:bc'}
        expected = {'nic1': 'em2', 'nic2': 'em1'}
        self.assertEqual(expected, objects._numbered_nics(nic_mapping=mapping))

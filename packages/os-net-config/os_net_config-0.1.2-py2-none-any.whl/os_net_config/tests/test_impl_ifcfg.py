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

import os.path
import tempfile

from oslo_concurrency import processutils

from os_net_config import impl_ifcfg
from os_net_config import objects
from os_net_config.tests import base
from os_net_config import utils


_BASE_IFCFG = """DEVICE=em1
ONBOOT=yes
HOTPLUG=no
"""

_NO_IP = _BASE_IFCFG + "BOOTPROTO=none\n"

_V4_IFCFG = _BASE_IFCFG + """BOOTPROTO=static
IPADDR=192.168.1.2
NETMASK=255.255.255.0
"""

_V4_IFCFG_MAPPED = _V4_IFCFG.replace('em1', 'nic1') + "HWADDR=a1:b2:c3:d4:e5\n"

_V6_IFCFG = _BASE_IFCFG + """IPV6INIT=yes
IPV6_AUTOCONF=no
IPV6ADDR=2001:abc:a::
"""

_OVS_IFCFG = _BASE_IFCFG + "DEVICETYPE=ovs\nBOOTPROTO=none\n"


_OVS_BRIDGE_IFCFG = _BASE_IFCFG + "DEVICETYPE=ovs\n"


_ROUTES = """default via 192.168.1.1 dev em1
172.19.0.0/24 via 192.168.1.1 dev em1
"""

_OVS_INTERFACE = _BASE_IFCFG + """DEVICETYPE=ovs
TYPE=OVSPort
OVS_BRIDGE=br-ctlplane
BOOTPROTO=none
"""

_OVS_BRIDGE_DHCP = """DEVICE=br-ctlplane
ONBOOT=yes
HOTPLUG=no
DEVICETYPE=ovs
TYPE=OVSBridge
OVSBOOTPROTO=dhcp
OVSDHCPINTERFACES="em1"
"""

_OVS_BRIDGE_DHCP_PRIMARY_INTERFACE = _OVS_BRIDGE_DHCP + \
    "OVS_EXTRA=\"set bridge br-ctlplane other-config:hwaddr=a1:b2:c3:d4:e5\"\n"


_OVS_BRIDGE_DHCP_OVS_EXTRA = _OVS_BRIDGE_DHCP + \
    "OVS_EXTRA=\"set bridge br-ctlplane other-config:hwaddr=a1:b2:c3:d4:e5" + \
    " -- br-set-external-id br-ctlplane bridge-id br-ctlplane\"\n"


_BASE_VLAN = """DEVICE=vlan5
ONBOOT=yes
HOTPLUG=no
VLAN=yes
PHYSDEV=em1
"""


_VLAN_NO_IP = _BASE_VLAN + "BOOTPROTO=none\n"


_VLAN_OVS = _BASE_VLAN + "DEVICETYPE=ovs\nBOOTPROTO=none\n"


_VLAN_OVS_BRIDGE = _BASE_VLAN + """DEVICETYPE=ovs
TYPE=OVSIntPort
OVS_BRIDGE=br-ctlplane
OVS_OPTIONS="tag=5"
BOOTPROTO=none
"""


_OVS_BOND_DHCP = """DEVICE=bond0
ONBOOT=yes
HOTPLUG=no
DEVICETYPE=ovs
TYPE=OVSBond
OVSBOOTPROTO=dhcp
BOND_IFACES="em1 em2"
"""


class TestIfcfgNetConfig(base.TestCase):

    def setUp(self):
        super(TestIfcfgNetConfig, self).setUp()

        self.provider = impl_ifcfg.IfcfgNetConfig()

    def tearDown(self):
        super(TestIfcfgNetConfig, self).tearDown()

    def get_interface_config(self, name='em1'):
        return self.provider.interface_data[name]

    def get_route_config(self, name='em1'):
        return self.provider.route_data.get(name, '')

    def test_add_base_interface(self):
        interface = objects.Interface('em1')
        self.provider.add_interface(interface)
        self.assertEqual(_NO_IP, self.get_interface_config())

    def test_add_ovs_interface(self):
        interface = objects.Interface('em1')
        interface.ovs_port = True
        self.provider.add_interface(interface)
        self.assertEqual(_OVS_IFCFG, self.get_interface_config())

    def test_add_interface_with_v4(self):
        v4_addr = objects.Address('192.168.1.2/24')
        interface = objects.Interface('em1', addresses=[v4_addr])
        self.provider.add_interface(interface)
        self.assertEqual(_V4_IFCFG, self.get_interface_config())
        self.assertEqual('', self.get_route_config())

    def test_add_interface_map_persisted(self):
        def test_interface_mac(name):
            macs = {'em1': 'a1:b2:c3:d4:e5'}
            return macs[name]
        self.stubs.Set(utils, 'interface_mac', test_interface_mac)

        nic_mapping = {'nic1': 'em1'}
        self.stubbed_numbered_nics = nic_mapping
        v4_addr = objects.Address('192.168.1.2/24')
        interface = objects.Interface('nic1', addresses=[v4_addr],
                                      nic_mapping=nic_mapping,
                                      persist_mapping=True)
        self.assertEqual('a1:b2:c3:d4:e5', interface.hwaddr)
        self.provider.add_interface(interface)
        self.assertEqual(_V4_IFCFG_MAPPED, self.get_interface_config('nic1'))
        self.assertEqual('', self.get_route_config('nic1'))

    def test_add_interface_with_v6(self):
        v6_addr = objects.Address('2001:abc:a::/64')
        interface = objects.Interface('em1', addresses=[v6_addr])
        self.provider.add_interface(interface)
        self.assertEqual(_V6_IFCFG, self.get_interface_config())

    def test_network_with_routes(self):
        route1 = objects.Route('192.168.1.1', default=True)
        route2 = objects.Route('192.168.1.1', '172.19.0.0/24')
        v4_addr = objects.Address('192.168.1.2/24')
        interface = objects.Interface('em1', addresses=[v4_addr],
                                      routes=[route1, route2])
        self.provider.add_interface(interface)
        self.assertEqual(_V4_IFCFG, self.get_interface_config())
        self.assertEqual(_ROUTES, self.get_route_config())

    def test_network_ovs_bridge_with_dhcp(self):
        interface = objects.Interface('em1')
        bridge = objects.OvsBridge('br-ctlplane', use_dhcp=True,
                                   members=[interface])
        self.provider.add_interface(interface)
        self.provider.add_bridge(bridge)
        self.assertEqual(_OVS_INTERFACE, self.get_interface_config())
        self.assertEqual(_OVS_BRIDGE_DHCP,
                         self.provider.bridge_data['br-ctlplane'])

    def test_network_ovs_bridge_with_dhcp_primary_interface(self):
        def test_interface_mac(name):
            return "a1:b2:c3:d4:e5"
        self.stubs.Set(utils, 'interface_mac', test_interface_mac)

        interface = objects.Interface('em1', primary=True)
        bridge = objects.OvsBridge('br-ctlplane', use_dhcp=True,
                                   members=[interface])
        self.provider.add_interface(interface)
        self.provider.add_bridge(bridge)
        self.assertEqual(_OVS_INTERFACE, self.get_interface_config())
        self.assertEqual(_OVS_BRIDGE_DHCP_PRIMARY_INTERFACE,
                         self.provider.bridge_data['br-ctlplane'])

    def test_network_ovs_bridge_with_dhcp_primary_interface_with_extra(self):
        def test_interface_mac(name):
            return "a1:b2:c3:d4:e5"
        self.stubs.Set(utils, 'interface_mac', test_interface_mac)

        interface = objects.Interface('em1', primary=True)
        ovs_extra = "br-set-external-id br-ctlplane bridge-id br-ctlplane"
        bridge = objects.OvsBridge('br-ctlplane', use_dhcp=True,
                                   members=[interface],
                                   ovs_extra=[ovs_extra])
        self.provider.add_interface(interface)
        self.provider.add_bridge(bridge)
        self.assertEqual(_OVS_INTERFACE, self.get_interface_config())
        self.assertEqual(_OVS_BRIDGE_DHCP_OVS_EXTRA,
                         self.provider.bridge_data['br-ctlplane'])

    def test_add_vlan(self):
        vlan = objects.Vlan('em1', 5)
        self.provider.add_vlan(vlan)
        self.assertEqual(_VLAN_NO_IP, self.get_interface_config('vlan5'))

    def test_add_vlan_ovs(self):
        vlan = objects.Vlan('em1', 5)
        vlan.ovs_port = True
        self.provider.add_vlan(vlan)
        self.assertEqual(_VLAN_OVS, self.get_interface_config('vlan5'))

    def test_add_ovs_bridge_with_vlan(self):
        vlan = objects.Vlan('em1', 5)
        bridge = objects.OvsBridge('br-ctlplane', use_dhcp=True,
                                   members=[vlan])
        self.provider.add_vlan(vlan)
        self.provider.add_bridge(bridge)
        self.assertEqual(_VLAN_OVS_BRIDGE, self.get_interface_config('vlan5'))

    def test_ovs_bond(self):
        interface1 = objects.Interface('em1')
        interface2 = objects.Interface('em2')
        bond = objects.OvsBond('bond0', use_dhcp=True,
                               members=[interface1, interface2])
        self.provider.add_interface(interface1)
        self.provider.add_interface(interface2)
        self.provider.add_bond(bond)
        self.assertEqual(_NO_IP, self.get_interface_config('em1'))

        em2_config = """DEVICE=em2
ONBOOT=yes
HOTPLUG=no
BOOTPROTO=none
"""
        self.assertEqual(em2_config, self.get_interface_config('em2'))
        self.assertEqual(_OVS_BOND_DHCP,
                         self.get_interface_config('bond0'))


class TestIfcfgNetConfigApply(base.TestCase):

    def setUp(self):
        super(TestIfcfgNetConfigApply, self).setUp()
        self.temp_ifcfg_file = tempfile.NamedTemporaryFile()
        self.temp_route_file = tempfile.NamedTemporaryFile()
        self.temp_bridge_file = tempfile.NamedTemporaryFile()
        self.temp_cleanup_file = tempfile.NamedTemporaryFile(delete=False)
        self.ifup_interface_names = []

        def test_ifcfg_path(name):
            return self.temp_ifcfg_file.name
        self.stubs.Set(impl_ifcfg, 'ifcfg_config_path', test_ifcfg_path)

        def test_routes_path(name):
            return self.temp_route_file.name
        self.stubs.Set(impl_ifcfg, 'route_config_path', test_routes_path)

        def test_bridge_path(name):
            return self.temp_bridge_file.name
        self.stubs.Set(impl_ifcfg, 'bridge_config_path', test_bridge_path)

        def test_cleanup_pattern():
            return self.temp_cleanup_file.name
        self.stubs.Set(impl_ifcfg, 'cleanup_pattern', test_cleanup_pattern)

        def test_execute(*args, **kwargs):
            if args[0] == '/sbin/ifup':
                self.ifup_interface_names.append(args[1])
            pass
        self.stubs.Set(processutils, 'execute', test_execute)

        self.provider = impl_ifcfg.IfcfgNetConfig()

    def tearDown(self):
        self.temp_ifcfg_file.close()
        self.temp_route_file.close()
        self.temp_bridge_file.close()
        if os.path.exists(self.temp_cleanup_file.name):
            self.temp_cleanup_file.close()
        super(TestIfcfgNetConfigApply, self).tearDown()

    def test_network_apply(self):
        route1 = objects.Route('192.168.1.1', default=True)
        route2 = objects.Route('192.168.1.1', '172.19.0.0/24')
        v4_addr = objects.Address('192.168.1.2/24')
        interface = objects.Interface('em1', addresses=[v4_addr],
                                      routes=[route1, route2])
        self.provider.add_interface(interface)

        self.provider.apply()

        ifcfg_data = utils.get_file_data(self.temp_ifcfg_file.name)
        self.assertEqual(_V4_IFCFG, ifcfg_data)
        route_data = utils.get_file_data(self.temp_route_file.name)
        self.assertEqual(_ROUTES, route_data)

    def test_dhcp_ovs_bridge_network_apply(self):
        interface = objects.Interface('em1')
        bridge = objects.OvsBridge('br-ctlplane', use_dhcp=True,
                                   members=[interface])
        self.provider.add_interface(interface)
        self.provider.add_bridge(bridge)
        self.provider.apply()

        ifcfg_data = utils.get_file_data(self.temp_ifcfg_file.name)
        self.assertEqual(_OVS_INTERFACE, ifcfg_data)
        bridge_data = utils.get_file_data(self.temp_bridge_file.name)
        self.assertEqual(_OVS_BRIDGE_DHCP, bridge_data)
        route_data = utils.get_file_data(self.temp_route_file.name)
        self.assertEqual("", route_data)

    def test_apply_noactivate(self):
        interface = objects.Interface('em1')
        bridge = objects.OvsBridge('br-ctlplane', use_dhcp=True,
                                   members=[interface])
        self.provider.add_interface(interface)
        self.provider.add_bridge(bridge)
        self.provider.apply(activate=False)
        self.assertEqual([], self.ifup_interface_names)

    def test_restart_children_on_change(self):
        # setup and apply a bridge
        interface = objects.Interface('em1')
        bridge = objects.OvsBridge('br-ctlplane', use_dhcp=True,
                                   members=[interface])
        self.provider.add_interface(interface)
        self.provider.add_bridge(bridge)
        self.provider.apply()
        self.assertIn('em1', self.ifup_interface_names)
        self.assertIn('br-ctlplane', self.ifup_interface_names)

        # changing the bridge should restart the interface too
        self.ifup_interface_names = []
        bridge = objects.OvsBridge('br-ctlplane', use_dhcp=False,
                                   members=[interface])
        self.provider.add_interface(interface)
        self.provider.add_bridge(bridge)
        self.provider.apply()

        # setup and apply a bond on a bridge
        self.ifup_interface_names = []
        interface1 = objects.Interface('em1')
        interface2 = objects.Interface('em2')
        bond = objects.OvsBond('bond0',
                               members=[interface1, interface2])
        bridge = objects.OvsBridge('br-ctlplane', use_dhcp=True,
                                   members=[bond])
        self.provider.add_interface(interface1)
        self.provider.add_interface(interface2)
        self.provider.add_bond(bond)
        self.provider.add_bridge(bridge)
        self.provider.apply()

        # changing the bridge should restart everything
        self.ifup_interface_names = []
        bridge = objects.OvsBridge('br-ctlplane', use_dhcp=False,
                                   members=[bond])
        self.provider.add_interface(interface1)
        self.provider.add_interface(interface2)
        self.provider.add_bond(bond)
        self.provider.add_bridge(bridge)
        self.provider.apply()
        self.assertIn('br-ctlplane', self.ifup_interface_names)
        self.assertIn('bond0', self.ifup_interface_names)
        self.assertIn('em1', self.ifup_interface_names)
        self.assertIn('em2', self.ifup_interface_names)

    def test_vlan_apply(self):
        vlan = objects.Vlan('em1', 5)
        self.provider.add_vlan(vlan)
        self.provider.apply()

        ifcfg_data = utils.get_file_data(self.temp_ifcfg_file.name)
        self.assertEqual(_VLAN_NO_IP, ifcfg_data)

    def test_cleanup(self):
        self.provider.apply(cleanup=True)
        self.assertTrue(not os.path.exists(self.temp_cleanup_file.name))

    def test_cleanup_not_loopback(self):
        tmp_lo_file = '%s-lo' % self.temp_cleanup_file.name
        utils.write_config(tmp_lo_file, 'foo')

        def test_cleanup_pattern():
            return '%s-*' % self.temp_cleanup_file.name
        self.stubs.Set(impl_ifcfg, 'cleanup_pattern', test_cleanup_pattern)

        self.provider.apply(cleanup=True)
        self.assertTrue(os.path.exists(tmp_lo_file))
        os.remove(tmp_lo_file)

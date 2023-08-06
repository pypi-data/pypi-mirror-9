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

import glob
import logging

import os_net_config
from os_net_config import objects
from os_net_config import utils


logger = logging.getLogger(__name__)


def ifcfg_config_path(name):
    return "/etc/sysconfig/network-scripts/ifcfg-%s" % name


#NOTE(dprince): added here for testability
def bridge_config_path(name):
    return ifcfg_config_path(name)


def route_config_path(name):
    return "/etc/sysconfig/network-scripts/route-%s" % name


def cleanup_pattern():
    return "/etc/sysconfig/network-scripts/ifcfg-*"


class IfcfgNetConfig(os_net_config.NetConfig):
    """Configure network interfaces using the ifcfg format."""

    def __init__(self, noop=False):
        super(IfcfgNetConfig, self).__init__(noop)
        self.interface_data = {}
        self.route_data = {}
        self.bridge_data = {}
        self.member_names = {}
        self.renamed_interfaces = {}
        logger.info('Ifcfg net config provider created.')

    def child_members(self, name):
        children = set()
        try:
            for member in self.member_names[name]:
                children.add(member)
                children.update(self.child_members(member))
        except KeyError:
            children.add(name)
        return children

    def _add_common(self, base_opt):

        ovs_extra = []

        data = "DEVICE=%s\n" % base_opt.name
        data += "ONBOOT=yes\n"
        data += "HOTPLUG=no\n"
        if isinstance(base_opt, objects.Vlan):
            data += "VLAN=yes\n"
            if base_opt.device:
                data += "PHYSDEV=%s\n" % base_opt.device
        if base_opt.ovs_port:
            data += "DEVICETYPE=ovs\n"
            if base_opt.bridge_name:
                if isinstance(base_opt, objects.Vlan):
                    data += "TYPE=OVSIntPort\n"
                    data += "OVS_BRIDGE=%s\n" % base_opt.bridge_name
                    data += "OVS_OPTIONS=\"tag=%s\"\n" % base_opt.vlan_id
                else:
                    data += "TYPE=OVSPort\n"
                    data += "OVS_BRIDGE=%s\n" % base_opt.bridge_name
        if isinstance(base_opt, objects.OvsBridge):
            data += "DEVICETYPE=ovs\n"
            data += "TYPE=OVSBridge\n"
            if base_opt.use_dhcp:
                data += "OVSBOOTPROTO=dhcp\n"
            if base_opt.members:
                members = [member.name for member in base_opt.members]
                self.member_names[base_opt.name] = members
                data += ("OVSDHCPINTERFACES=\"%s\"\n" % " ".join(members))
            if base_opt.primary_interface_name:
                mac = utils.interface_mac(base_opt.primary_interface_name)
                ovs_extra.append("set bridge %s other-config:hwaddr=%s" %
                                 (base_opt.name, mac))
            if base_opt.ovs_options:
                data += "OVS_OPTIONS=\"%s\"\n" % base_opt.ovs_options
            ovs_extra.extend(base_opt.ovs_extra)
        elif isinstance(base_opt, objects.OvsBond):
            data += "DEVICETYPE=ovs\n"
            data += "TYPE=OVSBond\n"
            if base_opt.use_dhcp:
                data += "OVSBOOTPROTO=dhcp\n"
            if base_opt.members:
                members = [member.name for member in base_opt.members]
                self.member_names[base_opt.name] = members
                data += ("BOND_IFACES=\"%s\"\n" % " ".join(members))
            if base_opt.ovs_options:
                data += "OVS_OPTIONS=\"%s\"\n" % base_opt.ovs_options
            ovs_extra.extend(base_opt.ovs_extra)
        else:
            if base_opt.use_dhcp:
                data += "BOOTPROTO=dhcp\n"
            elif not base_opt.addresses:
                data += "BOOTPROTO=none\n"
        if base_opt.mtu != 1500:
            data += "MTU=%i\n" % base_opt.mtu
        if base_opt.use_dhcpv6 or base_opt.v6_addresses():
            data += "IPV6INIT=yes\n"
            if base_opt.mtu != 1500:
                data += "IPV6_MTU=%i\n" % base_opt.mtu
        if base_opt.use_dhcpv6:
            data += "DHCPV6C=yes\n"
        elif base_opt.addresses:
            #TODO(dprince): Do we want to support multiple addresses?
            v4_addresses = base_opt.v4_addresses()
            if v4_addresses:
                first_v4 = v4_addresses[0]
                data += "BOOTPROTO=static\n"
                data += "IPADDR=%s\n" % first_v4.ip
                data += "NETMASK=%s\n" % first_v4.netmask

            v6_addresses = base_opt.v6_addresses()
            if v6_addresses:
                first_v6 = v6_addresses[0]
                data += "IPV6_AUTOCONF=no\n"
                data += "IPV6ADDR=%s\n" % first_v6.ip
        if base_opt.hwaddr:
            data += "HWADDR=%s\n" % base_opt.hwaddr
        if ovs_extra:
            data += "OVS_EXTRA=\"%s\"\n" % " -- ".join(ovs_extra)
        return data

    def _add_routes(self, interface_name, routes=[]):
        logger.info('adding custom route for interface: %s' % interface_name)
        data = ""
        first_line = ""
        for route in routes:
            if route.default:
                first_line = "default via %s dev %s\n" % (route.next_hop,
                                                          interface_name)
            else:
                data += "%s via %s dev %s\n" % (route.ip_netmask,
                                                route.next_hop,
                                                interface_name)
        self.route_data[interface_name] = first_line + data
        logger.debug('route data: %s' % self.route_data[interface_name])

    def add_interface(self, interface):
        """Add an Interface object to the net config object.

        :param interface: The Interface object to add.
        """
        logger.info('adding interface: %s' % interface.name)
        data = self._add_common(interface)
        logger.debug('interface data: %s' % data)
        self.interface_data[interface.name] = data
        if interface.routes:
            self._add_routes(interface.name, interface.routes)

        if interface.renamed:
            logger.info("Interface %s being renamed to %s"
                        % (interface.hwname, interface.name))
            self.renamed_interfaces[interface.hwname] = interface.name

    def add_vlan(self, vlan):
        """Add a Vlan object to the net config object.

        :param vlan: The vlan object to add.
        """
        logger.info('adding vlan: %s' % vlan.name)
        data = self._add_common(vlan)
        logger.debug('vlan data: %s' % data)
        self.interface_data[vlan.name] = data
        if vlan.routes:
            self._add_routes(vlan.name, vlan.routes)

    def add_bridge(self, bridge):
        """Add an OvsBridge object to the net config object.

        :param bridge: The OvsBridge object to add.
        """
        logger.info('adding bridge: %s' % bridge.name)
        data = self._add_common(bridge)
        logger.debug('bridge data: %s' % data)
        self.bridge_data[bridge.name] = data
        if bridge.routes:
            self._add_routes(bridge.name, bridge.routes)

    def add_bond(self, bond):
        """Add an OvsBond object to the net config object.

        :param bridge: The OvsBond object to add.
        """
        logger.info('adding bond: %s' % bond.name)
        data = self._add_common(bond)
        logger.debug('bond data: %s' % data)
        self.interface_data[bond.name] = data
        if bond.routes:
            self._add_routes(bond.name, bond.routes)

    def apply(self, cleanup=False, activate=True):
        """Apply the network configuration.

        :param cleanup: A boolean which indicates whether any undefined
            (existing but not present in the object model) interface
            should be disabled and deleted.
        :param activate: A boolean which indicates if the config should
            be activated by stopping/starting interfaces
            NOTE: if cleanup is specified we will deactivate interfaces even
            if activate is false
        :returns: a dict of the format: filename/data which contains info
            for each file that was changed (or would be changed if in --noop
            mode).
        Note the noop mode is set via the constructor noop boolean
        """
        logger.info('applying network configs...')
        restart_interfaces = []
        restart_bridges = []
        update_files = {}
        all_file_names = []

        for interface_name, iface_data in self.interface_data.iteritems():
            route_data = self.route_data.get(interface_name, '')
            interface_path = ifcfg_config_path(interface_name)
            route_path = route_config_path(interface_name)
            all_file_names.append(interface_path)
            all_file_names.append(route_path)
            if (utils.diff(interface_path, iface_data) or
                utils.diff(route_path, route_data)):
                restart_interfaces.append(interface_name)
                restart_interfaces.extend(self.child_members(interface_name))
                update_files[interface_path] = iface_data
                update_files[route_path] = route_data
                logger.info('No changes required for interface: %s' %
                            interface_name)

        for bridge_name, bridge_data in self.bridge_data.iteritems():
            route_data = self.route_data.get(bridge_name, '')
            bridge_path = bridge_config_path(bridge_name)
            bridge_route_path = route_config_path(bridge_name)
            all_file_names.append(bridge_path)
            all_file_names.append(bridge_route_path)
            if (utils.diff(bridge_path, bridge_data) or
                utils.diff(bridge_route_path, route_data)):
                restart_bridges.append(bridge_name)
                restart_interfaces.extend(self.child_members(bridge_name))
                update_files[bridge_path] = bridge_data
                update_files[bridge_route_path] = route_data
                logger.info('No changes required for bridge: %s' % bridge_name)

        if cleanup:
            for ifcfg_file in glob.iglob(cleanup_pattern()):
                if ifcfg_file not in all_file_names:
                    interface_name = ifcfg_file[len(cleanup_pattern()) - 1:]
                    if interface_name != 'lo':
                        logger.info('cleaning up interface: %s'
                                    % interface_name)
                        self.ifdown(interface_name)
                        self.remove_config(ifcfg_file)

        if activate:
            for interface in restart_interfaces:
                self.ifdown(interface)

            for bridge in restart_bridges:
                self.ifdown(bridge, iftype='bridge')

            for oldname, newname in self.renamed_interfaces.iteritems():
                self.ifrename(oldname, newname)

        for location, data in update_files.iteritems():
            self.write_config(location, data)

        if activate:
            for bridge in restart_bridges:
                self.ifup(bridge, iftype='bridge')

            for interface in restart_interfaces:
                self.ifup(interface)

        return update_files

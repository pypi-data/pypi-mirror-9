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

import logging
import netaddr
from oslo_utils import strutils

from os_net_config import utils


logger = logging.getLogger(__name__)

_NUMBERED_NICS = None


class InvalidConfigException(ValueError):
    pass


def object_from_json(json):
    obj_type = json.get("type")
    if obj_type == "interface":
        return Interface.from_json(json)
    elif obj_type == "vlan":
        return Vlan.from_json(json)
    elif obj_type == "ovs_bridge":
        return OvsBridge.from_json(json)
    elif obj_type == "ovs_bond":
        return OvsBond.from_json(json)


def _get_required_field(json, name, object_name):
    field = json.get(name)
    if not field:
        msg = '%s JSON objects require \'%s\' to be configured.' \
              % (object_name, name)
        raise InvalidConfigException(msg)
    return field


def _numbered_nics(nic_mapping=None):
    mapping = nic_mapping or {}
    global _NUMBERED_NICS
    if _NUMBERED_NICS:
        return _NUMBERED_NICS
    _NUMBERED_NICS = {}
    count = 0
    active_nics = utils.ordered_active_nics()
    for nic in active_nics:
        count += 1
        nic_alias = "nic%i" % count
        nic_mapped = mapping.get(nic_alias, nic)

        # The mapping is either invalid, or specifies a mac
        if nic_mapped not in active_nics:
            for active in active_nics:
                try:
                    active_mac = utils.interface_mac(active)
                except IOError:
                    continue
                if nic_mapped == active_mac:
                    logger.debug("%s matches device %s" % (nic_mapped, active))
                    nic_mapped = active
                    break
            else:
                # The mapping can't specify a non-active or non-existent nic
                logger.warning('interface %s is not in an active nic (%s)'
                               % (nic_mapped, ', '.join(active_nics)))
                continue

        # Duplicate mappings are not allowed
        if nic_mapped in _NUMBERED_NICS.values():
            msg = ('interface %s already mapped, '
                   'check mapping file for duplicates'
                   % nic_mapped)
            raise InvalidConfigException(msg)

        _NUMBERED_NICS[nic_alias] = nic_mapped
        logger.info("%s mapped to: %s" % (nic_alias, nic_mapped))
    return _NUMBERED_NICS


class Route(object):
    """Base class for network routes."""

    def __init__(self, next_hop, ip_netmask="", default=False):
        self.next_hop = next_hop
        self.ip_netmask = ip_netmask
        self.default = default

    @staticmethod
    def from_json(json):
        next_hop = _get_required_field(json, 'next_hop', 'Route')
        ip_netmask = json.get('ip_netmask', "")
        default = strutils.bool_from_string(str(json.get('default', False)))
        return Route(next_hop, ip_netmask, default)


class Address(object):
    """Base class for network addresses."""

    def __init__(self, ip_netmask):
        self.ip_netmask = ip_netmask
        ip_nw = netaddr.IPNetwork(self.ip_netmask)
        self.ip = str(ip_nw.ip)
        self.netmask = str(ip_nw.netmask)
        self.version = ip_nw.version

    @staticmethod
    def from_json(json):
        ip_netmask = _get_required_field(json, 'ip_netmask', 'Address')
        return Address(ip_netmask)


class _BaseOpts(object):
    """Base abstraction for logical port options."""

    def __init__(self, name, use_dhcp=False, use_dhcpv6=False, addresses=[],
                 routes=[], mtu=1500, primary=False, nic_mapping=None,
                 persist_mapping=False):
        numbered_nic_names = _numbered_nics(nic_mapping)
        self.hwaddr = None
        self.hwname = None
        self.renamed = False
        if name in numbered_nic_names:
            if persist_mapping:
                self.name = name
                self.hwname = numbered_nic_names[name]
                self.hwaddr = utils.interface_mac(self.hwname)
                self.renamed = True
            else:
                self.name = numbered_nic_names[name]
        else:
            self.name = name

        self.mtu = mtu
        self.use_dhcp = use_dhcp
        self.use_dhcpv6 = use_dhcpv6
        self.addresses = addresses
        self.routes = routes
        self.primary = primary
        self.bridge_name = None  # internal
        self.ovs_port = False  # internal
        self.primary_interface_name = None  # internal

    def v4_addresses(self):
        v4_addresses = []
        for addr in self.addresses:
            if addr.version == 4:
                v4_addresses.append(addr)

        return v4_addresses

    def v6_addresses(self):
        v6_addresses = []
        for addr in self.addresses:
            if addr.version == 6:
                v6_addresses.append(addr)

        return v6_addresses

    @staticmethod
    def base_opts_from_json(json, include_primary=True):
        use_dhcp = strutils.bool_from_string(str(json.get('use_dhcp', False)))
        use_dhcpv6 = strutils.bool_from_string(str(json.get('use_dhcpv6',
                                               False)))
        mtu = json.get('mtu', 1500)
        primary = strutils.bool_from_string(str(json.get('primary', False)))
        addresses = []
        routes = []

        # addresses
        addresses_json = json.get('addresses')
        if addresses_json:
            if isinstance(addresses_json, list):
                for address in addresses_json:
                    addresses.append(Address.from_json(address))
            else:
                msg = 'Addresses must be a list.'
                raise InvalidConfigException(msg)

        # routes
        routes_json = json.get('routes')
        if routes_json:
            if isinstance(routes_json, list):
                for route in routes_json:
                    routes.append(Route.from_json(route))
            else:
                msg = 'Routes must be a list.'
                raise InvalidConfigException(msg)

        nic_mapping = json.get('nic_mapping')
        persist_mapping = json.get('persist_mapping')

        if include_primary:
            return (use_dhcp, use_dhcpv6, addresses, routes, mtu, primary,
                    nic_mapping, persist_mapping)
        else:
            return (use_dhcp, use_dhcpv6, addresses, routes, mtu,
                    nic_mapping, persist_mapping)


class Interface(_BaseOpts):
    """Base class for network interfaces."""

    def __init__(self, name, use_dhcp=False, use_dhcpv6=False, addresses=[],
                 routes=[], mtu=1500, primary=False, nic_mapping=None,
                 persist_mapping=False):
        super(Interface, self).__init__(name, use_dhcp, use_dhcpv6, addresses,
                                        routes, mtu, primary, nic_mapping,
                                        persist_mapping)

    @staticmethod
    def from_json(json):
        name = _get_required_field(json, 'name', 'Interface')
        opts = _BaseOpts.base_opts_from_json(json)
        return Interface(name, *opts)


class Vlan(_BaseOpts):
    """Base class for VLANs.

       NOTE: the name parameter must be formated w/ vlan<num> where <num>
       matches the vlan ID being used. Example: vlan5
    """

    def __init__(self, device, vlan_id, use_dhcp=False, use_dhcpv6=False,
                 addresses=[], routes=[], mtu=1500, primary=False,
                 nic_mapping=None, persist_mapping=False):
        name = 'vlan%i' % vlan_id
        super(Vlan, self).__init__(name, use_dhcp, use_dhcpv6, addresses,
                                   routes, mtu, primary, nic_mapping,
                                   persist_mapping)
        self.vlan_id = int(vlan_id)

        numbered_nic_names = _numbered_nics(nic_mapping)
        if device in numbered_nic_names:
            self.device = numbered_nic_names[device]
        else:
            self.device = device

    @staticmethod
    def from_json(json):
        # A vlan on an OVS bridge won't require a device (OVS Int Port)
        device = json.get('device')
        vlan_id = _get_required_field(json, 'vlan_id', 'Vlan')
        opts = _BaseOpts.base_opts_from_json(json)
        return Vlan(device, vlan_id, *opts)


class OvsBridge(_BaseOpts):
    """Base class for OVS bridges."""

    def __init__(self, name, use_dhcp=False, use_dhcpv6=False, addresses=[],
                 routes=[], mtu=1500, members=[], ovs_options=None,
                 ovs_extra=[], nic_mapping=None, persist_mapping=False):
        super(OvsBridge, self).__init__(name, use_dhcp, use_dhcpv6, addresses,
                                        routes, mtu, False, nic_mapping,
                                        persist_mapping)
        self.members = members
        self.ovs_options = ovs_options
        self.ovs_extra = ovs_extra
        for member in self.members:
            member.bridge_name = name
            member.ovs_port = True
            if member.primary:
                if self.primary_interface_name:
                    msg = 'Only one primary interface allowed per bridge.'
                    raise InvalidConfigException(msg)
                if member.primary_interface_name:
                    self.primary_interface_name = member.primary_interface_name
                else:
                    self.primary_interface_name = member.name

    @staticmethod
    def from_json(json):
        name = _get_required_field(json, 'name', 'OvsBridge')
        (use_dhcp, use_dhcpv6, addresses, routes, mtu, nic_mapping,
         persist_mapping) = _BaseOpts.base_opts_from_json(
             json, include_primary=False)
        ovs_options = json.get('ovs_options')
        ovs_extra = json.get('ovs_extra', [])
        members = []

        # members
        members_json = json.get('members')
        if members_json:
            if isinstance(members_json, list):
                for member in members_json:
                    members.append(object_from_json(member))
            else:
                msg = 'Members must be a list.'
                raise InvalidConfigException(msg)

        return OvsBridge(name, use_dhcp=use_dhcp, use_dhcpv6=use_dhcpv6,
                         addresses=addresses, routes=routes, mtu=mtu,
                         members=members, ovs_options=ovs_options,
                         ovs_extra=ovs_extra, nic_mapping=nic_mapping,
                         persist_mapping=persist_mapping)


class OvsBond(_BaseOpts):
    """Base class for OVS bonds."""

    def __init__(self, name, use_dhcp=False, use_dhcpv6=False, addresses=[],
                 routes=[], mtu=1500, primary=False, members=[],
                 ovs_options=None, ovs_extra=[], nic_mapping=None,
                 persist_mapping=False):
        super(OvsBond, self).__init__(name, use_dhcp, use_dhcpv6, addresses,
                                      routes, mtu, primary, nic_mapping,
                                      persist_mapping)
        self.members = members
        self.ovs_options = ovs_options
        self.ovs_extra = ovs_extra
        for member in self.members:
            if member.primary:
                if self.primary_interface_name:
                    msg = 'Only one primary interface allowed per bond.'
                    raise InvalidConfigException(msg)
                if member.primary_interface_name:
                    self.primary_interface_name = member.primary_interface_name
                else:
                    self.primary_interface_name = member.name

    @staticmethod
    def from_json(json):
        name = _get_required_field(json, 'name', 'OvsBond')
        (use_dhcp, use_dhcpv6, addresses, routes, mtu, nic_mapping,
         persist_mapping) = _BaseOpts.base_opts_from_json(
             json, include_primary=False)
        ovs_options = json.get('ovs_options')
        ovs_extra = json.get('ovs_extra', [])
        members = []

        # members
        members_json = json.get('members')
        if members_json:
            if isinstance(members_json, list):
                for member in members_json:
                    members.append(object_from_json(member))
            else:
                msg = 'Members must be a list.'
                raise InvalidConfigException(msg)

        return OvsBond(name, use_dhcp=use_dhcp, use_dhcpv6=use_dhcpv6,
                       addresses=addresses, routes=routes, mtu=mtu,
                       members=members, ovs_options=ovs_options,
                       ovs_extra=ovs_extra, nic_mapping=nic_mapping,
                       persist_mapping=persist_mapping)

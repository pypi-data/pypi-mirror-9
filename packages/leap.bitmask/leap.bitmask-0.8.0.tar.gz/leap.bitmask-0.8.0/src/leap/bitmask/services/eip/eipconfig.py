# -*- coding: utf-8 -*-
# eipconfig.py
# Copyright (C) 2013 LEAP
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
Provider configuration
"""
import logging
import os
import re
import time

import ipaddr

from leap.bitmask.config import flags
from leap.bitmask.config.providerconfig import ProviderConfig
from leap.bitmask.services import ServiceConfig
from leap.bitmask.services.eip.eipspec import get_schema
from leap.bitmask.util import get_path_prefix
from leap.common.check import leap_assert, leap_assert_type

logger = logging.getLogger(__name__)


def get_eipconfig_path(domain, relative=True):
    """
    Returns relative or absolute path for EIP config.

    :param domain: the domain to which this eipconfig belongs to.
    :type domain: str
    :param relative: defines whether the path should be relative or absolute.
    :type relative: bool
    :returns: the path
    :rtype: str
    """
    leap_assert(domain is not None, "get_eipconfig_path: We need a domain")

    path = os.path.join("leap", "providers", domain, "eip-service.json")

    if not relative:
        path = os.path.join(get_path_prefix(), path)

    return path


def load_eipconfig_if_needed(provider_config, eip_config, domain):
    """
    Utility function to prime a eip_config object from a loaded
    provider_config and the chosen provider domain.

    :param provider_config: a loaded instance of ProviderConfig
    :type provider_config: ProviderConfig

    :param eip_config: the eipconfig object to be primed.
    :type eip_config: EIPConfig

    :param domain: the chosen provider domain
    :type domain: str

    :returns: Whether the eip_config object has been succesfully loaded
    :rtype: bool
    """
    loaded = eip_config.loaded()
    if not loaded:
        eip_config_path = get_eipconfig_path(domain)
        api_version = provider_config.get_api_version()
        eip_config.set_api_version(api_version)
        loaded = eip_config.load(eip_config_path)
    return loaded


class VPNGatewaySelector(object):
    """
    VPN Gateway selector.
    """
    # http://www.timeanddate.com/time/map/
    equivalent_timezones = {13: -11, 14: -10}

    def __init__(self, eipconfig, tz_offset=None):
        '''
        Constructor for VPNGatewaySelector.

        :param eipconfig: a valid EIP Configuration.
        :type eipconfig: EIPConfig
        :param tz_offset: use this offset as a local distance to GMT.
        :type tz_offset: int
        '''
        leap_assert_type(eipconfig, EIPConfig)

        self._local_offset = tz_offset
        if tz_offset is None:
            tz_offset = self._get_local_offset()

        if tz_offset in self.equivalent_timezones:
            tz_offset = self.equivalent_timezones[tz_offset]

        self._local_offset = tz_offset
        self._eipconfig = eipconfig

    def get_gateways_list(self):
        """
        Return the existing gateways, sorted by timezone proximity.

        :rtype: list of tuples (label, ip, country_code)
                (str, IPv4Address or IPv6Address object, str)
        """
        gateways_timezones = []
        locations = self._eipconfig.get_locations()
        if not locations:
            locations = {}
        gateways = self._eipconfig.get_gateways()

        for idx, gateway in enumerate(gateways):
            distance = 99  # if hasn't location -> should go last
            location = locations.get(gateway.get('location'))
            label = gateway.get('location', 'Unknown')
            country = 'XX'
            if location is not None:
                country = location.get('country_code', 'XX')
                label = location.get('name', label)
                timezone = location.get('timezone')
                if timezone is not None:
                    offset = int(timezone)
                    if offset in self.equivalent_timezones:
                        offset = self.equivalent_timezones[offset]
                    distance = self._get_timezone_distance(offset)

            ip = self._eipconfig.get_gateway_ip(idx)
            gateways_timezones.append((ip, distance, label, country))

        gateways_timezones = sorted(gateways_timezones, key=lambda gw: gw[1])

        result = []
        for ip, distance, label, country in gateways_timezones:
            result.append((label, ip, country))

        return result

    def get_gateways(self):
        """
        Return the 4 best gateways, sorted by timezone proximity.

        :rtype: list of IPv4Address or IPv6Address object.
        """
        gateways = [gateway[1] for gateway in self.get_gateways_list()][:4]
        return gateways

    def get_gateways_country_code(self):
        """
        Return a dict with ipaddress -> country code mapping.

        :rtype: dict
        """
        country_codes = {}

        locations = self._eipconfig.get_locations()
        gateways = self._eipconfig.get_gateways()

        for idx, gateway in enumerate(gateways):
            gateway_location = gateway.get('location')

            ip = self._eipconfig.get_gateway_ip(idx)
            if gateway_location is not None:
                ccode = locations[gateway['location']]['country_code']
                country_codes[ip] = ccode
        return country_codes

    def _get_timezone_distance(self, offset):
        '''
        Return the distance between the local timezone and
        the one with offset 'offset'.

        :param offset: the distance of a timezone to GMT.
        :type offset: int
        :returns: distance between local offset and param offset.
        :rtype: int
        '''
        timezones = range(-11, 13)
        tz1 = offset
        tz2 = self._local_offset
        distance = abs(timezones.index(tz1) - timezones.index(tz2))
        if distance > 12:
            if tz1 < 0:
                distance = timezones.index(tz1) + timezones[::-1].index(tz2)
            else:
                distance = timezones[::-1].index(tz1) + timezones.index(tz2)

        return distance

    def _get_local_offset(self):
        '''
        Return the distance between GMT and the local timezone.

        :rtype: int
        '''
        local_offset = time.timezone
        if time.daylight:
            local_offset = time.altzone

        return -local_offset / 3600


class EIPConfig(ServiceConfig):
    """
    Provider configuration abstraction class
    """
    _service_name = "eip"

    OPENVPN_ALLOWED_KEYS = ("auth", "cipher", "tls-cipher", "fragment")
    OPENVPN_CIPHERS_REGEX = re.compile("[A-Z0-9\-]+")

    def __init__(self):
        self.standalone = flags.STANDALONE
        ServiceConfig.__init__(self)
        self._api_version = None

    def _get_schema(self):
        """
        Returns the schema corresponding to the version given.

        :rtype: dict or None if the version is not supported.
        """
        return get_schema(self._api_version)

    def get_clusters(self):
        # TODO: create an abstraction for clusters
        return self._safe_get_value("clusters")

    def get_gateways(self):
        # TODO: create an abstraction for gateways
        return self._safe_get_value("gateways")

    def get_locations(self):
        '''
        Returns a list of locations

        :rtype: dict
        '''
        return self._safe_get_value("locations")

    def get_openvpn_configuration(self):
        """
        Returns a dictionary containing the openvpn configuration
        parameters.

        These are sanitized with alphanumeric whitelist.

        NOTE: some openvpn config option don't take a value, but
        this method currently requires that every option has a value.
        Also, this does not yet work with values with spaces, like
        `keepalive 10 30`

        :returns: openvpn configuration dict
        :rtype: C{dict}
        """
        ovpncfg = self._safe_get_value("openvpn_configuration")
        config = {}
        for key, value in ovpncfg.items():
            if key in self.OPENVPN_ALLOWED_KEYS and value is not None:
                sanitized_val = self.OPENVPN_CIPHERS_REGEX.findall(str(value))
                if len(sanitized_val) != 0:
                    _val = sanitized_val[0]
                    config[str(key)] = str(_val)
        return config

    def get_serial(self):
        return self._safe_get_value("serial")

    def get_version(self):
        return self._safe_get_value("version")

    def get_gateway_ip(self, index=0):
        """
        Returns the ip of the gateway.

        :rtype: An IPv4Address or IPv6Address object.
        """
        gateways = self.get_gateways()
        leap_assert(len(gateways) > 0, "We don't have any gateway!")
        if index > len(gateways):
            index = 0
            logger.warning("Provided an unknown gateway index %s, " +
                           "defaulting to 0")
        ip_addr_str = gateways[index]["ip_address"]

        try:
            ipaddr.IPAddress(ip_addr_str)
            return ip_addr_str
        except ValueError:
            logger.error("Invalid ip address in config: %s" % (ip_addr_str,))
            return None

    def get_client_cert_path(self,
                             providerconfig=None,
                             about_to_download=False):
        """
        Returns the path to the certificate used by openvpn
        """

        leap_assert(providerconfig, "We need a provider")
        leap_assert_type(providerconfig, ProviderConfig)

        cert_path = os.path.join(get_path_prefix(),
                                 "leap", "providers",
                                 providerconfig.get_domain(),
                                 "keys", "client", "openvpn.pem")

        if not about_to_download:
            leap_assert(os.path.exists(cert_path),
                        "You need to download the certificate first")
            logger.debug("Using OpenVPN cert %s" % (cert_path,))

        return cert_path


if __name__ == "__main__":
    logger = logging.getLogger(name='leap')
    logger.setLevel(logging.DEBUG)
    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        '%(asctime)s '
        '- %(name)s - %(levelname)s - %(message)s')
    console.setFormatter(formatter)
    logger.addHandler(console)

    eipconfig = EIPConfig()
    eipconfig.set_api_version('1')

    try:
        eipconfig.get_clusters()
    except Exception as e:
        assert isinstance(e, AssertionError), "Expected an assert"
        print "Safe value getting is working"

    if eipconfig.load("leap/providers/bitmask.net/eip-service.json"):
        print "EIPConfig methods"
        print eipconfig.get_clusters()
        print eipconfig.get_gateways()
        print eipconfig.get_locations()
        print eipconfig.get_openvpn_configuration()
        print eipconfig.get_serial()
        print eipconfig.get_version()
        print "VPNGatewaySelector methods"
        gws = VPNGatewaySelector(eipconfig)
        print gws.get_gateways()
        print gws.get_gateways_list()

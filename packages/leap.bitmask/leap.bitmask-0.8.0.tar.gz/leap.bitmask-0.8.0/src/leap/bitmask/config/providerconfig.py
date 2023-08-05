# -*- coding: utf-8 -*-
# providerconfig.py
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

from leap.bitmask import provider
from leap.bitmask.config import flags
from leap.bitmask.config.provider_spec import leap_provider_spec
from leap.bitmask.services import get_service_display_name
from leap.bitmask.util import get_path_prefix
from leap.common.check import leap_check
from leap.common.config.baseconfig import BaseConfig, LocalizedKey

logger = logging.getLogger(__name__)


class MissingCACert(Exception):
    """
    Raised when a CA certificate is needed but not found.
    """
    pass


class ProviderConfig(BaseConfig):
    """
    Provider configuration abstraction class
    """
    def __init__(self):
        self.standalone = flags.STANDALONE
        BaseConfig.__init__(self)

    def get_light_config(self, domain, lang=None):
        """
        Return a dict with the data for the loaded object.

        :param domain: the domain name of the provider.
        :type domain: str
        :param lang: the language to use for localized strings.
        :type lang: str

        :rtype: dict or None if the ProviderConfig isn't loaded.
        """
        config = self.get_provider_config(domain)

        if config is None:
            return

        details = {}
        details["domain"] = config.get_domain()
        details["name"] = config.get_name(lang=lang)
        details["description"] = config.get_description(lang=lang)
        details["enrollment_policy"] = config.get_enrollment_policy()
        details["services"] = config.get_services()

        services = []
        for service in config.get_services():
            services.append(get_service_display_name(service))

        details['services_string'] = ", ".join(services)

        return details

    @classmethod
    def get_provider_config(self, domain):
        """
        Helper to return a valid Provider Config from the domain name.

        :param domain: the domain name of the provider.
        :type domain: str

        :rtype: ProviderConfig or None if there is a problem loading the config
        """
        provider_config = ProviderConfig()
        if not provider_config.load(provider.get_provider_path(domain)):
            provider_config = None

        return provider_config

    def _get_schema(self):
        """
        Returns the schema corresponding to the version given.

        :rtype: dict or None if the version is not supported.
        """
        return leap_provider_spec

    def _get_spec(self):
        """
        Returns the spec object for the specific configuration.

        Override the BaseConfig one because we do not support multiple schemas
        for the provider yet.

        :rtype: dict or None if the version is not supported.
        """
        return self._get_schema()

    def get_api_uri(self):
        return self._safe_get_value("api_uri")

    def get_api_version(self):
        return self._safe_get_value("api_version")

    def get_ca_cert_fingerprint(self):
        return self._safe_get_value("ca_cert_fingerprint")

    def get_ca_cert_uri(self):
        return self._safe_get_value("ca_cert_uri")

    def get_default_language(self):
        return self._safe_get_value("default_language")

    @LocalizedKey
    def get_description(self):
        return self._safe_get_value("description")

    @classmethod
    def sanitize_path_component(cls, component):
        """
        If the provider tries to instrument the component of a path
        that is controlled by them, this will take care of
        removing/escaping all the necessary elements.

        :param component: Path component to process
        :type component: unicode or str

        :returns: The path component properly escaped
        :rtype: unicode or str
        """
        # TODO: Fix for windows, names like "aux" or "con" aren't
        # allowed.
        return component.replace(os.path.sep, "")

    def get_domain(self):
        return ProviderConfig.sanitize_path_component(
            self._safe_get_value("domain"))

    def get_enrollment_policy(self):
        """
        Returns the enrollment policy

        :rtype: string
        """
        return self._safe_get_value("enrollment_policy")

    def get_languages(self):
        return self._safe_get_value("languages")

    @LocalizedKey
    def get_name(self):
        return self._safe_get_value("name")

    def get_services(self):
        """
        Returns a list with the available services in the current provider.

        :rtype: list
        """
        services = self._safe_get_value("services")
        return services

    def get_ca_cert_path(self, about_to_download=False):
        """
        Returns the path to the certificate for the current provider.
        It may raise MissingCACert if
        the certificate does not exists and not about_to_download

        :param about_to_download: defines wether we want the path to
                                  download the cert or not. This helps avoid
                                  checking if the cert exists because we
                                  are about to write it.
        :type about_to_download: bool

        :rtype: unicode
        """

        cert_path = os.path.join(get_path_prefix(), "leap", "providers",
                                 self.get_domain(), "keys", "ca", "cacert.pem")

        if not about_to_download:
            cert_exists = os.path.exists(cert_path)
            error_msg = "You need to download the certificate first"
            leap_check(cert_exists, error_msg, MissingCACert)
            logger.debug("Going to verify SSL against %s" % (cert_path,))

        # OpenSSL does not handle unicode.
        return cert_path.encode('utf-8')

    def provides_eip(self):
        """
        Returns True if this particular provider has the EIP service,
        False otherwise.

        :rtype: bool
        """
        return "openvpn" in self.get_services()

    def provides_mx(self):
        """
        Returns True if this particular provider has the MX service,
        False otherwise.

        :rtype: bool
        """
        return "mx" in self.get_services()

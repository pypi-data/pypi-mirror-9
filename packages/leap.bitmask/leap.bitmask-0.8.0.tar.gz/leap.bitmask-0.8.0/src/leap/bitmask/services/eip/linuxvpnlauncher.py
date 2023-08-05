# -*- coding: utf-8 -*-
# linuxvpnlauncher.py
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
Linux VPN launcher implementation.
"""
import commands
import logging
import os
import sys

from leap.bitmask.config import flags
from leap.bitmask.util.privilege_policies import LinuxPolicyChecker
from leap.bitmask.util.privilege_policies import NoPolkitAuthAgentAvailable
from leap.bitmask.util.privilege_policies import NoPkexecAvailable
from leap.bitmask.services.eip.vpnlauncher import VPNLauncher
from leap.bitmask.services.eip.vpnlauncher import VPNLauncherException
from leap.bitmask.util import get_path_prefix, force_eval
from leap.bitmask.util import first

logger = logging.getLogger(__name__)

COM = commands


class EIPNoPolkitAuthAgentAvailable(VPNLauncherException):
    pass


class EIPNoPkexecAvailable(VPNLauncherException):
    pass


SYSTEM_CONFIG = "/etc/leap"
leapfile = lambda f: "%s/%s" % (SYSTEM_CONFIG, f)


class LinuxVPNLauncher(VPNLauncher):

    # The following classes depend on force_eval to be called against
    # the classes, to get the evaluation of the standalone flag on runtine.
    # If we keep extending this kind of classes, we should abstract the
    # handling of the STANDALONE flag in a base class

    class BITMASK_ROOT(object):
        def __call__(self):
            return ("/usr/local/sbin/bitmask-root" if flags.STANDALONE else
                    "/usr/sbin/bitmask-root")

    class OPENVPN_BIN_PATH(object):
        def __call__(self):
            return ("/usr/local/sbin/leap-openvpn" if flags.STANDALONE else
                    "/usr/sbin/openvpn")

    class POLKIT_PATH(object):
        def __call__(self):
            # LinuxPolicyChecker will give us the right path if standalone.
            return LinuxPolicyChecker.get_polkit_path()

    OTHER_FILES = (POLKIT_PATH, BITMASK_ROOT, OPENVPN_BIN_PATH)

    @classmethod
    def get_vpn_command(kls, eipconfig, providerconfig, socket_host,
                        socket_port="unix", openvpn_verb=1):
        """
        Returns the Linux implementation for the vpn launching command.

        Might raise:
            EIPNoPkexecAvailable,
            EIPNoPolkitAuthAgentAvailable,
            OpenVPNNotFoundException,
            VPNLauncherException.

        :param eipconfig: eip configuration object
        :type eipconfig: EIPConfig
        :param providerconfig: provider specific configuration
        :type providerconfig: ProviderConfig
        :param socket_host: either socket path (unix) or socket IP
        :type socket_host: str
        :param socket_port: either string "unix" if it's a unix socket,
                            or port otherwise
        :type socket_port: str
        :param openvpn_verb: the openvpn verbosity wanted
        :type openvpn_verb: int

        :return: A VPN command ready to be launched.
        :rtype: list
        """
        # we use `super` in order to send the class to use
        command = super(LinuxVPNLauncher, kls).get_vpn_command(
            eipconfig, providerconfig, socket_host, socket_port, openvpn_verb)

        command.insert(0, force_eval(kls.BITMASK_ROOT))
        command.insert(1, "openvpn")
        command.insert(2, "start")

        policyChecker = LinuxPolicyChecker()
        try:
            pkexec = policyChecker.maybe_pkexec()
        except NoPolkitAuthAgentAvailable:
            raise EIPNoPolkitAuthAgentAvailable()
        except NoPkexecAvailable:
            raise EIPNoPkexecAvailable()
        if pkexec:
            command.insert(0, first(pkexec))

        return command

    @classmethod
    def cmd_for_missing_scripts(kls, frompath):
        """
        Returns a sh script that can copy the missing files.

        :param frompath: The path where the helper files live
        :type frompath: str

        :rtype: str
        """
        bin_paths = force_eval(
            (LinuxVPNLauncher.POLKIT_PATH,
             LinuxVPNLauncher.OPENVPN_BIN_PATH,
             LinuxVPNLauncher.BITMASK_ROOT))

        polkit_path, openvpn_bin_path, bitmask_root = bin_paths

        # no system config for now
        # sys_config = kls.SYSTEM_CONFIG
        (polkit_file, openvpn_bin_file,
         bitmask_root_file) = map(
            lambda p: os.path.split(p)[-1],
            bin_paths)

        cmd = '#!/bin/sh\n'
        cmd += 'mkdir -p /usr/local/sbin\n'

        cmd += 'cp "%s" "%s"\n' % (os.path.join(frompath, polkit_file),
                                   polkit_path)
        cmd += 'chmod 644 "%s"\n' % (polkit_path, )

        cmd += 'cp "%s" "%s"\n' % (os.path.join(frompath, bitmask_root_file),
                                   bitmask_root)
        cmd += 'chmod 744 "%s"\n' % (bitmask_root, )

        if flags.STANDALONE:
            cmd += 'cp "%s" "%s"\n' % (
                os.path.join(frompath, openvpn_bin_file),
                openvpn_bin_path)
            cmd += 'chmod 744 "%s"\n' % (openvpn_bin_path, )

        return cmd

    @classmethod
    def get_vpn_env(kls):
        """
        Returns a dictionary with the custom env for the platform.
        This is mainly used for setting LD_LIBRARY_PATH to the correct
        path when distributing a standalone client

        :rtype: dict
        """
        ld_library_path = os.path.join(get_path_prefix(), "..", "lib")
        ld_library_path.encode(sys.getfilesystemencoding())
        return {
            "LD_LIBRARY_PATH": ld_library_path
        }

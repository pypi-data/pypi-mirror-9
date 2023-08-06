# -*- coding: utf-8 -*-
# Copyright (C) 2014 LEAP
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
Widget for "vpn" preferences
"""

from PySide import QtCore, QtGui
from leap.bitmask.gui.ui_preferences_vpn_page import Ui_PreferencesVpnPage

from leap.bitmask.config.leapsettings import LeapSettings
from leap.bitmask.gui.flashable import Flashable


class PreferencesVpnPage(QtGui.QWidget, Flashable):

    """
    Page in the preferences window that shows VPN settings
    """

    def __init__(self, parent, account, app):
        """
        :param parent: parent object of the EIPPreferencesWindow.
        :type parent: QWidget

        :param account: the currently active account
        :type account: Account

        :param app: shared App instance
        :type app: App
        """
        QtGui.QWidget.__init__(self, parent)
        self.AUTOMATIC_GATEWAY_LABEL = self.tr("Automatic")

        self.account = account
        self.app = app

        # Load UI
        self.ui = Ui_PreferencesVpnPage()
        self.ui.setupUi(self)
        self.ui.flash_label.setVisible(False)
        self.hide_flash()

        # Connections
        self.ui.gateways_list.clicked.connect(self._save_selected_gateway)
        sig = self.app.signaler
        sig.eip_get_gateways_list.connect(self._update_gateways_list)
        sig.eip_get_gateways_list_error.connect(self._gateways_list_error)
        sig.eip_uninitialized_provider.connect(
            self._gateways_list_uninitialized)

        # Trigger update
        self.app.backend.eip_get_gateways_list(domain=self.account.domain)

    def _save_selected_gateway(self, index):
        """
        TRIGGERS:
            self.ui.gateways_list.clicked

        Saves the new gateway setting to the configuration file.

        :param index: the current index of the selection.
        :type current_item: QModelIndex
        """
        item = self.ui.gateways_list.currentItem()

        if item.text() == self.AUTOMATIC_GATEWAY_LABEL:
            gateway = self.app.settings.GATEWAY_AUTOMATIC
        else:
            gateway = item.data(QtCore.Qt.UserRole)
        self.app.settings.set_selected_gateway(self.account.domain, gateway)
        self.app.backend.settings_set_selected_gateway(
            provider=self.account.domain,
            gateway=gateway)

    def _update_gateways_list(self, gateways):
        """
        TRIGGERS:
            Signaler.eip_get_gateways_list

        :param gateways: a list of gateways
        :type gateways: list of unicode

        Add the available gateways and select the one stored in
        configuration file.
        """
        self.ui.gateways_list.clear()
        self.ui.gateways_list.addItem(self.AUTOMATIC_GATEWAY_LABEL)

        selected_gateway = self.app.settings.get_selected_gateway(
            self.account.domain)

        index = 0
        for idx, (gw_name, gw_ip, gw_country) in enumerate(gateways):
            gateway_text = "{0} ({1})".format(gw_name, gw_ip)
            item = QtGui.QListWidgetItem(self.ui.gateways_list)
            item.setText(gateway_text)
            item.setIcon(QtGui.QIcon(
                ":/images/countries/%s.png" % (gw_country.lower(),)))
            item.setData(QtCore.Qt.UserRole, gw_ip)
            if gw_ip == selected_gateway:
                index = idx + 1
        self.ui.gateways_list.setCurrentRow(index)

    def _gateways_list_error(self):
        """
        TRIGGERS:
            Signaler.eip_get_gateways_list_error

        An error has occurred retrieving the gateway list
        so we inform the user.
        """
        self.flash_error(
            self.tr("Error loading configuration file."))
        self.ui.gateways_list.setEnabled(False)

    def _gateways_list_uninitialized(self):
        """
        TRIGGERS:
            Signaler.eip_uninitialized_provider

        The requested provider in not initialized yet, so we give the user an
        error msg.
        """
        self.flash_error(
            self.tr("This is an uninitialized provider, please log in first."))
        self.ui.gateways_list.setEnabled(False)

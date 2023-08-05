# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'src/leap/bitmask/gui/ui/preferences_vpn_page.ui'
#
# Created: Mon Dec 29 09:53:14 2014
#      by: pyside-uic 0.2.15 running on PySide 1.2.2
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_PreferencesVpnPage(object):
    def setupUi(self, PreferencesVpnPage):
        PreferencesVpnPage.setObjectName("PreferencesVpnPage")
        PreferencesVpnPage.resize(400, 362)
        self.verticalLayout = QtGui.QVBoxLayout(PreferencesVpnPage)
        self.verticalLayout.setObjectName("verticalLayout")
        self.flash_label = QtGui.QLabel(PreferencesVpnPage)
        self.flash_label.setAlignment(QtCore.Qt.AlignCenter)
        self.flash_label.setObjectName("flash_label")
        self.verticalLayout.addWidget(self.flash_label)
        self.heading_label = QtGui.QLabel(PreferencesVpnPage)
        self.heading_label.setObjectName("heading_label")
        self.verticalLayout.addWidget(self.heading_label)
        self.gateways_list = QtGui.QListWidget(PreferencesVpnPage)
        self.gateways_list.setObjectName("gateways_list")
        self.verticalLayout.addWidget(self.gateways_list)
        self.tip_label = QtGui.QLabel(PreferencesVpnPage)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tip_label.sizePolicy().hasHeightForWidth())
        self.tip_label.setSizePolicy(sizePolicy)
        self.tip_label.setScaledContents(False)
        self.tip_label.setWordWrap(True)
        self.tip_label.setObjectName("tip_label")
        self.verticalLayout.addWidget(self.tip_label)
        self.heading_label.setBuddy(self.gateways_list)
        self.tip_label.setBuddy(self.gateways_list)

        self.retranslateUi(PreferencesVpnPage)
        QtCore.QMetaObject.connectSlotsByName(PreferencesVpnPage)

    def retranslateUi(self, PreferencesVpnPage):
        PreferencesVpnPage.setWindowTitle(QtGui.QApplication.translate("PreferencesVpnPage", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.flash_label.setText(QtGui.QApplication.translate("PreferencesVpnPage", "<flash_label>", None, QtGui.QApplication.UnicodeUTF8))
        self.heading_label.setText(QtGui.QApplication.translate("PreferencesVpnPage", "Default VPN Gateway:", None, QtGui.QApplication.UnicodeUTF8))
        self.tip_label.setText(QtGui.QApplication.translate("PreferencesVpnPage", "You must reconnect for changes to take effect.", None, QtGui.QApplication.UnicodeUTF8))

import flags_rc

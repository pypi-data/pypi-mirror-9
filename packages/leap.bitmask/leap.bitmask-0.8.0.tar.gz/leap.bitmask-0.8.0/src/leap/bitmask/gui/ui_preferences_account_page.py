# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'src/leap/bitmask/gui/ui/preferences_account_page.ui'
#
# Created: Mon Dec 29 09:53:14 2014
#      by: pyside-uic 0.2.15 running on PySide 1.2.2
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_PreferencesAccountPage(object):
    def setupUi(self, PreferencesAccountPage):
        PreferencesAccountPage.setObjectName("PreferencesAccountPage")
        PreferencesAccountPage.resize(462, 371)
        self.verticalLayout = QtGui.QVBoxLayout(PreferencesAccountPage)
        self.verticalLayout.setObjectName("verticalLayout")
        self.provider_services_box = QtGui.QGroupBox(PreferencesAccountPage)
        self.provider_services_box.setFlat(False)
        self.provider_services_box.setObjectName("provider_services_box")
        self.gridLayout_4 = QtGui.QGridLayout(self.provider_services_box)
        self.gridLayout_4.setObjectName("gridLayout_4")
        self.provider_services_layout = QtGui.QVBoxLayout()
        self.provider_services_layout.setObjectName("provider_services_layout")
        self.gridLayout_4.addLayout(self.provider_services_layout, 1, 0, 1, 1)
        self.provider_services_label = QtGui.QLabel(self.provider_services_box)
        self.provider_services_label.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.provider_services_label.setObjectName("provider_services_label")
        self.gridLayout_4.addWidget(self.provider_services_label, 2, 0, 1, 1)
        self.verticalLayout.addWidget(self.provider_services_box)
        spacerItem = QtGui.QSpacerItem(20, 15, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Preferred)
        self.verticalLayout.addItem(spacerItem)
        self.groupBox = QtGui.QGroupBox(PreferencesAccountPage)
        self.groupBox.setObjectName("groupBox")
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.groupBox)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.change_password_button = QtGui.QPushButton(self.groupBox)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.change_password_button.sizePolicy().hasHeightForWidth())
        self.change_password_button.setSizePolicy(sizePolicy)
        self.change_password_button.setObjectName("change_password_button")
        self.verticalLayout_2.addWidget(self.change_password_button)
        self.change_password_label = QtGui.QLabel(self.groupBox)
        self.change_password_label.setObjectName("change_password_label")
        self.verticalLayout_2.addWidget(self.change_password_label)
        self.verticalLayout.addWidget(self.groupBox)
        spacerItem1 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem1)

        self.retranslateUi(PreferencesAccountPage)
        QtCore.QMetaObject.connectSlotsByName(PreferencesAccountPage)

    def retranslateUi(self, PreferencesAccountPage):
        PreferencesAccountPage.setWindowTitle(QtGui.QApplication.translate("PreferencesAccountPage", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.provider_services_box.setTitle(QtGui.QApplication.translate("PreferencesAccountPage", "Services", None, QtGui.QApplication.UnicodeUTF8))
        self.provider_services_label.setText(QtGui.QApplication.translate("PreferencesAccountPage", "<provider_services_label>", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox.setTitle(QtGui.QApplication.translate("PreferencesAccountPage", "Password", None, QtGui.QApplication.UnicodeUTF8))
        self.change_password_button.setText(QtGui.QApplication.translate("PreferencesAccountPage", "Change Password", None, QtGui.QApplication.UnicodeUTF8))
        self.change_password_label.setText(QtGui.QApplication.translate("PreferencesAccountPage", "<change_password_label>", None, QtGui.QApplication.UnicodeUTF8))


# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'src/leap/bitmask/gui/ui/preferences.ui'
#
# Created: Mon Dec 29 09:53:14 2014
#      by: pyside-uic 0.2.15 running on PySide 1.2.2
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_Preferences(object):
    def setupUi(self, Preferences):
        Preferences.setObjectName("Preferences")
        Preferences.resize(520, 439)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/images/mask-icon.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        Preferences.setWindowIcon(icon)
        self.verticalLayout = QtGui.QVBoxLayout(Preferences)
        self.verticalLayout.setSpacing(6)
        self.verticalLayout.setObjectName("verticalLayout")
        self.account_label = QtGui.QLabel(Preferences)
        font = QtGui.QFont()
        font.setWeight(75)
        font.setBold(True)
        self.account_label.setFont(font)
        self.account_label.setObjectName("account_label")
        self.verticalLayout.addWidget(self.account_label)
        self.line = QtGui.QFrame(Preferences)
        self.line.setFrameShape(QtGui.QFrame.HLine)
        self.line.setFrameShadow(QtGui.QFrame.Sunken)
        self.line.setObjectName("line")
        self.verticalLayout.addWidget(self.line)
        self.horizontal_layout = QtGui.QHBoxLayout()
        self.horizontal_layout.setSpacing(12)
        self.horizontal_layout.setObjectName("horizontal_layout")
        self.nav_widget = QtGui.QListWidget(Preferences)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.nav_widget.sizePolicy().hasHeightForWidth())
        self.nav_widget.setSizePolicy(sizePolicy)
        self.nav_widget.setMaximumSize(QtCore.QSize(120, 16777215))
        self.nav_widget.setIconSize(QtCore.QSize(32, 32))
        self.nav_widget.setMovement(QtGui.QListView.Static)
        self.nav_widget.setSpacing(10)
        self.nav_widget.setViewMode(QtGui.QListView.IconMode)
        self.nav_widget.setUniformItemSizes(True)
        self.nav_widget.setObjectName("nav_widget")
        self.horizontal_layout.addWidget(self.nav_widget)
        self.pages_widget = QtGui.QStackedWidget(Preferences)
        self.pages_widget.setObjectName("pages_widget")
        self.horizontal_layout.addWidget(self.pages_widget)
        self.verticalLayout.addLayout(self.horizontal_layout)
        self.button_layout = QtGui.QHBoxLayout()
        self.button_layout.setObjectName("button_layout")
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.button_layout.addItem(spacerItem)
        self.close_button = QtGui.QPushButton(Preferences)
        self.close_button.setObjectName("close_button")
        self.button_layout.addWidget(self.close_button)
        self.verticalLayout.addLayout(self.button_layout)
        self.verticalLayout.setStretch(2, 1)

        self.retranslateUi(Preferences)
        QtCore.QMetaObject.connectSlotsByName(Preferences)

    def retranslateUi(self, Preferences):
        Preferences.setWindowTitle(QtGui.QApplication.translate("Preferences", "Preferences", None, QtGui.QApplication.UnicodeUTF8))
        self.account_label.setText(QtGui.QApplication.translate("Preferences", "user@example.org", None, QtGui.QApplication.UnicodeUTF8))
        self.close_button.setText(QtGui.QApplication.translate("Preferences", "Close", None, QtGui.QApplication.UnicodeUTF8))

import icons_rc

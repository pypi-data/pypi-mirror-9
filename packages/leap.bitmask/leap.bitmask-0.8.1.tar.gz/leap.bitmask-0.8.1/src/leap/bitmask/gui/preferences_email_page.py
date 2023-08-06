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
Widget for "email" preferences
"""
import logging

from PySide import QtCore, QtGui
from leap.bitmask.gui.ui_preferences_email_page import Ui_PreferencesEmailPage

logger = logging.getLogger(__name__)


class PreferencesEmailPage(QtGui.QWidget):

    def __init__(self, parent, account, app):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_PreferencesEmailPage()
        self.ui.setupUi(self)

        self.account = account
        self.app = app

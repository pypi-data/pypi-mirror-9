# -*- coding: utf-8 -*-
# credentials.py
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
Credentials utilities
"""
from PySide import QtCore, QtGui

WEAK_PASSWORDS = ("123456", "qweasd", "qwerty", "password")
USERNAME_REGEX = r"^[a-z][a-z\d_\-\.]+[a-z\d]$"

USERNAME_VALIDATOR = QtGui.QRegExpValidator(QtCore.QRegExp(USERNAME_REGEX))


def username_checks(username):
    # translation helper
    _tr = QtCore.QObject().tr

    message = None

    if message is None and len(username) < 2:
        message = _tr("Username must have at least 2 characters")

    valid = USERNAME_VALIDATOR.validate(username, 0)
    valid_username = valid[0] == QtGui.QValidator.State.Acceptable
    if message is None and not valid_username:
        message = _tr("That username is not allowed. Try another.")

    return message is None, message


def password_checks(username, password, password2):
    """
    Performs basic password checks to avoid really easy passwords.

    :param username: username provided at the registrarion form
    :type username: str
    :param password: password from the registration form
    :type password: str
    :param password2: second password from the registration form
    :type password: str

    :returns: (True, None, None) if all the checks pass,
              (False, message, field name) otherwise
    :rtype: tuple(bool, str, str)
    """
    # translation helper
    _tr = QtCore.QObject().tr

    message = None
    field = None

    if message is None and password != password2:
        message = _tr("Passwords don't match")
        field = 'new_password_confirmation'

    if message is None and not password:
        message = _tr("Password is empty")
        field = 'new_password'

    if message is None and len(password) < 8:
        message = _tr("Password is too short")
        field = 'new_password'

    if message is None and password in WEAK_PASSWORDS:
        message = _tr("Password is too easy")
        field = 'new_password'

    if message is None and username == password:
        message = _tr("Password can't be the same as username")
        field = 'new_password'

    return message is None, message, field

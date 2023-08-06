# -*- coding: utf-8 -*-
# soledadbootstrapper.py
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
Soledad bootstrapping
"""
import logging
import os
import socket
import sys
import time

from ssl import SSLError
from sqlite3 import ProgrammingError as sqlite_ProgrammingError

from u1db import errors as u1db_errors
from twisted.internet import threads
from zope.proxy import sameProxiedObjects
from pysqlcipher.dbapi2 import ProgrammingError as sqlcipher_ProgrammingError

from leap.bitmask.config import flags
from leap.bitmask.config.providerconfig import ProviderConfig
from leap.bitmask.crypto.srpauth import SRPAuth
from leap.bitmask.services import download_service_config
from leap.bitmask.services.abstractbootstrapper import AbstractBootstrapper
from leap.bitmask.services.soledad.soledadconfig import SoledadConfig
from leap.bitmask.util import first, is_file, is_empty_file, make_address
from leap.bitmask.util import get_path_prefix
from leap.bitmask.platform_init import IS_WIN
from leap.common.check import leap_assert, leap_assert_type, leap_check
from leap.common.files import which
from leap.keymanager import KeyManager, openpgp
from leap.keymanager.errors import KeyNotFound
from leap.soledad.common.errors import InvalidAuthTokenError
from leap.soledad.client import Soledad, BootstrapSequenceError

logger = logging.getLogger(__name__)

"""
These mocks are replicated from imap tests and the repair utility.
They are needed for the moment to knock out the remote capabilities of soledad
during the use of the offline mode.

They should not be needed after we allow a null remote initialization in the
soledad client, and a switch to remote sync-able mode during runtime.
"""


class Mock(object):
    """
    A generic simple mock class
    """
    def __init__(self, return_value=None):
        self._return = return_value

    def __call__(self, *args, **kwargs):
        return self._return


class MockSharedDB(object):
    """
    Mocked  SharedDB object to replace in soledad before
    instantiating it in offline mode.
    """
    get_doc = Mock()
    put_doc = Mock()
    lock = Mock(return_value=('atoken', 300))
    unlock = Mock(return_value=True)

    def __call__(self):
        return self

# TODO these exceptions could be moved to soledad itself
# after settling this down.


class SoledadSyncError(Exception):
    message = "Error while syncing Soledad"


class SoledadInitError(Exception):
    message = "Error while initializing Soledad"


def get_db_paths(uuid):
    """
    Return the secrets and local db paths needed for soledad
    initialization

    :param uuid: uuid for user
    :type uuid: str

    :return: a tuple with secrets, local_db paths
    :rtype: tuple
    """
    prefix = os.path.join(get_path_prefix(), "leap", "soledad")
    secrets = "%s/%s.secret" % (prefix, uuid)
    local_db = "%s/%s.db" % (prefix, uuid)

    # We remove an empty file if found to avoid complains
    # about the db not being properly initialized
    if is_file(local_db) and is_empty_file(local_db):
        try:
            os.remove(local_db)
        except OSError:
            logger.warning(
                "Could not remove empty file %s"
                % local_db)
    return secrets, local_db


class SoledadBootstrapper(AbstractBootstrapper):
    """
    Soledad init procedure.
    """
    SOLEDAD_KEY = "soledad"
    KEYMANAGER_KEY = "keymanager"

    PUBKEY_KEY = "user[public_key]"

    MAX_INIT_RETRIES = 10
    MAX_SYNC_RETRIES = 10
    WAIT_MAX_SECONDS = 600
    # WAIT_STEP_SECONDS = 1
    WAIT_STEP_SECONDS = 5

    def __init__(self, signaler=None):
        AbstractBootstrapper.__init__(self, signaler)

        if signaler is not None:
            self._cancel_signal = signaler.soledad_cancelled_bootstrap

        self._provider_config = None
        self._soledad_config = None
        self._keymanager = None
        self._download_if_needed = False

        self._user = ""
        self._password = ""
        self._address = ""
        self._uuid = ""

        self._srpauth = None
        self._soledad = None

    @property
    def keymanager(self):
        return self._keymanager

    @property
    def soledad(self):
        return self._soledad

    @property
    def srpauth(self):
        if flags.OFFLINE is True:
            return None
        leap_assert(self._provider_config is not None,
                    "We need a provider config")
        return SRPAuth(self._provider_config)

    # initialization

    def load_offline_soledad(self, username, password, uuid):
        """
        Instantiate Soledad for offline use.

        :param username: full user id (user@provider)
        :type username: str or unicode
        :param password: the soledad passphrase
        :type password: unicode
        :param uuid: the user uuid
        :type uuid: str or unicode
        """
        self._address = username
        self._password = password
        self._uuid = uuid
        try:
            self.load_and_sync_soledad(uuid, offline=True)
            self._signaler.signal(self._signaler.soledad_offline_finished)
        except Exception as e:
            # TODO: we should handle more specific exceptions in here
            logger.exception(e)
            self._signaler.signal(self._signaler.soledad_offline_failed)

    def _get_soledad_local_params(self, uuid, offline=False):
        """
        Return the locals parameters needed for the soledad initialization.

        :param uuid: the uuid of the user, used in offline mode.
        :type uuid: unicode, or None.
        :return: secrets_path, local_db_path, token
        :rtype: tuple
        """
        # in the future, when we want to be able to switch to
        # online mode, this should be a proxy object too.
        # Same for server_url below.

        if offline is False:
            token = self.srpauth.get_token()
        else:
            token = ""

        secrets_path, local_db_path = get_db_paths(uuid)

        logger.debug('secrets_path:%s' % (secrets_path,))
        logger.debug('local_db:%s' % (local_db_path,))
        return (secrets_path, local_db_path, token)

    def _get_soledad_server_params(self, uuid, offline):
        """
        Return the remote parameters needed for the soledad initialization.

        :param uuid: the uuid of the user, used in offline mode.
        :type uuid: unicode, or None.
        :return: server_url, cert_file
        :rtype: tuple
        """
        if uuid is None:
            uuid = self.srpauth.get_uuid()

        if offline is True:
            server_url = "http://localhost:9999/"
            cert_file = ""
        else:
            server_url = self._pick_server(uuid)
            cert_file = self._provider_config.get_ca_cert_path()

        return server_url, cert_file

    def _soledad_sync_errback(self, failure):
        failure.trap(InvalidAuthTokenError)
        # in the case of an invalid token we have already turned off mail and
        # warned the user in _do_soledad_sync()

    def _do_soledad_init(self, uuid, secrets_path, local_db_path,
                         server_url, cert_file, token):
        """
        Initialize soledad, retry if necessary and raise an exception if we
        can't succeed.

        :param uuid: user identifier
        :type uuid: str
        :param secrets_path: path to secrets file
        :type secrets_path: str
        :param local_db_path: path to local db file
        :type local_db_path: str
        :param server_url: soledad server uri
        :type server_url: str
        :param cert_file: path to the certificate of the ca used
                          to validate the SSL certificate used by the remote
                          soledad server.
        :type cert_file: str
        :param auth token: auth token
        :type auth_token: str
        """
        init_tries = 1
        while init_tries <= self.MAX_INIT_RETRIES:
            try:
                logger.debug("Trying to init soledad....")
                self._try_soledad_init(
                    uuid, secrets_path, local_db_path,
                    server_url, cert_file, token)
                logger.debug("Soledad has been initialized.")
                return
            except Exception as exc:
                init_tries += 1
                msg = "Init failed, retrying... (retry {0} of {1})".format(
                    init_tries, self.MAX_INIT_RETRIES)
                logger.warning(msg)
                continue

        logger.exception(exc)
        raise SoledadInitError()

    def load_and_sync_soledad(self, uuid=None, offline=False):
        """
        Once everthing is in the right place, we instantiate and sync
        Soledad

        :param uuid: the uuid of the user, used in offline mode.
        :type uuid: unicode, or None.
        :param offline: whether to instantiate soledad for offline use.
        :type offline: bool
        """
        local_param = self._get_soledad_local_params(uuid, offline)
        remote_param = self._get_soledad_server_params(uuid, offline)

        secrets_path, local_db_path, token = local_param
        server_url, cert_file = remote_param

        try:
            self._do_soledad_init(uuid, secrets_path, local_db_path,
                                  server_url, cert_file, token)
        except SoledadInitError:
            # re-raise the exceptions from try_init,
            # we're currently handling the retries from the
            # soledad-launcher in the gui.
            raise

        leap_assert(not sameProxiedObjects(self._soledad, None),
                    "Null soledad, error while initializing")

        if flags.OFFLINE:
            self._init_keymanager(self._address, token)
        else:
            try:
                address = make_address(
                    self._user, self._provider_config.get_domain())
                self._init_keymanager(address, token)
                self._keymanager.get_key(
                    address, openpgp.OpenPGPKey,
                    private=True, fetch_remote=False)
                d = threads.deferToThread(self._do_soledad_sync)
                d.addErrback(self._soledad_sync_errback)
            except KeyNotFound:
                logger.debug("Key not found. Generating key for %s" %
                             (address,))
                self._do_soledad_sync()

    def _pick_server(self, uuid):
        """
        Choose a soledad server to sync against.

        :param uuid: the uuid for the user.
        :type uuid: unicode
        :returns: the server url
        :rtype: unicode
        """
        # TODO: Select server based on timezone (issue #3308)
        server_dict = self._soledad_config.get_hosts()

        if not server_dict.keys():
            # XXX raise more specific exception, and catch it properly!
            raise Exception("No soledad server found")

        selected_server = server_dict[first(server_dict.keys())]
        server_url = "https://%s:%s/user-%s" % (
            selected_server["hostname"],
            selected_server["port"],
            uuid)
        logger.debug("Using soledad server url: %s" % (server_url,))
        return server_url

    def _do_soledad_sync(self):
        """
        Do several retries to get an initial soledad sync.
        """
        # and now, let's sync
        sync_tries = self.MAX_SYNC_RETRIES
        step = self.WAIT_STEP_SECONDS
        max_wait = self.WAIT_MAX_SECONDS
        while sync_tries > 0:
            wait = 0
            try:
                logger.debug("Trying to sync soledad....")
                self._try_soledad_sync()
                while self.soledad.syncing:
                    time.sleep(step)
                    wait += step
                    if wait >= max_wait:
                        raise SoledadSyncError("timeout!")
                logger.debug("Soledad has been synced!")
                # so long, and thanks for all the fish
                return
            except SoledadSyncError:
                # maybe it's my connection, but I'm getting
                # ssl handshake timeouts and read errors quite often.
                # A particularly big sync is a disaster.
                # This deserves further investigation, maybe the
                # retry strategy can be pushed to u1db, or at least
                # it's something worthy to talk about with the
                # ubuntu folks.
                sync_tries += 1
                msg = "Sync failed, retrying... (retry {0} of {1})".format(
                    sync_tries, self.MAX_SYNC_RETRIES)
                logger.warning(msg)
                continue
            except InvalidAuthTokenError:
                self._signaler.signal(
                    self._signaler.soledad_invalid_auth_token)
                raise
            except Exception as e:
                # XXX release syncing lock
                logger.exception("Unhandled error while syncing "
                                 "soledad: %r" % (e,))
                break

        raise SoledadSyncError()

    def _try_soledad_init(self, uuid, secrets_path, local_db_path,
                          server_url, cert_file, auth_token):
        """
        Try to initialize soledad.

        :param uuid: user identifier
        :type uuid: str
        :param secrets_path: path to secrets file
        :type secrets_path: str
        :param local_db_path: path to local db file
        :type local_db_path: str
        :param server_url: soledad server uri
        :type server_url: str
        :param cert_file: path to the certificate of the ca used
                          to validate the SSL certificate used by the remote
                          soledad server.
        :type cert_file: str
        :param auth token: auth token
        :type auth_token: str
        """
        # TODO: If selected server fails, retry with another host
        # (issue #3309)
        encoding = sys.getfilesystemencoding()

        # XXX We should get a flag in soledad itself
        if flags.OFFLINE is True:
            Soledad._shared_db = MockSharedDB()
        try:
            self._soledad = Soledad(
                uuid,
                self._password,
                secrets_path=secrets_path.encode(encoding),
                local_db_path=local_db_path.encode(encoding),
                server_url=server_url,
                cert_file=cert_file.encode(encoding),
                auth_token=auth_token,
                defer_encryption=True)

        # XXX All these errors should be handled by soledad itself,
        # and return a subclass of SoledadInitializationFailed

        # recoverable, will guarantee retries
        except (socket.timeout, socket.error, BootstrapSequenceError):
            logger.warning("Error while initializing Soledad")
            raise

        # unrecoverable
        except (u1db_errors.Unauthorized, u1db_errors.HTTPError):
            logger.error("Error while initializing Soledad (u1db error).")
            raise
        except Exception as exc:
            logger.exception("Unhandled error while initializating "
                             "Soledad: %r" % (exc,))
            raise

    def _try_soledad_sync(self):
        """
        Try to sync soledad.
        Raises SoledadSyncError if not successful.
        """
        try:
            logger.debug("BOOTSTRAPPER: trying to sync Soledad....")
            # pass defer_decryption=False to get inline decryption
            # for debugging.
            self._soledad.sync(defer_decryption=True)
        except SSLError as exc:
            logger.error("%r" % (exc,))
            raise SoledadSyncError("Failed to sync soledad")
        except u1db_errors.InvalidGeneration as exc:
            logger.error("%r" % (exc,))
            raise SoledadSyncError("u1db: InvalidGeneration")
        except (sqlite_ProgrammingError, sqlcipher_ProgrammingError) as e:
            logger.exception("%r" % (e,))
            raise
        except InvalidAuthTokenError:
            # token is invalid, probably expired
            logger.error('Invalid auth token while trying to sync Soledad')
            raise
        except Exception as exc:
            logger.exception("Unhandled error while syncing "
                             "soledad: %r" % (exc,))
            raise SoledadSyncError("Failed to sync soledad")

    def _download_config(self):
        """
        Download the Soledad config for the given provider
        """
        leap_assert(self._provider_config,
                    "We need a provider configuration!")
        logger.debug("Downloading Soledad config for %s" %
                     (self._provider_config.get_domain(),))

        self._soledad_config = SoledadConfig()
        download_service_config(
            self._provider_config,
            self._soledad_config,
            self._session,
            self._download_if_needed)

    def _get_gpg_bin_path(self):
        """
        Return the path to gpg binary.

        :returns: the gpg binary path
        :rtype: str
        """
        gpgbin = None
        if flags.STANDALONE:
            gpgbin = os.path.join(
                get_path_prefix(), "..", "apps", "mail", "gpg")
            if IS_WIN:
                gpgbin += ".exe"
        else:
            try:
                gpgbin_options = which("gpg")
                # gnupg checks that the path to the binary is not a
                # symlink, so we need to filter those and come up with
                # just one option.
                for opt in gpgbin_options:
                    if not os.path.islink(opt):
                        gpgbin = opt
                        break
            except IndexError as e:
                logger.debug("Couldn't find the gpg binary!")
                logger.exception(e)
        leap_check(gpgbin is not None, "Could not find gpg binary")
        return gpgbin

    def _init_keymanager(self, address, token):
        """
        Initialize the keymanager.

        :param address: the address to initialize the keymanager with.
        :type address: str
        :param token: the auth token for accessing webapp.
        :type token: str
        """
        srp_auth = self.srpauth
        logger.debug('initializing keymanager...')

        if flags.OFFLINE is True:
            args = (address, "https://localhost", self._soledad)
            kwargs = {
                "ca_cert_path": "",
                "api_uri": "",
                "api_version": "",
                "uid": self._uuid,
                "gpgbinary": self._get_gpg_bin_path()
            }
        else:
            args = (
                address,
                "https://nicknym.%s:6425" % (
                    self._provider_config.get_domain(),),
                self._soledad
            )
            kwargs = {
                "token": token,
                "ca_cert_path": self._provider_config.get_ca_cert_path(),
                "api_uri": self._provider_config.get_api_uri(),
                "api_version": self._provider_config.get_api_version(),
                "uid": srp_auth.get_uuid(),
                "gpgbinary": self._get_gpg_bin_path()
            }
        try:
            self._keymanager = KeyManager(*args, **kwargs)
        except KeyNotFound:
            logger.debug('key for %s not found.' % address)
        except Exception as exc:
            logger.exception(exc)
            raise

        if flags.OFFLINE is False:
            # make sure key is in server
            logger.debug('Trying to send key to server...')
            try:
                self._keymanager.send_key(openpgp.OpenPGPKey)
            except KeyNotFound:
                logger.debug('No key found for %s, will generate soon.'
                             % address)
            except Exception as exc:
                logger.error("Error sending key to server.")
                logger.exception(exc)
                # but we do not raise

    def _gen_key(self):
        """
        Generates the key pair if needed, uploads it to the webapp and
        nickserver
        """
        leap_assert(self._provider_config is not None,
                    "We need a provider configuration!")
        leap_assert(self._soledad is not None,
                    "We need a non-null soledad to generate keys")

        address = make_address(
            self._user, self._provider_config.get_domain())
        logger.debug("Retrieving key for %s" % (address,))

        try:
            self._keymanager.get_key(
                address, openpgp.OpenPGPKey, private=True, fetch_remote=False)
            return
        except KeyNotFound:
            logger.debug("Key not found. Generating key for %s" % (address,))

        # generate key
        try:
            self._keymanager.gen_key(openpgp.OpenPGPKey)
        except Exception as exc:
            logger.error("Error while generating key!")
            logger.exception(exc)
            raise

        # send key
        try:
            self._keymanager.send_key(openpgp.OpenPGPKey)
        except Exception as exc:
            logger.error("Error while sending key!")
            logger.exception(exc)
            raise

        logger.debug("Key generated successfully.")

    def run_soledad_setup_checks(self, provider_config, user, password,
                                 download_if_needed=False):
        """
        Starts the checks needed for a new soledad setup

        :param provider_config: Provider configuration
        :type provider_config: ProviderConfig
        :param user: User's login
        :type user: unicode
        :param password: User's password
        :type password: unicode
        :param download_if_needed: If True, it will only download
                                   files if the have changed since the
                                   time it was previously downloaded.
        :type download_if_needed: bool
        """
        leap_assert_type(provider_config, ProviderConfig)

        # XXX we should provider a method for setting provider_config
        self._provider_config = provider_config
        self._download_if_needed = download_if_needed
        self._user = user
        self._password = password

        if flags.OFFLINE:
            signal_finished = self._signaler.soledad_offline_finished
            signal_failed = self._signaler.soledad_offline_failed
        else:
            signal_finished = self._signaler.soledad_bootstrap_finished
            signal_failed = self._signaler.soledad_bootstrap_failed

        try:
            self._download_config()

            # soledad config is ok, let's proceed to load and sync soledad
            uuid = self.srpauth.get_uuid()
            self.load_and_sync_soledad(uuid)

            if not flags.OFFLINE:
                self._gen_key()

            self._signaler.signal(signal_finished)
        except Exception as e:
            # TODO: we should handle more specific exceptions in here
            self._soledad = None
            self._keymanager = None
            logger.exception("Error while bootstrapping Soledad: %r" % (e, ))
            self._signaler.signal(signal_failed)

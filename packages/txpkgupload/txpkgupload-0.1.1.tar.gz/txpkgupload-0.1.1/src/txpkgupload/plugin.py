# Copyright 2005-2015 Canonical Ltd.  This software is licensed under the
# GNU Affero General Public License version 3 (see the file LICENSE).

__metaclass__ = type
__all__ = [
    'PkgUploadServiceMaker',
    ]

from functools import partial

from formencode import Schema
from formencode.api import set_stdtranslation
from formencode.validators import (
    Int,
    RequireIfPresent,
    String,
    StringBool,
    )
from lazr.sshserver.auth import (
    LaunchpadAvatar,
    PublicKeyFromLaunchpadChecker,
    )
from lazr.sshserver.service import SSHService
from lazr.sshserver.session import DoNothingSession
from twisted.application.service import IServiceMaker
from twisted.conch.interfaces import ISession
from twisted.conch.ssh import filetransfer
from twisted.cred.portal import IRealm, Portal
from twisted.plugin import IPlugin
from twisted.protocols.policies import TimeoutFactory
from twisted.python import (
    components,
    usage,
    )
from twisted.web.xmlrpc import Proxy
import yaml
from zope.interface import implements

from txpkgupload import get_txpkgupload_root
from txpkgupload.services import (
    PkgUploadServices,
    ReadyService,
    )
from txpkgupload.twistedftp import FTPServiceFactory
from txpkgupload.twistedsftp import SFTPServer


# Ensure that formencode does not translate strings; there are encoding issues
# that are easier to side-step for now.
set_stdtranslation(languages=[])


class ConfigOops(Schema):
    """Configuration validator for OOPS options."""

    if_key_missing = None

    directory = String(if_missing="")
    reporter = String(if_missing="PKGUPLOAD")

    chained_validators = (
        RequireIfPresent("reporter", present="directory"),
        )


class ConfigFtp(Schema):
    """Configuration validator for FTP options."""

    if_key_missing = None

    # The port to run the FTP server on.
    port = Int(if_missing=2121)


class ConfigSftp(Schema):
    """Configuration validator for SFTP options."""

    if_key_missing = None

    # The URL of the XML-RPC endpoint that handles authentication of SSH
    # users.  This should implement IAuthServer.
    authentication_endpoint = String(if_missing=None)

    # The absolute path to the private key used for the SFTP server.
    host_key_private = String(if_missing=None)

    # The absolute path to the public key used for the SFTP server.
    host_key_public = String(if_missing=None)

    # An announcement printed to users when they connect.
    banner = String(if_missing=None)

    # The port to run the SFTP server on, expressed in Twisted's "strports"
    # mini-language.
    port = String(if_missing="tcp:5022")


class Config(Schema):
    """Configuration validator."""

    if_key_missing = None

    oops = ConfigOops
    ftp = ConfigFtp
    sftp = ConfigSftp

    # The access log location.  Information such as connection, SSH login
    # and session start times will be logged here.
    access_log = String(
        if_empty="txpkgupload-access.log", if_missing="txpkgupload-access.log")

    # If true, enable additional debug logging.
    debug = StringBool(if_missing=False)

    # Connections that are idle for more than this many seconds are
    # disconnected.
    idle_timeout = Int(if_missing=3600)

    # Where on the filesystem do uploads live?
    fsroot = String(if_missing=None)

    @classmethod
    def parse(cls, stream):
        """Load a YAML configuration from `stream` and validate."""
        return cls.to_python(yaml.load(stream))

    @classmethod
    def load(cls, filename):
        """Load a YAML configuration from `filename` and validate."""
        with open(filename, "rb") as stream:
            return cls.parse(stream)


class Options(usage.Options):

    optParameters = [
        ["config-file", "c", "etc/txpkgupload.yaml",
         "Configuration file to load."],
        ]


class PkgUploadAvatar(LaunchpadAvatar):
    """An SSH avatar specific to txpkgupload.

    :ivar fs_root: The file system root for this session.
    """

    def __init__(self, user_dict, fs_root):
        LaunchpadAvatar.__init__(self, user_dict)
        self.fs_root = fs_root


class Realm:
    implements(IRealm)

    def __init__(self, authentication_proxy, fs_root):
        self.authentication_proxy = authentication_proxy
        self.fs_root = fs_root

    def requestAvatar(self, avatar_id, mind, *interfaces):
        # Fetch the user's details from the authserver
        deferred = mind.lookupUserDetails(
            self.authentication_proxy, avatar_id)

        # Once all those details are retrieved, we can construct the avatar.
        def got_user_dict(user_dict):
            avatar = PkgUploadAvatar(user_dict, self.fs_root)
            return interfaces[0], avatar, avatar.logout

        return deferred.addCallback(got_user_dict)


def make_portal(authentication_endpoint, fs_root):
    """Create and return a `Portal` for the SSH service.

    This portal accepts SSH credentials and returns our customized SSH
    avatars (see `LaunchpadAvatar`).
    """
    authentication_proxy = Proxy(authentication_endpoint)
    portal = Portal(Realm(authentication_proxy, fs_root))
    portal.registerChecker(
        PublicKeyFromLaunchpadChecker(authentication_proxy))
    return portal


def timeout_decorator(idle_timeout, factory):
    """Add idle timeouts to a factory."""
    return TimeoutFactory(factory, timeoutPeriod=idle_timeout)


class PkgUploadServiceMaker:
    """Create package upload frontend servers."""

    implements(IServiceMaker, IPlugin)

    options = Options

    def __init__(self, name, description):
        self.tapname = name
        self.description = description

    def makeService(self, options, server_argv=None):
        """Construct a service."""
        config_file = options["config-file"]
        config = Config.load(config_file)

        oops_config = config["oops"]
        oops_dir = oops_config["directory"]
        oops_reporter = oops_config["reporter"]

        services = PkgUploadServices(
            oops_dir, oops_reporter, server_argv=server_argv)

        root = get_txpkgupload_root(config["fsroot"])

        ftp_config = config["ftp"]
        ftp_service = FTPServiceFactory.makeFTPService(
            port=ftp_config["port"],
            root=root,
            idle_timeout=config["idle_timeout"])
        ftp_service.name = "ftp"
        ftp_service.setServiceParent(services)

        sftp_config = config["sftp"]
        sftp_service = SSHService(
            portal=make_portal(sftp_config["authentication_endpoint"], root),
            private_key_path=sftp_config["host_key_private"],
            public_key_path=sftp_config["host_key_public"],
            main_log='txpkgupload',
            access_log='txpkgupload.access',
            access_log_path=config["access_log"],
            strport=sftp_config["port"],
            factory_decorator=partial(
                timeout_decorator, config["idle_timeout"]),
            banner=sftp_config["banner"])
        sftp_service.name = "sftp"
        sftp_service.setServiceParent(services)

        ready_service = ReadyService()
        ready_service.setServiceParent(services)

        return services


components.registerAdapter(
    SFTPServer, PkgUploadAvatar, filetransfer.ISFTPServer)

components.registerAdapter(DoNothingSession, PkgUploadAvatar, ISession)

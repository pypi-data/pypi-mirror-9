# Copyright 2011 Canonical Ltd.  This software is licensed under the
# GNU Affero General Public License version 3 (see the file LICENSE).

"""Twisted FTP implementation of the txpkgupload upload server."""

__metaclass__ = type
__all__ = [
    'AnonymousShell',
    'FTPRealm',
    ]

import os
import tempfile

from twisted.application import (
    service,
    strports,
    )
from twisted.cred import (
    checkers,
    credentials,
    )
from twisted.cred.portal import (
    IRealm,
    Portal,
    )
from twisted.internet import defer
from twisted.protocols import ftp
from twisted.python import filepath
from zope.interface import implements

from txpkgupload.filesystem import UploadFileSystem
from txpkgupload.hooks import Hooks


class AccessCheck:
    """An `ICredentialsChecker` for txpkgupload FTP sessions."""
    implements(checkers.ICredentialsChecker)
    credentialInterfaces = (
        credentials.IUsernamePassword, credentials.IAnonymous)

    def requestAvatarId(self, credentials):
        # txpkgupload allows any credentials.  People can use "anonymous" if
        # they want but anything goes.  Thus, we don't actually *check* the
        # credentials, and we return the standard avatarId for 'anonymous'.
        return checkers.ANONYMOUS


class AnonymousShell(ftp.FTPShell):
    """The 'command' interface for sessions.

    Roughly equivalent to the SFTPServer in the sftp side of things.
    """

    def __init__(self, fsroot, temp_dir):
        self._fs_root = fsroot
        self.uploadfilesystem = UploadFileSystem(
            tempfile.mkdtemp(dir=temp_dir))
        self._current_upload = self.uploadfilesystem.rootpath
        os.chmod(self._current_upload, 0770)
        self.hook = Hooks(self._fs_root, perms='g+rws', prefix='-ftp')
        self.hook.new_client_hook(self._current_upload, 0, 0)
        super(AnonymousShell, self).__init__(
            filepath.FilePath(self._current_upload))

    def openForWriting(self, file_segments):
        """Write the uploaded file to disk, safely.

        :param file_segments: A list containing string items, one for each
            path component of the file being uploaded.  The file referenced
            is relative to the temporary root for this session.

        If the file path contains directories, we create them.
        """
        filename = os.sep.join(file_segments)
        self._create_missing_directories(filename)
        return super(AnonymousShell, self).openForWriting(file_segments)

    def makeDirectory(self, path):
        """Make a directory using the secure `UploadFileSystem`."""
        path = os.sep.join(path)
        return defer.maybeDeferred(self.uploadfilesystem.mkdir, path)

    def access(self, segments):
        """Permissive CWD that auto-creates target directories."""
        if segments:
            path = self._path(segments)
            path.makedirs()
        return super(AnonymousShell, self).access(segments)

    def logout(self):
        """Called when the client disconnects.

        We need to post-process the upload.
        """
        self.hook.client_done_hook(self._current_upload, 0, 0)

    def _create_missing_directories(self, filename):
        # Same as SFTPServer
        new_dir, new_file = os.path.split(
            self.uploadfilesystem._sanitize(filename))
        if new_dir != '':
            if not os.path.exists(
                os.path.join(self._current_upload, new_dir)):
                self.uploadfilesystem.mkdir(new_dir)

    def list(self, path_segments, attrs):
        return defer.fail(ftp.CmdNotImplementedError("LIST"))


class FTPRealm:
    """FTP Realm that lets anyone in."""
    implements(IRealm)

    def __init__(self, root, temp_dir):
        self.root = root
        self.temp_dir = temp_dir

    def requestAvatar(self, avatarId, mind, *interfaces):
        """Return a txpkgupload avatar - that is, an "authorisation".

        txpkgupload FTP avatars are totally fake, we don't care about
        credentials. See `AccessCheck` above.
        """
        for iface in interfaces:
            if iface is ftp.IFTPShell:
                avatar = AnonymousShell(self.root, self.temp_dir)
                return ftp.IFTPShell, avatar, getattr(
                    avatar, 'logout', lambda: None)
        raise NotImplementedError(
            "Only IFTPShell interface is supported by this realm")


class FTPServiceFactory(service.Service):
    """A factory that makes an `FTPService`"""

    def __init__(self, port, root, temp_dir, idle_timeout):
        realm = FTPRealm(root, temp_dir)
        portal = Portal(realm)
        portal.registerChecker(AccessCheck())
        factory = ftp.FTPFactory(portal)

        factory.tld = root
        factory.protocol = ftp.FTP
        factory.welcomeMessage = "Launchpad upload server"
        factory.timeOut = idle_timeout

        self.ftpfactory = factory
        self.portno = port

    @staticmethod
    def makeFTPService(port, root, temp_dir, idle_timeout):
        strport = "tcp:%s" % port
        factory = FTPServiceFactory(port, root, temp_dir, idle_timeout)
        return strports.service(strport, factory.ftpfactory)

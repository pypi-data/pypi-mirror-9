# Copyright 2009-2011 Canonical Ltd.  This software is licensed under the
# GNU Affero General Public License version 3 (see the file LICENSE).

__metaclass__ = type

from collections import defaultdict
from functools import partial
import os
import shutil
import stat
import StringIO
import sys
import tempfile
from textwrap import dedent

from fixtures import (
    EnvironmentVariableFixture,
    Fixture,
    TempDir,
    )
from fixtures.callmany import MultipleExceptions
from formencode import Invalid
from lazr.sshserver.auth import NoSuchPersonWithName
from testtools import TestCase
from testtools.compat import reraise
from testtools.deferredruntest import AsynchronousDeferredRunTest
from testtools.matchers import (
    MatchesException,
    Raises,
    )
from twisted.application.service import (
    Application,
    IService,
    MultiService,
    )
from twisted.conch.client.default import SSHUserAuthClient
from twisted.conch.client.direct import SSHClientFactory
from twisted.conch.scripts.cftp import ClientOptions
from twisted.conch.ssh.channel import SSHChannel
from twisted.conch.ssh.common import NS
from twisted.conch.ssh.connection import SSHConnection
from twisted.conch.ssh.filetransfer import (
    FileTransferClient,
    FXF_CREAT,
    FXF_EXCL,
    FXF_TRUNC,
    FXF_WRITE,
    )
from twisted.internet import (
    defer,
    reactor,
    )
from twisted.internet.protocol import ClientCreator
from twisted.protocols.ftp import FTPClient
from twisted.python import log
from twisted.web import (
    server,
    xmlrpc,
    )
import yaml

from txpkgupload.hooks import Hooks
from txpkgupload.plugin import (
    Config,
    Options,
    PkgUploadServiceMaker,
    )


class DeferringFixture(Fixture):
    """A Fixture whose cleanups may return Deferred objects."""

    @defer.inlineCallbacks
    def cleanUp(self, raise_first=True):
        # We can't use the usual fixtures.callmany.CallMany.__call__
        # implementation, as it loses Deferreds, so we have to poke inside
        # it.
        result = []
        while self._cleanups._cleanups:
            cleanup, args, kwargs = self._cleanups._cleanups.pop()
            try:
                yield cleanup(*args, **kwargs)
            except Exception:
                result.append(sys.exc_info())
        if result and raise_first:
            if 1 == len(result):
                error = result[0]
                reraise(error[0], error[1], error[2])
            else:
                raise MultipleExceptions(*result)
        if not raise_first:
            defer.returnValue(result)


class TestConfig(TestCase):
    """Tests for `txpkgupload.plugin.Config`."""

    def test_defaults(self):
        expected = {
            "access_log": "txpkgupload-access.log",
            "debug": False,
            "fsroot": None,
            "ftp": {
                "port": 2121,
                },
            "idle_timeout": 3600,
            "oops": {
                "directory": "",
                "reporter": "PKGUPLOAD",
                },
            "sftp": {
                "authentication_endpoint": None,
                "banner": None,
                "host_key_private": None,
                "host_key_public": None,
                "port": "tcp:5022",
                },
            "temp_dir": None,
            }
        observed = Config.to_python({})
        self.assertEqual(expected, observed)

    def test_parse(self):
        # Configuration can be parsed from a snippet of YAML.
        observed = Config.parse('access_log: "/some/where.log"')
        self.assertEqual("/some/where.log", observed["access_log"])

    def test_load(self):
        # Configuration can be loaded and parsed from a file.
        filename = os.path.join(self.useFixture(TempDir()).path, "config.yaml")
        with open(filename, "w") as stream:
            stream.write('access_log: "/some/where.log"')
        observed = Config.load(filename)
        self.assertEqual("/some/where.log", observed["access_log"])

    def test_load_example(self):
        # The example configuration can be loaded and validated.
        filename = os.path.join(
            os.path.dirname(__file__), os.pardir, os.pardir, os.pardir,
            "etc", "txpkgupload.yaml")
        Config.load(filename)

    def check_exception(self, config, message):
        # Check that a UsageError is raised when parsing options.
        self.assertThat(
            partial(Config.to_python, config),
            Raises(MatchesException(Invalid, message)))

    def test_option_ftp_port_integer(self):
        self.check_exception(
            {"ftp": {"port": "bob"}},
            "ftp: port: Please enter an integer value")

    def test_option_idle_timeout_integer(self):
        self.check_exception(
            {"idle_timeout": "bob"},
            "idle_timeout: Please enter an integer value")


class TestOptions(TestCase):
    """Tests for `txpkgupload.plugin.Options`."""

    def test_defaults(self):
        options = Options()
        expected = {"config-file": "etc/txpkgupload.yaml"}
        self.assertEqual(expected, options.defaults)

    def test_parse_minimal_options(self):
        options = Options()
        # The minimal set of options that must be provided.
        arguments = []
        options.parseOptions(arguments)  # No error.


def deep_update(old, new):
    for key, value in new.items():
        if isinstance(value, dict):
            if key in old:
                deep_update(old[key], new[key])
            else:
                old[key] = dict(new[key])
        else:
            old[key] = new[key]


class PkgUploadFixture(DeferringFixture):
    """A txpkgupload server fixture."""

    def __init__(self, extra_config=None):
        self.extra_config = extra_config

    @property
    def logfile(self):
        return os.path.join(self.root, "txpkgupload.log")

    def setUp(self):
        super(PkgUploadFixture, self).setUp()
        self.root = self.useFixture(TempDir()).path
        top = os.path.join(
            os.path.dirname(__file__), os.pardir, os.pardir, os.pardir)
        with open(os.path.join(top, "etc", "txpkgupload.yaml")) as stream:
            config = yaml.load(stream)
        config["access_log"] = os.path.join(
            self.root, "txpkgupload-access.log")
        if self.extra_config is not None:
            deep_update(
                config, yaml.load(StringIO.StringIO(self.extra_config)))
        # Make some paths absolute to cope with tests running in a different
        # working directory.
        for key in ("host_key_private", "host_key_public"):
            if config["sftp"][key] and not os.path.isabs(config["sftp"][key]):
                config["sftp"][key] = os.path.join(top, config["sftp"][key])
        filename = os.path.join(self.root, "config.yaml")
        with open(filename, "w") as stream:
            yaml.dump(config, stream)
        options = Options()
        options.parseOptions(["-c", filename])
        self.service_maker = PkgUploadServiceMaker(
            "txpkgupload", "description")
        self.service = self.service_maker.makeService(
            options, server_argv=["--logfile", self.logfile])
        # Set up logging more or less as twistd's standard application
        # runner would, and start the service.
        application = Application(self.service_maker.tapname)
        self.service.setServiceParent(application)
        self.observer = application.getComponent(log.ILogObserver, None)
        log.addObserver(self.observer)
        self.addCleanup(log.removeObserver, self.observer)
        IService(application).startService()
        self.addCleanup(IService(application).stopService)

    def waitForPostProcessing(self, number=1):
        deferred = defer.Deferred()
        check_call = None
        timeout_call = None

        def check():
            if os.path.exists(self.logfile):
                with open(self.logfile, "r") as logfile:
                    occurrences = logfile.read().count(Hooks.LOG_MAGIC)
                    if occurrences >= number:
                        if timeout_call is not None and timeout_call.active():
                            timeout_call.cancel()
                        deferred.callback(None)
                        return
            check_call = reactor.callLater(0.1, check)

        def timeout():
            if check_call is not None and check_call.active():
                check_call.cancel()
            try:
                raise Exception("txpkgupload post-processing did not complete")
            except Exception:
                deferred.errback()

        check()
        timeout_call = reactor.callLater(20, timeout)
        return deferred


class FTPServer(DeferringFixture):
    """This is an abstraction of connecting to an FTP server."""

    def __init__(self, root_dir):
        self.root_dir = root_dir
        self.fsroot = os.path.join(self.root_dir, "incoming")
        self.temp_dir = os.path.join(self.root_dir, "tmp-incoming")
        top = os.path.join(
            os.path.dirname(__file__), os.pardir, os.pardir, os.pardir)
        with open(os.path.join(top, "etc", "txpkgupload.yaml")) as stream:
            config = yaml.load(stream)
        self.port = config["ftp"]["port"]

    def setUp(self):
        super(FTPServer, self).setUp()
        os.mkdir(self.fsroot)
        os.mkdir(self.temp_dir)
        self.pkgupload = self.useFixture(PkgUploadFixture(dedent("""\
            fsroot: %s
            temp_dir: %s""") % (self.fsroot, self.temp_dir)))

    def getAnonClient(self):
        creator = ClientCreator(
            reactor, FTPClient,
            username="anonymous", password="me@example.com")
        return creator.connectTCP("localhost", self.port)

    def getClient(self):
        creator = ClientCreator(
            reactor, FTPClient, username="ubuntu", password="")
        return creator.connectTCP("localhost", self.port)

    def makeDirectory(self, client, path):
        return client.makeDirectory(path)

    @defer.inlineCallbacks
    def createFile(self, client, relpath, data):
        d1, d2 = client.storeFile(relpath)
        sender = yield d1
        sender.transport.write(data)
        sender.finish()
        yield d2

    def disconnect(self, client):
        return client.transport.loseConnection()

    def waitForClose(self, number=1):
        """Wait for an FTP connection to close.

        txpkgupload is configured to echo 'Post-processing finished' to
        stdout when a connection closes, so we wait for that to appear in
        its output as a way to tell that the server has finished with the
        connection.
        """
        return self.pkgupload.waitForPostProcessing(number)


class SFTPSession(SSHChannel):
    """An SSH channel that requests the SFTP subsystem."""

    name = "session"

    def channelOpen(self, data):
        d = self.conn.sendRequest(self, "subsystem", NS("sftp"), wantReply=1)

        def _continueSFTP(result):
            client = FileTransferClient()
            client.makeConnection(self)
            self.dataReceived = client.dataReceived
            self.conn._sftp.callback(client)

        d.addCallback(_continueSFTP)


class SFTPConnection(SSHConnection):
    """An SSH connection that just opens an SFTP session."""

    def serviceStarted(self):
        SSHConnection.serviceStarted(self)
        self.openChannel(SFTPSession())


class FakeAuthServerService(xmlrpc.XMLRPC):
    """A fake version of the Launchpad authserver service."""

    def __init__(self):
        xmlrpc.XMLRPC.__init__(self)
        self.keys = defaultdict(list)

    def addSSHKey(self, username, public_key_path):
        with open(public_key_path, "r") as f:
            public_key = f.read()
        kind, keytext, _ = public_key.split(" ", 2)
        if kind == "ssh-rsa":
            keytype = "RSA"
        elif kind == "ssh-dss":
            keytype = "DSA"
        else:
            raise Exception("Unrecognised public key type %s" % kind)
        self.keys[username].append((keytype, keytext))

    def xmlrpc_getUserAndSSHKeys(self, username):
        if username not in self.keys:
            raise NoSuchPersonWithName(username)
        return {
            "id": username,
            "name": username,
            "keys": self.keys[username],
            }


class SFTPServer(DeferringFixture):
    """This is an abstraction of connecting to an SFTP server."""

    def __init__(self, root_dir):
        self.root_dir = root_dir
        self.fsroot = os.path.join(self.root_dir, "incoming")
        self.temp_dir = os.path.join(self.root_dir, "tmp-incoming")
        #self._factory = factory
        top = os.path.join(
            os.path.dirname(__file__), os.pardir, os.pardir, os.pardir)
        with open(os.path.join(top, "etc", "txpkgupload.yaml")) as stream:
            config = yaml.load(stream)
        self.port = int(config["sftp"]["port"].partition(':')[2])
        self.test_private_key = os.path.join(
            os.path.dirname(__file__), "txpkgupload-sftp")
        self.test_public_key = os.path.join(
            os.path.dirname(__file__), "txpkgupload-sftp.pub")

    def setUpUser(self, name):
        self.authserver.addSSHKey(name, self.test_public_key)
        # Set up a temporary home directory for Paramiko's sake
        self._home_dir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self._home_dir)
        os.mkdir(os.path.join(self._home_dir, '.ssh'))
        os.symlink(
            self.test_private_key,
            os.path.join(self._home_dir, '.ssh', 'id_rsa'))
        self.useFixture(EnvironmentVariableFixture('HOME', self._home_dir))
        self.useFixture(EnvironmentVariableFixture('SSH_AUTH_SOCK', None))
        self.useFixture(EnvironmentVariableFixture('BZR_SSH', 'paramiko'))

    def setUp(self):
        super(SFTPServer, self).setUp()
        self.authserver = FakeAuthServerService()
        self.authserver_listener = reactor.listenTCP(
            0, server.Site(self.authserver))
        self.authserver_port = self.authserver_listener.getHost().port
        self.authserver_url = b"http://localhost:%d/" % self.authserver_port
        self.addCleanup(self.authserver_listener.stopListening)
        self.setUpUser('joe')
        os.mkdir(self.fsroot)
        os.mkdir(self.temp_dir)
        self.pkgupload = self.useFixture(PkgUploadFixture(dedent("""\
            sftp:
              authentication_endpoint: %s
            fsroot: %s
            temp_dir: %s""") %
            (self.authserver_url, self.fsroot, self.temp_dir)))

    @defer.inlineCallbacks
    def getClient(self):
        options = ClientOptions()
        options["host"] = host = "localhost"
        options["port"] = self.port
        options.identitys = [self.test_private_key]
        conn = SFTPConnection()
        conn._sftp = defer.Deferred()
        auth_client = SSHUserAuthClient("joe", options, conn)
        verifyHostKey = lambda t, h, pk, fp: defer.succeed(None)
        connecting = defer.Deferred()
        factory = SSHClientFactory(
            connecting, options, verifyHostKey, auth_client)
        connector = reactor.connectTCP(host, self.port, factory)
        yield connecting
        client = yield conn._sftp
        defer.returnValue(client)

    def makeDirectory(self, client, path):
        return client.makeDirectory(path, {"permissions": 0777})

    @defer.inlineCallbacks
    def createFile(self, client, relpath, data):
        remote_file = yield client.openFile(
            relpath, FXF_WRITE | FXF_CREAT | FXF_TRUNC | FXF_EXCL, {})
        yield remote_file.writeChunk(0, data)
        yield remote_file.close()

    # Having to do all this work here probably means that some handlers
    # aren't hooked up properly, but it's good enough for testing.
    @defer.inlineCallbacks
    def disconnect(self, client):
        sftp_session = client.transport
        ssh_client_transport = sftp_session.conn.transport
        raw_transport = ssh_client_transport.transport
        yield sftp_session.loseConnection()
        yield ssh_client_transport.loseConnection()
        yield raw_transport.loseConnection()

    def waitForClose(self, number=1):
        return self.pkgupload.waitForPostProcessing(number)


class TestPkgUploadServiceMakerMixin:
    """Mixin with generic tests for `txpkgupload.plugin.PkgUploadServiceMaker`.

    Includes functional tests of the services.
    """

    run_tests_with = AsynchronousDeferredRunTest.make_factory(timeout=20)

    def setUp(self):
        """Set up txpkgupload in a temp dir."""
        super(TestPkgUploadServiceMakerMixin, self).setUp()
        root_dir = self.useFixture(TempDir()).path
        self.server = self.server_factory(root_dir)
        self.useFixture(self.server)

    def test_init(self):
        service_maker = self.server.pkgupload.service_maker
        self.assertEqual("txpkgupload", service_maker.tapname)
        self.assertEqual("description", service_maker.description)

    def test_makeService(self):
        service = self.server.pkgupload.service
        self.assertIsInstance(service, MultiService)
        self.assertEqual(3, len(service.services))
        self.assertSequenceEqual(
            ["ftp", "ready", "sftp"], sorted(service.namedServices))
        self.assertEqual(
            len(service.namedServices), len(service.services),
            "Not all services are named.")

    def _uploadPath(self, path):
        """Return system path of specified path inside an upload.

        Only works for a single upload (txpkgupload transaction).
        """
        contents = sorted(os.listdir(self.server.fsroot))
        upload_dir = contents[0]
        return os.path.join(self.server.fsroot, upload_dir, path)

    @defer.inlineCallbacks
    def test_mkdir(self):
        # Creating directories on the server makes actual directories where we
        # expect them, and creates them with g+rwxs
        client = yield self.server.getClient()
        yield self.server.makeDirectory(client, 'foo/bar')

        yield self.server.disconnect(client)
        yield self.server.waitForClose()

        wanted_path = self._uploadPath('foo/bar')
        self.assertTrue(os.path.exists(wanted_path))
        self.assertEqual(os.stat(wanted_path).st_mode, 042775)

    @defer.inlineCallbacks
    def test_rmdir(self):
        """Check recursive RMD (aka rmdir)"""
        client = yield self.server.getClient()
        yield self.server.makeDirectory(client, 'foo/bar')
        yield client.removeDirectory('foo/bar')
        yield client.removeDirectory('foo')

        yield self.server.disconnect(client)
        yield self.server.waitForClose()

        wanted_path = self._uploadPath('foo')
        self.assertFalse(os.path.exists(wanted_path))

    @defer.inlineCallbacks
    def test_single_upload(self):
        """Check if the parent directories are created during file upload.

        The uploaded file permissions are also special (g+rwxs).
        """
        client = yield self.server.getClient()
        yield self.server.createFile(client, "foo/bar/baz", "fake contents")

        yield self.server.disconnect(client)
        yield self.server.waitForClose()

        wanted_path = self._uploadPath('foo/bar/baz')
        fs_content = open(os.path.join(wanted_path)).read()
        self.assertEqual(fs_content, "fake contents")
        # Expected mode is -rw-rwSr--.
        self.assertEqual(
            os.stat(wanted_path).st_mode,
            stat.S_IROTH | stat.S_ISGID | stat.S_IRGRP | stat.S_IWGRP
            | stat.S_IWUSR | stat.S_IRUSR | stat.S_IFREG)

    @defer.inlineCallbacks
    def test_full_source_upload(self):
        """Check that the connection will deal with multiple files being
        uploaded.
        """
        client = yield self.server.getClient()

        files = ['test-source_0.1.dsc',
                 'test-source_0.1.orig.tar.gz',
                 'test-source_0.1.diff.gz',
                 'test-source_0.1_source.changes']

        for upload in files:
            fake_file = StringIO.StringIO(upload)
            file_to_upload = "~ppa-user/ppa/ubuntu/%s" % upload
            yield self.server.createFile(client, file_to_upload, upload)

        yield self.server.disconnect(client)
        yield self.server.waitForClose()

        upload_path = self._uploadPath('')
        self.assertEqual(os.stat(upload_path).st_mode, 042770)
        dir_name = upload_path.split('/')[-2]
        if isinstance(self.server, SFTPServer):
            self.assertEqual(dir_name.startswith('upload-sftp-2'), True)
        elif isinstance(self.server, FTPServer):
            self.assertEqual(dir_name.startswith('upload-ftp-2'), True)
        else:
            raise AssertionError(
                "self.server is neither SFTPServer or FTPServer")
        for upload in files:
            wanted_path = self._uploadPath(
                "~ppa-user/ppa/ubuntu/%s" % upload)
            fs_content = open(os.path.join(wanted_path)).read()
            self.assertEqual(fs_content, upload)
            # Expected mode is -rw-rwSr--.
            self.assertEqual(
                os.stat(wanted_path).st_mode,
                stat.S_IROTH | stat.S_ISGID | stat.S_IRGRP | stat.S_IWGRP
                | stat.S_IWUSR | stat.S_IRUSR | stat.S_IFREG)

    @defer.inlineCallbacks
    def test_upload_isolation(self):
        """Check if txpkgupload isolates the uploads properly.

        Upload should be done atomically, i.e., txpkgupload should isolate
        the context according to each connection/session.
        """
        # Perform a pair of sessions with distinct connections in time.
        conn_one = yield self.server.getClient()
        yield self.server.createFile(conn_one, "test", "ONE")
        yield self.server.disconnect(conn_one)
        yield self.server.waitForClose(1)

        conn_two = yield self.server.getClient()
        yield self.server.createFile(conn_two, "test", "TWO")
        yield self.server.disconnect(conn_two)
        yield self.server.waitForClose(2)

        # Perform a pair of sessions with simultaneous connections.
        conn_three = yield self.server.getClient()
        conn_four = yield self.server.getClient()

        yield self.server.createFile(conn_three, "test", "THREE")

        yield self.server.createFile(conn_four, "test", "FOUR")

        yield self.server.disconnect(conn_three)
        yield self.server.waitForClose(3)

        yield self.server.disconnect(conn_four)
        yield self.server.waitForClose(4)

        # Build a list of directories representing the 4 sessions.
        upload_dirs = [leaf for leaf in sorted(os.listdir(self.server.fsroot))
                       if not leaf.startswith(".")]
        self.assertEqual(len(upload_dirs), 4)

        # Check the contents of files on each session.
        expected_contents = ['ONE', 'TWO', 'THREE', 'FOUR']
        for index in range(4):
            content = open(os.path.join(
                self.server.fsroot, upload_dirs[index], "test")).read()
            self.assertEqual(content, expected_contents[index])


class TestPkgUploadServiceMakerFTP(TestPkgUploadServiceMakerMixin, TestCase):
    """FTP tests for `txpkgupload.plugin.PkgUploadServiceMaker`.

    Includes functional tests of the services.

    SFTP doesn't have the concept of the server changing directories, since
    clients will only send absolute paths, so we only include these tests
    for FTP.
    """

    server_factory = FTPServer

    @defer.inlineCallbacks
    def test_change_directory_anonymous(self):
        # Check that FTP access with an anonymous user works.
        client = yield self.server.getAnonClient()
        yield self.test_change_directory(client)

    @defer.inlineCallbacks
    def test_change_directory(self, client=None):
        """Check automatic creation of directories 'cwd'ed in.

        Also ensure they are created with proper permission (g+rwxs)
        """
        if client is None:
            client = yield self.server.getClient()
        yield client.cwd('foo/bar')

        yield self.server.disconnect(client)
        yield self.server.waitForClose()

        wanted_path = self._uploadPath('foo/bar')
        self.assertTrue(os.path.exists(wanted_path))
        self.assertEqual(os.stat(wanted_path).st_mode, 042775)


class TestPkgUploadServiceMakerSFTP(TestPkgUploadServiceMakerMixin, TestCase):
    """SFTP tests for `txpkgupload.plugin.PkgUploadServiceMaker`.

    Includes functional tests of the services.
    """

    server_factory = SFTPServer

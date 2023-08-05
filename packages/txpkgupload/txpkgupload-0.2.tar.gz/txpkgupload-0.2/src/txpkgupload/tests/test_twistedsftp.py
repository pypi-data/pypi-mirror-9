# Copyright 2010-2011 Canonical Ltd.  This software is licensed under the
# GNU Affero General Public License version 3 (see the file LICENSE).

"""Tests for twistedsftp."""

__metaclass__ = type

import os

import fixtures
from lazr.sshserver.sftp import FileIsADirectory
import testtools

from txpkgupload.twistedsftp import SFTPServer


class MockAvatar:

    def __init__(self, fs_root, temp_dir):
        self.fs_root = fs_root
        self.temp_dir = temp_dir


class TestSFTPServer(testtools.TestCase):

    def setUp(self):
        temp_dir = self.useFixture(fixtures.TempDir()).path
        fs_root = os.path.join(temp_dir, "incoming")
        temp_dir = os.path.join(temp_dir, "tmp-incoming")
        os.mkdir(fs_root)
        os.mkdir(temp_dir)
        self.sftp_server = SFTPServer(MockAvatar(fs_root, temp_dir))
        super(TestSFTPServer, self).setUp()

    def assertPermissions(self, expected, file_name):
        observed = os.stat(file_name).st_mode
        self.assertEqual(
            expected, observed, "Expected %07o, got %07o, for %s" % (
                expected, observed, file_name))

    def test_gotVersion(self):
        # gotVersion always returns an empty dict, since the server does not
        # support any extended features. See ISFTPServer.
        extras = self.sftp_server.gotVersion(None, None)
        self.assertEquals(extras, {})

    def test_mkdir_and_rmdir(self):
        self.sftp_server.makeDirectory('foo/bar', None)
        self.assertEqual(
            os.listdir(os.path.join(self.sftp_server._current_upload))[0],
            'foo')
        dir_name = os.path.join(self.sftp_server._current_upload, 'foo')
        self.assertEqual(os.listdir(dir_name)[0], 'bar')
        self.assertPermissions(040775, dir_name)
        self.sftp_server.removeDirectory('foo/bar')
        self.assertEqual(
            os.listdir(os.path.join(self.sftp_server._current_upload,
            'foo')), [])
        self.sftp_server.removeDirectory('foo')
        self.assertEqual(
            os.listdir(os.path.join(self.sftp_server._current_upload)), [])

    def test_file_creation(self):
        upload_file = self.sftp_server.openFile('foo/bar', None, None)
        upload_file.writeChunk(0, "This is a test")
        file_name = os.path.join(self.sftp_server._current_upload, 'foo/bar')
        test_file = open(file_name, 'r')
        self.assertEqual(test_file.read(), "This is a test")
        test_file.close()
        self.assertPermissions(0100644, file_name)
        dir_name = os.path.join(self.sftp_server._current_upload, 'bar/foo')
        os.makedirs(dir_name)
        upload_file = self.sftp_server.openFile('bar/foo', None, None)
        err = self.assertRaises(
            FileIsADirectory, upload_file.writeChunk, 0, "This is a test")
        self.assertEqual("File is a directory: '%s'" % dir_name, str(err))

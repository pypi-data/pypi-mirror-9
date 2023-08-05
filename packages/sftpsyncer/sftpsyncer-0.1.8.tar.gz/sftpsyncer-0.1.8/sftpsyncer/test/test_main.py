# -*- coding: utf-8 -*-

import unittest
from subprocess import Popen, check_output
import time
import sys
import os
from contextlib import contextmanager
import uuid
import paramiko
import logging

from sftpsyncer.sftpagent import SyncAgent
import sftpsyncer.exceptions

logger = logging.getLogger(name=__name__)

try:
    import sftpserver  # noqa
except:
    sys.exit("\nYou're missing one or more test requirements. Please install "
             "via:\n\npip install -r test_requirements.txt")


@contextmanager
def cd(newdir):
    prevdir = os.getcwd()
    os.chdir(newdir)
    try:
        yield
    finally:
        os.chdir(prevdir)


def create_tmp_dir(dir_type):
    dirname = generate_tmp_dir_name(dir_type)
    os.mkdir(dirname)
    return dirname


def generate_tmp_dir_name(dir_type):
    dirname = "/tmp/sftpsynctest_%s_%s" % (dir_type, uuid.uuid4())
    return dirname


class TestFileOps(unittest.TestCase):
    KEY = "/tmp/sftpsyncer_rsakey_%s" % uuid.uuid4()
    KEYPASS = ""
    create_key = check_output(
        ["ssh-keygen", "-b", "2048", "-t", "rsa", "-f", KEY, "-N",
         KEYPASS])
    PORT = 3373

    def setUp(self):
        self.sftpproc = None

        self.sftp_file_root = generate_tmp_dir_name("sftproot")
        os.mkdir(self.sftp_file_root)
        self._start_sftp_server()

    def tearDown(self):
        self._stop_sftp_server()

    def _start_sftp_server(self):
        sftpbin = check_output(["which", "sftpserver"]).replace("\n", "")
        with cd(self.sftp_file_root):
            self.sftpproc = Popen([sftpbin, "--host", "localhost", "-k",
                                   self.KEY, "-p", str(self.PORT), "-l",
                                   "CRITICAL"])
        time.sleep(0.1)

    def _stop_sftp_server(self):
        self.sftpproc.terminate()

    def _localised_remote_path(self, path):
        return os.path.join(self.sftp_file_root, path.lstrip("/"))

    def _localised_remote_file_path(self, path, file):
        return os.path.join(self._localised_remote_path(path), file)

    def test_sftpserver_working(self):
        # pkey = paramiko.RSAKey.from_private_key_file(KEY, KEYPASS)
        transport = paramiko.Transport(('localhost', self.PORT))
        transport.connect(username='admin', password="")
        sftp = paramiko.SFTPClient.from_transport(transport)
        dirs = sftp.listdir('.')
        self.assertEqual(dirs, [])

    def test_connection_failure(self):
        remote_root = "/repo"
        local_root = create_tmp_dir("localroot")

        try:
            sa = SyncAgent(hostname="something.localhost", host_port=60000,
                           username="theuser", key_path=self.KEY,
                           local_root=local_root, remote_root=remote_root)
            sa.connect()
        except sftpsyncer.exceptions.ConnectionError:
            assert(True)
        else:
            assert(False)
        sa.disconnect()

    def test_no_such_local_dir(self):
        remote_root = "/repo"
        local_root = "No such dir here"

        try:
            SyncAgent(hostname="localhost", host_port=self.PORT,
                      username="theuser", key_path=self.KEY,
                      local_root=local_root, remote_root=remote_root)
        except sftpsyncer.exceptions.LocalCacheDirNotFound:
            assert(True)
        else:
            assert(False)

    def test_str_port(self):
        remote_root = "/repo"
        local_root = create_tmp_dir("localroot")

        SyncAgent(hostname="localhost", host_port="2222",
                  username="theuser", key_path=self.KEY,
                  local_root=local_root, remote_root=remote_root)

    def test_mkdir_p_basic(self):
        local_root = create_tmp_dir("localroot")
        remote_root = "/my/test/dir/"

        sa = SyncAgent(hostname="localhost", host_port=self.PORT,
                       username="theuser", key_path=self.KEY,
                       local_root=local_root, remote_root=remote_root)

        sa.mkdir_p(remote_root)
        remote_absolute_path = self._localised_remote_path(remote_root)
        logger.debug(self.sftp_file_root)
        logger.debug("Remote target path: %s" % remote_absolute_path)
        self.assertTrue(os.path.isdir(remote_absolute_path))
        sa.disconnect()

    def test_mkdir_p_empty(self):
        local_root = create_tmp_dir("localroot")
        remote_root = ""

        sa = SyncAgent(hostname="localhost", host_port=self.PORT,
                       username="theuser", key_path=self.KEY,
                       local_root=local_root, remote_root=remote_root)

        try:
            sa.mkdir_p(remote_root)
            sa.disconnect()
        except sftpsyncer.exceptions.RemoteDirNotCreated:
            assert(True)
        else:
            assert(False)

    def test_mkdir_p_invalid_chars(self):
        pass

    def test_local_no_file_sync(self):
        remote_root = "/repo"
        local_root = create_tmp_dir("localroot")

        sa = SyncAgent(hostname="localhost", host_port=self.PORT,
                       username="theuser", key_path=self.KEY,
                       local_root=local_root, remote_root=remote_root)
        sa.push()
        sa.disconnect()

    def test_local_single_sync_unicode_file(self):
        file_name = "香港.txt"
        remote_root = "/repo"
        local_root = create_tmp_dir("localroot")

        with open(os.path.join(local_root, file_name), "wb") as f:
            f.write("test data")

        sa = SyncAgent(hostname="localhost", host_port=self.PORT,
                       username="theuser", key_path=self.KEY,
                       local_root=local_root, remote_root=remote_root)
        sa.upload_queue.add(file_name)
        sa.push()
        sa.disconnect()

        remote_file_path = self._localised_remote_file_path(
            remote_root, file_name)
        remote_fh = open(remote_file_path, "r")
        self.assertEqual(remote_fh.read(), "test data")

    def test_local_single_unicode_dir(self):
        file_name = "myfile.txt"
        remote_root = "/日本"
        local_root = create_tmp_dir("localroot")

        with open(os.path.join(local_root, file_name), "wb") as f:
            f.write("test data")

        sa = SyncAgent(hostname="localhost", host_port=self.PORT,
                       username="theuser", key_path=self.KEY,
                       local_root=local_root, remote_root=remote_root)
        sa.upload_queue.add(file_name)
        sa.push()
        sa.disconnect()

        remote_file_path = self._localised_remote_file_path(
            remote_root, file_name)
        remote_fh = open(remote_file_path, "r")
        self.assertEqual(remote_fh.read(), "test data")

    def test_local_single_sync_root(self):
        file_name = "myfile.txt"
        remote_root = "/"
        local_root = create_tmp_dir("localroot")

        with open(os.path.join(local_root, file_name), "wb") as f:
            f.write("test data")

        sa = SyncAgent(hostname="localhost", host_port=self.PORT,
                       username="theuser", key_path=self.KEY,
                       local_root=local_root, remote_root=remote_root)
        sa.upload_queue.add(file_name)
        sa.push()
        sa.disconnect()

        remote_file_path = self._localised_remote_file_path(
            remote_root, file_name)
        remote_fh = open(remote_file_path, "r")
        self.assertEqual(remote_fh.read(), "test data")

    def test_local_multi_sync(self):
        file_names = ["myfile.txt", "anotherfile.txt"]
        remote_root = "/repo"
        local_root = create_tmp_dir("localroot")

        for file_name in file_names:
            with open(os.path.join(local_root, file_name), "w") as f:
                f.write("test data")

        sa = SyncAgent(hostname="localhost", host_port=self.PORT,
                       username="theuser", key_path=self.KEY,
                       local_root=local_root, remote_root=remote_root)
        for file_name in file_names:
            sa.upload_queue.add(file_name)
        sa.push()
        sa.disconnect()

        for file_name in file_names:
            remote_file_path = self._localised_remote_file_path(
                remote_root, file_name)
            remote_fh = open(remote_file_path, "r")
            self.assertEqual(remote_fh.read(), "test data")

    def test_local_single_sync(self):
        file_name = "myfile.txt"
        remote_root = "/repo"
        local_root = create_tmp_dir("localroot")

        with open(os.path.join(local_root, file_name), "wb") as f:
            f.write("test data")

        sa = SyncAgent(hostname="localhost", host_port=self.PORT,
                       username="theuser", key_path=self.KEY,
                       local_root=local_root, remote_root=remote_root)
        sa.upload_queue.add(file_name)
        sa.push()
        sa.disconnect()

        remote_file_path = self._localised_remote_file_path(
            remote_root, file_name)
        remote_fh = open(remote_file_path, "r")
        self.assertEqual(remote_fh.read(), "test data")

    def test_local_single_sync_fake(self):
        file_name = "myfile.txt"
        remote_root = "/repo"
        local_root = create_tmp_dir("localroot")

        with open(os.path.join(local_root, file_name), "wb") as f:
            f.write("test data")

        sa = SyncAgent(hostname="localhost", host_port=self.PORT,
                       username="theuser", key_path=self.KEY,
                       local_root=local_root, remote_root=remote_root,
                       fake_connection=True)
        sa.upload_queue.add(file_name)
        sa.push()

        sa.pull_dir("*")

        # this is cached, we should be able to open
        data = sa.open(file_name)
        sa.disconnect()
        self.assertEqual(data.read(), "test data")

    def test_local_dir_push(self):
        remote_root = "/deep"
        local_root = create_tmp_dir("localroot")

        sa = SyncAgent(hostname="localhost", host_port=self.PORT,
                       username="theuser", key_path=self.KEY,
                       local_root=local_root, remote_root=remote_root)

        dir_nest = ""
        for dir_ in ["a", "b", "c"]:
            dir_nest = dir_nest + dir_ + "/"
            local_dir_path = os.path.join(local_root, dir_nest)
            os.mkdir(local_dir_path)
            for file_ in ["1", "2", "3"]:
                local_file_path = os.path.join(local_dir_path, file_)
                logger.debug(local_file_path)
                with open(local_file_path, "w") as f:
                    f.write("test data")
        sa.upload_queue.add_dir(".")
        sa.push()
        sa.disconnect()

        dir_nest = ""
        for dir_ in ["a", "b", "c"]:
            dir_nest = dir_nest + dir_ + "/"

            for file_ in ["1", "2", "3"]:
                remote_abs_file_path = self._localised_remote_file_path(
                    os.path.join(remote_root, dir_nest), file_)
                logger.debug(remote_abs_file_path)
                with open(remote_abs_file_path, "r") as f:
                    self.assertEqual(f.read(), "test data")

    def test_local_dir_pull(self):
        remote_root = "/deep"
        local_root = create_tmp_dir("localroot")

        sa = SyncAgent(hostname="localhost", host_port=self.PORT,
                       username="theuser", key_path=self.KEY,
                       local_root=local_root, remote_root=remote_root)

        # create files in remote SFTP server
        dir_nest = ""
        for dir_ in ["a", "b", "c"]:
            dir_nest = dir_nest + dir_ + "/"
            remote_abs_file_path = self._localised_remote_path(
                os.path.join(remote_root, dir_nest))
            logger.debug("makedirs %s" % remote_abs_file_path)
            os.makedirs(remote_abs_file_path)
            for file_ in ["1", "2", "3"]:
                remote_abs_file_path = self._localised_remote_file_path(
                    os.path.join(remote_root, dir_nest), file_)
                logger.debug(remote_abs_file_path)
                with open(remote_abs_file_path, "w") as f:
                    f.write("test data")
        sa.pull_dir("*")
        sa.disconnect()

        # verify local cache files
        dir_nest = ""
        for dir_ in ["a", "b", "c"]:
            dir_nest = dir_nest + dir_ + "/"
            local_dir_path = os.path.join(local_root, dir_nest)
            for file_ in ["1", "2", "3"]:
                local_file_path = os.path.join(local_dir_path, file_)
                logger.debug("Testing local file %s" % local_file_path)
                with open(local_file_path, "r") as f:
                    self.assertEqual(f.read(), "test data")

    def test_get_remote_file(self):
        file_name = "myfile.txt"
        remote_root = "/repo/other/dir"
        local_root = create_tmp_dir("localroot")

        os.makedirs(self._localised_remote_path(remote_root))
        # simulate a file already there
        remote_abs_path = self._localised_remote_file_path(
            remote_root, file_name)
        logger.debug("Remote localised path: %s" % remote_abs_path)
        with open(remote_abs_path, "w") as f:
            f.write("test data")

        sa = SyncAgent(hostname="localhost", host_port=self.PORT,
                       username="theuser", key_path=self.KEY,
                       local_root=local_root, remote_root=remote_root)

        self.assertFalse(os.path.exists(os.path.join(local_root, file_name)))
        data = sa.open(file_name)
        sa.disconnect()
        self.assertEqual(data.read(), "test data")
        self.assertTrue(os.path.exists(os.path.join(local_root, file_name)))

    def test_get_remote_file_deep(self):
        nest_path = "x/y/z/"
        file_name = os.path.join(nest_path, "myfile.txt")
        remote_root = "/repo/other/dir"
        local_root = create_tmp_dir("localroot")

        os.makedirs(self._localised_remote_file_path(remote_root, nest_path))
        # simulate a file already there
        remote_abs_path = self._localised_remote_file_path(
            remote_root, file_name)
        logger.debug("Remote localised path: %s" % remote_abs_path)
        with open(remote_abs_path, "w") as f:
            f.write("test data")

        sa = SyncAgent(hostname="localhost", host_port=self.PORT,
                       username="theuser", key_path=self.KEY,
                       local_root=local_root, remote_root=remote_root)

        self.assertFalse(os.path.exists(os.path.join(local_root, file_name)))
        logger.debug("Opening %s" % file_name)
        data = sa.open(file_name)
        self.assertEqual(data.read(), "test data")
        self.assertTrue(os.path.exists(os.path.join(local_root, file_name)))
        sa.disconnect()

    def test_get_remote_dir(self):
        pass

    def test_file_missing_everywhere(self):
        file_name = "myfile.txt"
        remote_root = "/repo"
        local_root = create_tmp_dir("localroot")

        sa = SyncAgent(hostname="localhost", host_port=self.PORT,
                       username="theuser", key_path=self.KEY,
                       local_root=local_root, remote_root=remote_root)

        self.assertFalse(os.path.exists(os.path.join(local_root, file_name)))
        try:
            sa.open(file_name)
        except sftpsyncer.exceptions.FileNotFound:
            assert(True)
        else:
            assert(False)
        sa.disconnect()

    def test_ignore_remote_if_cached(self):
        """
        If we have the file locally, we don't check remotely. Note that the
        file is not automatically uploaded - this must be done manually.
        """
        file_name = "myfile.txt"
        remote_root = "/repo"
        local_root = create_tmp_dir("localroot")

        with open(os.path.join(local_root, file_name), "wb") as f:
            f.write("test data")

        sa = SyncAgent(hostname="localhost", host_port=self.PORT,
                       username="theuser", key_path=self.KEY,
                       local_root=local_root, remote_root=remote_root)
        sa.upload_queue.add(file_name)
        sa.push()

        remote_fh = sa.open(file_name)
        self.assertEqual(remote_fh.read(), "test data")
        sa.disconnect()

    def test_race_condition_between_queue_and_transfer(self):
        file_name = "myfile.txt"
        remote_root = "repo"
        local_root = create_tmp_dir("localroot")
        local_file_path = os.path.join(local_root, file_name)

        with open(local_file_path, "w") as f:
            f.write("test data")

        sa = SyncAgent(hostname="localhost", host_port=self.PORT,
                       username="theuser", key_path=self.KEY,
                       local_root=local_root, remote_root=remote_root)
        sa.upload_queue.add(file_name)
        # file is remove before committing
        os.unlink(local_file_path)
        try:
            sa.push()
        except:
            assert(True)
        else:
            assert(False)
        sa.disconnect()

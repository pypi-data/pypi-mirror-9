from functools import wraps
import logging
import paramiko
import errno
from stat import S_ISDIR
import os.path
from .exceptions import (LocalFileNotFound, FileNotFound, ConnectionError,
                         LocalCacheDirNotFound, TransferError,
                         RemoteDirNotCreated)

logger = logging.getLogger(name=__name__)

ROOT_ALIASES = ["*", "/", "."]


class SyncAgentLocalQueue(object):
    def __init__(self, local_root):
        self.queued_files = []

        self.local_root = local_root

    def add(self, rel_file_path):
        file_path = os.path.join(self.local_root, rel_file_path)
        logger.debug("Adding file: %s" % file_path)

        if not os.path.exists(file_path):
            raise LocalFileNotFound(
                "Could not add file: %s not found" % file_path)

        self.queued_files.append(rel_file_path)

    def _add_wrapper(self, callback, abs_dir_name, names):
        rel_dir_path = abs_dir_name.replace(self.local_root + "/", "")
        for name in names:
            abs_file_path = os.path.join(abs_dir_name, name)
            if os.path.isfile(abs_file_path):
                rel_file_path = os.path.join(rel_dir_path, name)
                logger.debug("Adding to package: %s" % rel_file_path)
                self.add(rel_file_path)
                if callback:
                    callback(rel_file_path)

    def add_dir(self, rel_dir_path, file_callback=None):
        dir_path = None
        if rel_dir_path in ROOT_ALIASES:
            # add everything under root
            dir_path = self.local_root
        else:
            dir_path = os.path.join(self.local_root, rel_dir_path)
        logger.debug("Walking dir: %s" % dir_path)
        os.path.walk(dir_path, self._add_wrapper, file_callback)

    def clear_queue(self):
        self.queued_files = []

    def __iter__(self):
        return self.queued_files.__iter__()

class MockTransport(object):
    def close(*args, **kwargs):
        pass


class MockConn(object):
    def put(*args, **kwargs):
        pass

    def rename(*args, **kwargs):
        pass

    def listdir(*args, **kwargs):
        return []

    def chdir(*args, **kwargs):
        pass

    def mkdir(*args, **kwargs):
        pass

    def get(*args, **kwargs):
        pass

    def close(*args, **kwargs):
        pass

class SyncAgent(object):
    def __init__(self, hostname=None, host_port=22, username=None,
                 key_path=None, local_root=None, remote_root=None,
                 fake_connection=False):
        self.hostname = hostname
        self.host_port = int(host_port)
        self.username = username
        self.key_path = key_path
        self.local_root = local_root
        self.remote_root = remote_root

        if not os.path.isdir(self.local_root):
            raise LocalCacheDirNotFound(
                "Couldn't find local_root at %s: make sure this is "
                "created" % local_root)

        self.upload_queue = SyncAgentLocalQueue(local_root)
        self.transport = None
        self.conn = None

        # fake_connections just neuters any SFTP commands we use. It's designed
        # for limited testing when a test SFTP server is unavailable.
        if fake_connection:
            self.transport = MockTransport()
            self.conn = MockConn()

    def _rel_path_to_abs_local(self, path):
        path = path.lstrip("/")
        return os.path.join(self.local_root, path)

    def _rel_path_to_abs_remote(self, path):
        path = path.lstrip("/")
        return os.path.join(self.remote_root, path)

    def ensure_connected(func):
        @wraps(func)
        def connect_wrapper(self, *args, **kwargs):
            self.connect()
            return func(self, *args, **kwargs)
        return connect_wrapper

    def connect(self):
        if not self.conn:
            try:
                pkey = paramiko.RSAKey.from_private_key_file(self.key_path)
                self.transport = paramiko.Transport((self.hostname,
                    self.host_port))
                self.transport.connect(username=self.username, pkey=pkey)
                self.transport.use_compression(compress=True)
                self.conn = paramiko.SFTPClient.from_transport(self.transport)
            except Exception as e:
                raise ConnectionError(
                    "Couldn't connect to SFTP server: %s" % e)

    def disconnect(self):
        if self.conn:
            try:
                self.conn.close()
            except Exception as e:
                logger.debug("Couldn't terminate SFTP connection cleanly: %s"
                    % e)
        if self.transport:
            try:
                self.transport.close()
            except Exception as e:
                logger.debug("Couldn't terminate SFTP transport cleanly: %s"
                    % e)

    @ensure_connected
    def push(self):
        for file in self.upload_queue:
            local_file_path = os.path.join(self.local_root, file)
            remote_temp_file_path = os.path.join(self.remote_root,
                                                 "%s.part" % file)
            remote_file_path = os.path.join(self.remote_root, file)
            try:
                assert(os.path.exists(local_file_path))
                remote_dir_path, _ = os.path.split(remote_file_path)
                self.mkdir_p(remote_dir_path)
                self.conn.put(local_file_path, remote_temp_file_path,
                              confirm=True)
                self.conn.rename(remote_temp_file_path, remote_file_path)
            except AssertionError as e:
                raise LocalFileNotFound("Error during commit: %s missing"
                                        % local_file_path)
            except Exception as e:
                raise TransferError("Couldn't transfer %s: %s" % (
                    local_file_path, e))

    @ensure_connected
    def pull_dir(self, rel_path):
        if rel_path in ROOT_ALIASES:
            # add everything under root
            remote_abs_dir_path = self.remote_root
            rel_path = ""
        else:
            remote_abs_dir_path = self._rel_path_to_abs_remote(rel_path)

        files = self.conn.listdir(remote_abs_dir_path)

        for file in files:
            remote_abs_file_path = os.path.join(remote_abs_dir_path, file)
            remote_rel_file_path = os.path.join(rel_path, file)
            logger.debug("local_file_path %s, %s, %s" %
                         (self.local_root, rel_path, file))
            local_file_path = os.path.join(
                self._rel_path_to_abs_local(rel_path), file)
            if self.is_remote_dir(remote_abs_file_path):
                logger.debug("mkdir %s and pull %s" %
                             (local_file_path, remote_abs_file_path))
                os.makedirs(local_file_path)
                self.pull_dir(remote_rel_file_path)
            else:
                logger.debug("Getting %s to %s" %
                             (remote_abs_file_path, local_file_path))
                self.conn.get(remote_abs_file_path, local_file_path)

    @ensure_connected
    def is_remote_dir(self, path):
        try:
            logger.debug("Is %s a dir?" % path)
            return S_ISDIR(self.conn.stat(path).st_mode)
        except IOError:
            logger.debug("Not a dir")
            return False

    @ensure_connected
    def mkdir_p(self, remote_path):
        logger.debug("mkdir_p:remote_path %s" % remote_path)
        if remote_path == '/':
            # absolute path so change directory to root
            self.conn.chdir('/')
            return
        if not remote_path:
            # top-level relative directory must exist
            raise RemoteDirNotCreated("You must specify a path")
        _, basename = os.path.split(remote_path)
        self.mkdir_p(os.path.dirname(remote_path))
        try:
            self.conn.chdir(basename)
        except IOError:
            logger.debug("mkdir_p:mkdir %s" % remote_path)
            self.conn.mkdir(basename)
            self.conn.chdir(basename)

    @ensure_connected
    def open(self, path, mode="r"):
        """
        Given a relative file path, check the local cache. If present, return a
        filehandle. If not in the local cache, check the remote SFTP server. If
        present remotely, get and place in the local cache. If missing
        remotely, raise a FileNotFound exception.
        """

        local_file_path = self._rel_path_to_abs_local(path)
        local_file_dir = os.path.dirname(local_file_path)
        logger.debug("Checking local_file_path: %s" % local_file_path)
        if not os.path.isfile(local_file_path):
            remote_file_path = self._rel_path_to_abs_remote(path)
            logger.debug("Local file missing get remote: %s"
                         % remote_file_path)
            try:
                os.makedirs(local_file_dir)
            except OSError as e:
                if e.errno == errno.EEXIST:
                    pass
            try:
                self.conn.get(remote_file_path, local_file_path)
            except IOError as e:
                raise FileNotFound("%s not found locally or remotely: %s" %
                                   (path, e))
        try:
            return open(local_file_path, mode)
        except IOError:
            raise

class LocalFileNotFound(Exception):
    """
    This file could not be found locally, when we expected it to be.
    """
    pass


class LocalCacheDirNotFound(Exception):
    """
    We couldn't find a local cache dir to use
    """
    pass


class FileNotFound(Exception):
    """
    This file could not be found locally or remotely
    """
    pass


class ConnectionError(Exception):
    """
    Error connecting to SFTP server
    """
    pass


class TransferError(Exception):
    """
    Connected, but some other problem transferring file
    """
    pass


class RemoteDirNotCreated(Exception):
    """
    Remote dir could not be created
    """
    pass

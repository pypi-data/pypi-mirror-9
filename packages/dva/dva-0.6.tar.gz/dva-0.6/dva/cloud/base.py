"""
Basic abstract cloud class and exceptions
"""
import contextlib

class TemporaryCloudException(Exception):
    """
    Temporary exception, 'try again'
    """
    pass


class PermanentCloudException(Exception):
    """
    Permanent exception, no need to try any more
    """
    pass


class SkipCloudException(Exception):
    """
    'Skip' exception - missing hardware in the region,...
    """
    pass


class UnknownCloudException(Exception):
    """
    Unknown exception, 'try again' but increase ntry
    """
    pass


class AbstractCloud(object):
    """
    Abstract cloud class
    """
    cloud = 'default'
    mandatory_fields = []

    def __init__(self, logger, maxwait):
        self.logger = logger
        self.maxwait = maxwait

    def set_default_params(self, params, cloud_access_config):
        raise NotImplementedError

    def create(self, params):
        raise NotImplementedError

    def terminate(self, params):
        raise NotImplementedError

    def get_console_output(self, params):
        raise NotImplementedError

    def update(self, params):
        raise NotImplementedError

    def get_connection(self, params):
        raise NotImplementedError

    @contextlib.contextmanager
    def connection(self, params):
        raise NotImplementedError

    def get_image(self, params):
        raise NotImplementedError

    def get_instance(self, params):
        raise NotImplementedError

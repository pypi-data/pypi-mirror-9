import logging


class Echo(object):
    """
    A debug resource which will echo it's payload to the log.
    """

    def __init__(self, name):
        self.name = name
        self.logger = logging.getLogger(__name__)

    def invoke(self, *args, **kwargs):
        self.logger.info(
            'ECHO[{}]: args={} kwargs={}'.format(self.name, args, kwargs)
        )
        return True


class Failure(object):
    """
    A debug resource which will always fail, and therefore re-queue.
    """
    def __init__(self, name):
        self.name = name
        self.logger = logging.getLogger(__name__)

    def invoke(self, *args, **kwargs):
        self.logger.info(
            'FAILURE[{}]: failing and re-queueing...'.format(self.name)
        )
        return False

import logging

from .consumer import Consumer
from .processor import Processor
from .message import AbstractMessage
from .resource_factory import ResourceFactory


logging.getLogger(__name__).addHandler(logging.NullHandler())


class AbstractResource(object):
    """
    Base class for a resource.
    Do not inherit, just implement the interface.
    """

    logger = None

    def invoke(self, *args, **kwargs):
        """
        Invokes the named action with the supplied parameters.
        """
        raise NotImplementedError


__all__ = [
    'Consumer', 'Processor',
    'AbstractMessage', 'AbstractResource',
    'ResourceFactory',
]

import logging
import StringIO


spy_logger = logging.getLogger(__name__)


def spy_handler():
    return spy_logger.handlers[0]

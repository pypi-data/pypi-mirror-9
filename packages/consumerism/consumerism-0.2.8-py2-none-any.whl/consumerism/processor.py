import logging


class Processor(object):
    """
    Processes SQS messages.
    """

    def __init__(self, resource_factory, message_class):
        """
        Create a new processor.
        The resource factory should return objects which implement the
        AbstractResource interface.
        """
        self.resource_factory = resource_factory
        self.message_class = message_class
        self.logger = logging.getLogger(__name__)

    def process(self, body, log_handler=None):
        """
        Dispatch the JSON message to the correct Resource handler and
        perform the requested action.
        Optionally attach a supplied log handler to the resource created
        to fulfill the processing request.
        """
        try:
            message = self.message_class(body)
            resource_name = message.resource_name()
            invoke_args, invoke_kwargs = message.invoke_args()
        except Exception as e:
            # Discard malformed messages
            self.logger.warn(
                'Discarding malformed message, missing field "{}", body={}'
                .format(e, body))
            return True

        try:
            resource = self.resource_factory.new(resource_name)
        except:
            self.logger.critical(
                'Could not create resource "{}", body={}'
                .format(resource_name, body),
                exc_info=True)
            return False

        try:
            with ResourceActionLogger(log_handler, resource):
                result = resource.invoke(*invoke_args, **invoke_kwargs)
        except:
            self.logger.critical(
                'Encountered exception while invoking resource "{}"'
                .format(resource_name),
                exc_info=True
            )
            return False

        return result


class ResourceActionLogger(object):
    def __init__(self, handler, resource):
        self.handler = handler
        self.resource = resource

    def get_resource_logger(self):
        module = self.resource.__module__
        if module is not None:
            name = module.split('.')[0]
            return logging.getLogger(name)
        elif hasattr(self.resource, 'logger'):
            name = self.resource.logger.name.split('.')[0]
            return logging.getLogger(name)
        else:
            return None

    def __enter__(self):
        logger = self.get_resource_logger()
        if logger:
            logger.addHandler(self.handler)

    def __exit__(self, type, value, traceback):
        logger = self.get_resource_logger()
        if logger:
            logger.removeHandler(self.handler)

import functools
import inspect
import logging


class ResourceFactory(object):
    def __init__(self):
        self.resource_map = {}
        self.logger = logging.getLogger(__name__)

    def register(self, name, cls, **kwargs):
        """
        Register the given class with the factory.
        Any kwargs specified will be matched against the classes constructor
        arguments and automatically injected.
        """
        argspec = inspect.getargspec(cls.__init__)
        ctr_args = {k: v for k, v in kwargs.iteritems() if k in argspec.args}

        # A faux constructor for the class with DI from the supplied kwargs
        def constructor(cls, ctr_args, *args, **kwargs):
            kwargs.update(ctr_args)
            return cls(*args, **kwargs)

        self.resource_map[name] = functools.partial(constructor, cls, ctr_args)
        self.logger.info('Registered resource "{}"'.format(name))

    def new(self, name):
        resource_cls = self.resource_map.get(name, NoopResource)
        return resource_cls(name=name)


class NoopResource(object):
    """
    A no-operation resource which will simply print the fact that
    """
    def __init__(self, name):
        self.name = name
        self.logger = logging.getLogger(__name__)

    def invoke(self, *args, **kwargs):
        self.logger.warn(
            'NoopResource invoked for "{}" with arguments: args={} kwargs={}'
            .format(self.name, args, kwargs)
        )
        return True

class AbstractResource(object):  # pragma: nocover
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

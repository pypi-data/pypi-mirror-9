class AbstractMessage(object):  # pragma: no cover
    """
    Base class for processed messages.
    """

    def __init__(self, body_dict):
        self.message = body_dict

    def resource_name(self):
        """
        Returns the name of the resource which should act upon this message.
        """
        raise NotImplementedError

    def invoke_args(self):
        """
        Returns arguments which should be passed to the resource's invoke
        method.
        """
        raise NotImplementedError

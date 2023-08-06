class RetryStrategy(object):  # pragma: nocover
    """
    Base class for retry strategies.
    """
    def should_retry(self, succeeded, attempt):
        """
        Returns True if a message should be eventually retried, given the
        most recent result and number of attempts at processing the message.
        """
        raise NotImplementedError

    def __repr__(self):
        return 'Retry Strategy logic descriptions goes here'


class LimitedRetries(RetryStrategy):
    """
    A strategy to limit the number of time a message is processes.
    Set limit to -1 for unlimited retries.
    """
    def __init__(self, limit):
        self.limit = limit

    def should_retry(self, succeeded, attempt):
        if succeeded:
            return False
        elif self.limit < 0:
            return True
        else:
            return attempt < self.limit

    def __repr__(self):  # pragma: nocover
        if self.limit < 0:
            return 'Retry strategy allows unlimited processing attempts'
        elif self.limit == 1:
            return 'Strategy configured to never retry'
        else:
            return 'Retry strategy limited to {} attempts'.format(self.limit)


UnlimitedRetries = LimitedRetries(-1)

NeverRetry = LimitedRetries(1)

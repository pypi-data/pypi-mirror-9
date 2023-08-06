DISABLED = 'disabled'
DEAD = 'dead'
SUCCESS = 'success'
ALL = {DEAD, SUCCESS}


class PersistStrategy(object):
    """
    Strategy to determine when a message should be persisted.

    Configured by configuring which event(s) should cause persistence.
    """
    def __init__(self, events):
        if events is None:
            events = [DISABLED]
        if isinstance(events, basestring):
            events = [events]
        if not isinstance(events, set):
            events = set(events)

        self.events = events

    def should_persist(self, succeeded, will_retry):
        decision = (
            (DISABLED not in self.events)
            and
            (
                (succeeded and SUCCESS in self.events) or
                (not succeeded and not will_retry and DEAD in self.events)
            )
        )
        return decision


class PersistBackend(object):  # pragma: nocover
    """
    Abstract base class for persistence strategies.
    """
    def persist(self, queue, message):
        raise NotImplementedError

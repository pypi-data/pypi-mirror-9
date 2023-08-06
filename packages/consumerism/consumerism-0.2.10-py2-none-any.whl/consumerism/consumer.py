import logging
import StringIO
import time

import boto.sqs
import boto.sqs.jsonmessage


class Consumer(object):
    def __init__(self,
                 region,
                 queue_name,
                 retry_strategy=None,
                 persist_on=None,
                 persist_backend=None,
                 message_class=boto.sqs.jsonmessage.JSONMessage):
        """
        Create an SQS Consumer for the configured queue.

        A `retry_strategy` will be consulted when a message fails processing
        to determine if it should be deleted or requeued. If none is supplied,
        messages will be retried indefinitely.

        The consumer will use the `persist_on` (string or list of events:
        'all', 'dead', 'success') argument to determine when a processed
        message should be persisted via the supplied `persist_backend`.
        """
        self.region = region
        self.queue_name = queue_name
        self.retry_strategy = retry_strategy or LimitedRetries(-1)
        self.persist_on = persist_on
        self.persist_backend = persist_backend
        self.message_class = message_class
        self.logger = logging.getLogger(__name__)

    def connect(self):
        """
        Connect to AWS and return the required boto.sqs.queue.Queue
        """
        sqs = boto.sqs.connect_to_region(self.region)
        queue = sqs.get_queue(self.queue_name)
        queue.set_message_class(self.message_class)
        return queue

    def poll(self, processor, period):
        """
        Polls the queue and then sleeps for a specified period before trying
        again.
        """
        while True:
            self.consume(processor)
            time.sleep(period)

    def consume(self, processor):
        """
        Process messages received on the configured queue using the supplied
        processor function.
        The processor should return True if the message is considered to be
        successfully handled.
        Returns when the queue is empty.
        """
        queue = self.connect()

        while True:
            msgs = queue.get_messages(num_messages=1, attributes='All')
            if not msgs:
                return
            message = msgs[0]

            attempt = int(message.attributes.get('ApproximateReceiveCount', 0))

            # Capture any logging events during the processing of the message
            action_log = StringIO.StringIO()
            handler = logging.StreamHandler(action_log)

            success = processor(message.get_body(), log_handler=handler)
            if success:
                self.logger.debug(
                    'MessageID={} successfully processed '
                    'on attempt={}, deleting.\n'
                    'Action log:\n'
                    '{}'
                    .format(message.id, attempt, action_log.getvalue())
                )
                self.delete(queue, message)

            elif self.retry_strategy.should_delete(attempt):
                self.logger.critical(
                    'Deleting MessageID={} attributes={} '
                    'because: {}\n'
                    'message={}\n'
                    'Action log:\n'
                    '{}'
                    .format(message.id,
                            message.attributes,
                            str(self.retry_strategy),
                            message.get_body(),
                            action_log.getvalue())
                )
                self.delete(queue, message, dead=True)

            else:
                self.logger.warn(
                    'MessageID={} failed to process '
                    'on attempt={}, requeueing.\n'
                    'Action log:\n'
                    '{}'
                    .format(message.id, attempt, action_log.getvalue())
                )

            action_log.close()

    def delete(self, queue, message, dead=False):
        should_persist = (
            (self.persist_on is not None and self.persist_backend is not None)
            and
            (
                ('all' in self.persist_on) or
                (dead and 'dead' in self.persist_on) or
                (not dead and 'success' in self.persist_on)
            )
        )
        if should_persist:
            self.persist_backend.persist(queue, message)

        queue.delete_message(message)


class RetryStrategy(object):
    """
    Base class for retry strategies.
    """
    def should_delete(self, attempt):
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

    def should_delete(self, attempt):
        if self.limit < 0:
            return False
        else:
            return attempt >= self.limit

    def __repr__(self):
        if self.limit < 0:
            return 'Retry strategy allows unlimited processing attempts'
        else:
            return 'Retry strategy limited to {} attempts'.format(self.limit)


class PersistStrategy(object):
    def persist(self, queue, message):
        raise NotImplementedError

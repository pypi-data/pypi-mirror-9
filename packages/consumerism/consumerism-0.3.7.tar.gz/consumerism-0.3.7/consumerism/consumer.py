import logging
import signal
import time

import boto.sqs
import boto.sqs.jsonmessage

from .persist import PersistStrategy
from .retry import UnlimitedRetries
from .utils import LogCapture, GracefulExit


class Consumer(object):
    def __init__(self,
                 region,
                 queue_name,
                 retry_strategy=None,
                 persist_on=None,
                 persist_backend=None,
                 queue_must_exist=True,
                 message_class=boto.sqs.jsonmessage.JSONMessage):
        """
        Create an SQS Consumer for the configured queue.

        A `retry_strategy` will be consulted when a message fails processing
        to determine if it should be deleted or requeued. If none is supplied,
        messages will be retried indefinitely.
        """
        self.region = region
        self.queue_name = queue_name
        self.retry_strategy = retry_strategy or UnlimitedRetries
        self.persist_strategy = PersistStrategy(persist_on)
        self.persist_backend = persist_backend
        self.queue_must_exist = queue_must_exist
        self.message_class = message_class
        self.logger = logging.getLogger(__name__)

        self._shutting_down = False

    def connect(self):
        """
        Connect to AWS and return the required boto.sqs.queue.Queue
        """
        if self._shutting_down:
            return None

        sqs = boto.sqs.connect_to_region(self.region)
        queue = sqs.get_queue(self.queue_name)
        if queue:
            queue.set_message_class(self.message_class)
        elif self.queue_must_exist:
            raise Exception(
                'Consumer expected queue "{}" to exist, but it doesn\'t!'
                .format(self.queue_name)
            )

        return queue

    def shutdown(self, signum, frame):
        # Stop consume() from processing any more messages
        self._shutting_down = True
        self.logger.warning('Caught shutdown signal, waiting for consumer to '
                            'finish processing current message...')

    def poll(self, processor, period):
        """
        Polls the queue and then sleeps for a specified period before trying
        again.
        """
        with GracefulExit(signal.SIGTERM, self.shutdown):
            while True:
                self.consume(self.connect(), processor)
                time.sleep(period)

    def consume(self, queue, processor):
        """
        Process messages received on the configured queue using the supplied
        processor function.
        The processor should return True if the message is considered to be
        successfully handled.
        Returns when the queue is empty.
        """
        while queue is not None:
            msgs = queue.get_messages(num_messages=1, attributes='All')
            if not msgs:
                return
            message = msgs[0]

            attempt = int(message.attributes.get('ApproximateReceiveCount', 0))

            root_logger = logging.getLogger()
            with LogCapture(root_logger) as captured:
                success = processor(message.get_body())

                retry = self.retry_strategy.should_retry(success, attempt)

                persist = self.persist_strategy.should_persist(success, retry)
                if persist:
                    self.persist_backend.persist(queue, message)

                if success or not retry:
                    queue.delete_message(message)

            if success:
                self.logger.debug(
                    'MessageID={id} successfully processed '
                    'on attempt #{n}, deleting.\n'
                    'Captured logs from message processing:\n{log}'
                    .format(id=message.id, n=attempt, log=captured.output())
                )
            elif not retry:
                self.logger.critical(
                    'MessageID={id} is being deleting because {reason}\n'
                    'Captured logs from message processing attempt:\n{log}'
                    .format(reason=self.retry_strategy,
                            id=message.id,
                            log=captured.output())
                )
            else:
                self.logger.warn(
                    'MessageID={id} failed on processing attempt #{n}, '
                    'message will be retried at a later time.\n'
                    'Captured logs from message processing attempt:\n{log}'
                    .format(id=message.id, n=attempt, log=captured.output())
                )

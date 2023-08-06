import logging
import StringIO
import time

import boto.sqs
import boto.sqs.jsonmessage


class Consumer(object):
    def __init__(self, region, queue_name, retry_limit,
                 message_class=boto.sqs.jsonmessage.JSONMessage):
        """
        Create an SQS Consumer for the configured queue.
        """
        self.region = region
        self.queue_name = queue_name
        self.retry_limit = retry_limit
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
            msg = msgs[0]

            attempt = int(msg.attributes.get('ApproximateReceiveCount', 0))

            # Capture any logging events during the processing of the message
            action_log = StringIO.StringIO()
            handler = logging.StreamHandler(action_log)

            success = processor(msg.get_body(), log_handler=handler)
            if success:
                self.logger.debug(
                    'MessageID={} successfully processed '
                    'on attempt={}, deleting.\n'
                    'Action log:\n'
                    '{}'
                    .format(msg.id, attempt, action_log.getvalue())
                )
                queue.delete_message(msg)

            elif attempt >= self.retry_limit:
                self.logger.critical(
                    'MessageID={} attributes={} '
                    'exceeded retry limit {} deleting!\n'
                    'msg={}\n'
                    'Action log:\n'
                    '{}'
                    .format(msg.id,
                            msg.attributes,
                            self.retry_limit,
                            msg.get_body(),
                            action_log.getvalue())
                )
                queue.delete_message(msg)

            else:
                self.logger.warn(
                    'MessageID={} failed to process '
                    'on attempt={}, requeueing.\n'
                    'Action log:\n'
                    '{}'
                    .format(msg.id, attempt, action_log.getvalue())
                )

            action_log.close()

import logging
import os
import uuid

import boto.s3
import boto.sqs


class DeadLetterS3Backend(object):
    """
    A mechanism to store and reload dead letter messages to and from S3.
    Implements PersistStrategy interface.
    """
    def __init__(self, region, bucket_name, queue_name, *args, **kwargs):
        self.region = region
        self.bucket = bucket_name
        self.queue_name = queue_name
        self.logger = logging.getLogger(__name__)

    def get_bucket(self):
        c = boto.s3.connect_to_region(self.region)
        bucket = c.get_bucket(self.bucket)
        return bucket

    def get_queue(self):
        sqs = boto.sqs.connect_to_region(self.region)
        queue = sqs.get_queue(self.queue_name)
        return queue

    def persist(self, queue, message):
        """
        Persist a `boto.sqs.message` to the configured S3 bucket.
        """
        bucket = self.get_bucket()
        key = bucket.new_key(os.path.join(queue.name, message.id))
        key.set_contents_from_string(message.encode(message.get_body()))
        self.logger.info('Message {} persisted to s3://{}/{}'
                         .format(message.id, self.bucket, key.key))


class DeadLetter(object):
    def __init__(self, backend_builder, *args, **kwargs):
        self.backend = backend_builder()
        self.logger = logging.getLogger(__name__)

    def _find_message_id(self, *args):
        # Find the first thing in the arg list which looks like a UUID
        for arg in args:
            try:
                return uuid.UUID(arg)
            except:
                continue
        return None

    def invoke(self, *args, **kwargs):
        # We try to be as compatible as possible with the implementors
        # Processor Message Class.
        # Furthermore, we never want any of this resources actions to result in
        # a re-queue

        action = None
        message_id = None
        try:
            if 'replay' in args:
                action = 'replay'

            if action:
                message_id = self._find_message_id(*args)

            if message_id:
                getattr(self, action)(message_id)

        except:
            self.logger.error(
                'DeadLetter failed: action={} message_id={}'
                .format(action, message_id),
                exc_info=True
            )
        finally:
            return True

    def replay(self, message_id):
        bucket = self.backend.get_bucket()
        queue = self.backend.get_queue()

        key = bucket.new_key(os.path.join(queue.name, message_id))
        message = queue.new_message(key.get_contents_as_string())
        replayed_message = queue.write(message)

        self.logger.info(
            'Message replayed from s3://{}/{} with new MessageID={}'
            .format(self.bucket, key.key, replayed_message.id)
        )

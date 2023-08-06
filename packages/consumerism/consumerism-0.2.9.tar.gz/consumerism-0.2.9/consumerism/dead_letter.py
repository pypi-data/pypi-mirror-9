import logging
import os

import boto.s3
import boto.sqs


class DeadLetterS3Backend(object):
    """
    A mechanism to store and reload dead letter messages to and from S3.
    """
    def __init__(self, region, bucket_name):
        self.region = region
        self.bucket = bucket_name
        self.logger = logging.getLogger(__name__)

    def persist(self, queue, message):
        """
        Persist a `boto.sqs.message` to the configured S3 bucket.
        """
        c = boto.s3.connect_to_region(self.region)
        bucket = c.get_bucket(self.bucket)
        key = bucket.new_key(os.path.join(queue.name, message.id))
        key.set_contents_from_string(message.get_body())

    def reload(self, queue, message_id):
        c = boto.s3.connect_to_region(self.region)
        bucket = c.get_bucket(self.bucket)
        key = bucket.new_key(os.path.join(queue.name, message.id))
        message = queue.new_message(key.get_contents_as_string())
        queue.write(message)

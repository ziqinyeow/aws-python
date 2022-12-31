import os
import json
import uuid
import boto3
import typing
import logging
from .err.sqs import errorhandler
from .schema.sqs import SQSQueueSpecifications, \
    SQSMessage, ReceiveAttributeNames, ReturnedSQSMessages


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s -- [%(module)s:%(lineno)s - %(levelname)s] -- %(message)s"
)
logger = logging.getLogger(__name__)


class SQS:
    def __init__(
        self,
        queue: str = None,
        aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID", None),
        aws_secret_access_key=os.environ.get(
            "AWS_SECRET_ACCESS_KEY", None),
        region_name=os.environ.get("AWS_DEFAULT_REGION", None)
    ):
        self.queue = queue
        self.sqs = boto3.client(
            'sqs',
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=region_name
        )

    @errorhandler
    def publish(self, message: SQSMessage, queue: str = None) -> typing.Dict:
        queue = queue or self.queue
        message = message.__dict__

        if queue.endswith(".fifo"):
            resp = self.sqs.send_message(
                QueueUrl=queue,
                MessageBody=json.dumps(message['body']),
                MessageDeduplicationId=message['deduplication_id'],
                MessageGroupId=message['group_id']
            )
        else:
            resp = self.sqs.send_message(
                QueueUrl=queue,
                MessageBody=json.dumps(message['body']),
            )
        logging.info(
            f"Sent message ID {message['body']} to SQS ({queue}) with ID: {resp['MessageId']}"
        )
        return resp

    @errorhandler
    def pool(
        self,
        queue: str = None,
        attribute_names: typing.List[ReceiveAttributeNames] = [
            ReceiveAttributeNames.ALL.value],
        message_attribute_names: typing.List = [],
        max_number_of_messages: int = 10,  # 1 - 10
        visibility_timeout: int = 1,  # 1 - 20
        wait_time_seconds: int = 5,
        receive_request_attempt_id: str = uuid.uuid1().hex
    ) -> typing.List[typing.Union[ReturnedSQSMessages, None]]:
        queue = queue or self.queue
        resp = self.sqs.receive_message(
            QueueUrl=queue,
            AttributeNames=attribute_names,
            MessageAttributeNames=message_attribute_names,
            MaxNumberOfMessages=max_number_of_messages,
            VisibilityTimeout=visibility_timeout,
            WaitTimeSeconds=wait_time_seconds,
            ReceiveRequestAttemptId=receive_request_attempt_id
        )
        return resp.get("Messages", [])

    @staticmethod
    @errorhandler
    def create_queue(
        self,
        queue: str,
        attributes: typing.Union[SQSQueueSpecifications,
                                 typing.Dict] = SQSQueueSpecifications(),
        tags: typing.Dict = {}
    ) -> str:
        if isinstance(attributes, SQSQueueSpecifications):
            attributes = attributes.__dict__

        if attributes["FifoQueue"] == "false":
            attributes.pop("FifoQueue")
            attributes.pop("ContentBasedDeduplication")
            attributes.pop("DeduplicationScope")
            attributes.pop("FifoThroughputLimit")
        else:
            queue += ".fifo" if not queue.endswith(".fifo") else ""

        url = self.sqs.create_queue(
            QueueName=queue,
            Attributes=attributes,
            tags=tags
        )['QueueUrl']
        return url

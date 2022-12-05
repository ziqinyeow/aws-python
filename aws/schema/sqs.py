import enum
import uuid
import typing
import dataclasses


@dataclasses.dataclass
class SQSQueueSpecifications:
    DelaySeconds: str = "0"
    MaximumMessageSize: str = "262144"  # 256kb
    MessageRetentionPeriod: str = "345600"  # 4 days
    Policy: str = ""
    ReceiveMessageWaitTimeSeconds: str = "0"
    RedrivePolicy: str = ""
    VisibilityTimeout: str = "30"
    KmsMasterKeyId: str = ""
    KmsDataKeyReusePeriodSeconds: str = "300"
    SqsManagedSseEnabled: str = "true"
    FifoQueue: str = "false"
    ContentBasedDeduplication: str = "false"
    DeduplicationScope: str = "messageGroup" or "queue"
    FifoThroughputLimit: str = "perMessageGroupId" or "perQueue"


@dataclasses.dataclass
class SQSMessage:
    deduplication_id: str = uuid.uuid1().hex
    group_id: str = uuid.uuid1().hex
    body: typing.Dict = dataclasses.field(default_factory=dict)


class ReceiveAttributeNames(enum.Enum):
    ALL = "All"
    POLICY = "Policy"
    VISIBILITY_TIMEOUT = "VisibilityTimeout"
    MAXIMUM_MESSAGE_SIZE = "MaximumMessageSize"
    MESSAGE_RETENTION_PERIOD = "MessageRetentionPeriod"
    APPROXIMATE_NUMBER_OF_MESSAGES = "ApproximateNumberOfMessages"
    APPROXIMATE_NUMBER_OF_MESSAGES_NOT_VISIBLE = "ApproximateNumberOfMessagesNotVisible"
    CREATED_TIMESTAMP = "CreatedTimestamp"
    LAST_MODIFIED_TIMESTAMP = "LastModifiedTimestamp"
    QUEUE_ARN = "QueueArn"
    APPROXIMATE_NUMBER_OF_MESSAGES_DELAYED = "ApproximateNumberOfMessagesDelayed"
    DELAY_SECONDS = "DelaySeconds"
    RECEIVE_MESSAGE_WAIT_TIME_SECONDS = "ReceiveMessageWaitTimeSeconds"
    REDRIVE_POLICY = "RedrivePolicy"
    FIFO_QUEUE = "FifoQueue"
    CONTENT_BASED_DEDUPLICATION = "ContentBasedDeduplication"
    KMS_MASTER_KEY_ID = "KmsMasterKeyId"
    KMS_DATA_KEY_REUSE_PERIOD_SECONDS = "KmsDataKeyReusePeriodSeconds"
    DEDUPLICATION_SCOPE = "DeduplicationScope"
    FIFO_THROUGHPUT_LIMIT = "FifoThroughputLimit"
    REDRIVE_ALLOW_POLICY = "RedriveAllowPolicy"
    SQS_MANAGED_SSE_ENABLED = "SqsManagedSseEnabled"


class ReturnedSQSMessages(typing.TypedDict):
    MessageId: str
    ReceiptHandle: str
    MD5OfBody: str
    Body: str
    Attributes: typing.Dict
    MD5OfMessageAttributes: typing.Union[str, None]
    MessageAttributes: typing.Union[typing.Dict, None]

import enum
import logging
import botocore
import functools

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s -- [%(module)s:%(lineno)s - %(levelname)s] -- %(message)s"
)
logger = logging.getLogger(__name__)


class SQS_ERROR_LIST(enum.Enum):
    BatchEntryIdsNotDistinct = "AWS.SimpleQueueService.BatchEntryIdsNotDistinct"
    BatchRequestTooLong = "AWS.SimpleQueueService.BatchRequestTooLong"
    EmptyBatchRequest = "AWS.SimpleQueueService.EmptyBatchRequest"
    InvalidAttributeName = "InvalidAttributeName"
    InvalidBatchEntryId = "AWS.SimpleQueueService.InvalidBatchEntryId"
    InvalidIdFormat = "InvalidIdFormat"
    InvalidMessageContents = "InvalidMessageContents"
    MessageNotInflight = "AWS.SimpleQueueService.MessageNotInflight"
    OverLimit = "OverLimit"
    PurgeQueueInProgress = "AWS.SimpleQueueService.PurgeQueueInProgress"
    QueueDeletedRecently = "AWS.SimpleQueueService.QueueDeletedRecently"
    NonExistentQueue = "AWS.SimpleQueueService.NonExistentQueue"
    QueueAlreadyExists = "QueueAlreadyExists"
    ReceiptHandleIsInvalid = "ReceiptHandleIsInvalid"
    TooManyEntriesInBatchRequest = "AWS.SimpleQueueService.TooManyEntriesInBatchRequest"
    UnsupportedOperation = "AWS.SimpleQueueService.UnsupportedOperation"


def errorhandler(func):
    @functools.wraps(func)
    def _wrap(*args, **kwargs):
        try:
            ret = func(*args, **kwargs)
            return ret or True
        except botocore.exceptions.ClientError as err:
            logging.error(err.response['Error']['Message'])
            return False

    return _wrap

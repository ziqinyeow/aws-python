import enum
import logging
import botocore
import functools

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s -- [%(module)s:%(lineno)s - %(levelname)s] -- %(message)s"
)
logger = logging.getLogger(__name__)


class DYDB_ERROR_LIST(enum.Enum):
    BackupInUseException = "BackupInUseException"
    BackupNotFoundException = "BackupNotFoundException"
    ConditionalCheckFailedException = "ConditionalCheckFailedException"
    ContinuousBackupsUnavailableException = "ContinuousBackupsUnavailableException"
    DuplicateItemException = "DuplicateItemException"
    ExportConflictException = "ExportConflictException"
    ExportNotFoundException = "ExportNotFoundException"
    GlobalTableAlreadyExistsException = "GlobalTableAlreadyExistsException"
    GlobalTableNotFoundException = "GlobalTableNotFoundException"
    IdempotentParameterMismatchException = "IdempotentParameterMismatchException"
    ImportConflictException = "ImportConflictException"
    ImportNotFoundException = "ImportNotFoundException"
    IndexNotFoundException = "IndexNotFoundException"
    InternalServerError = "InternalServerError"
    InvalidExportTimeException = "InvalidExportTimeException"
    InvalidRestoreTimeException = "InvalidRestoreTimeException"
    ItemCollectionSizeLimitExceededException = "ItemCollectionSizeLimitExceededException"
    LimitExceededException = "LimitExceededException"
    PointInTimeRecoveryUnavailableException = "PointInTimeRecoveryUnavailableException"
    ProvisionedThroughputExceededException = "ProvisionedThroughputExceededException"
    ReplicaAlreadyExistsException = "ReplicaAlreadyExistsException"
    ReplicaNotFoundException = "ReplicaNotFoundException"
    RequestLimitExceeded = "RequestLimitExceeded"
    ResourceInUseException = "ResourceInUseException"
    ResourceNotFoundException = "ResourceNotFoundException"
    TableAlreadyExistsException = "TableAlreadyExistsException"
    TableInUseException = "TableInUseException"
    TableNotFoundException = "TableNotFoundException"
    TransactionCanceledException = "TransactionCanceledException"
    TransactionConflictException = "TransactionConflictException"
    TransactionInProgressException = "TransactionInProgressException"


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

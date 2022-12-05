import enum
import logging
import botocore
import functools

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s -- [%(module)s:%(lineno)s - %(levelname)s] -- %(message)s"
)
logger = logging.getLogger(__name__)


class S3_ERROR_LIST(enum.Enum):
    BucketAlreadyExists = "BucketAlreadyExists"
    BucketAlreadyOwnedByYou = "BucketAlreadyOwnedByYou"
    InvalidObjectState = "InvalidObjectState"
    NoSuchBucket = "NoSuchBucket"
    NoSuchKey = "NoSuchKey"
    NoSuchUpload = "NoSuchUpload"
    ObjectAlreadyInActiveTierError = "ObjectAlreadyInActiveTierError"
    ObjectNotInActiveTierError = "ObjectNotInActiveTierError"


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

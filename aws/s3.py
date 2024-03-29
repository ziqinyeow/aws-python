import os
import tqdm
import glob
import boto3
import typing
import logging
from pathlib import Path
from .err.s3 import errorhandler


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s -- [%(module)s:%(lineno)s - %(levelname)s] -- %(message)s"
)
logger = logging.getLogger(__name__)


class S3():
    def __init__(
        self,
        bucket: str = None,
        aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID", None),
        aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY", None),
        region_name=os.environ.get("AWS_DEFAULT_REGION", None)
    ):
        self.bucket = bucket
        # resource
        self.s3r = boto3.resource(
            's3',
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=region_name
        )

        # client
        self.s3c = boto3.client(
            's3',
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=region_name
        )

    @errorhandler
    def contains(self, prefix: str, bucket: str = None) -> bool:
        """Check if prefix folder contains folder/file path"""
        bucket = bucket or self.bucket
        if len(prefix.split("/")[-1].split(".")) <= 1:
            if prefix.endswith("/"):
                prefix = prefix[:-1]
            objects = self.s3c.list_objects(
                Bucket=bucket, Prefix=prefix, Delimiter="/", MaxKeys=1)
            return prefix + "/" == objects.get('CommonPrefixes')[0].get("Prefix")
        else:
            self.s3r.Object(bucket, os.path.join(prefix)).load()
        return True

    @errorhandler
    def list_all(self, prefix: str, bucket: str = None) -> list:
        """
        List all files recursively within the prefix folder 
        Maximum Len Returns: 1000
        """
        bucket = bucket or self.bucket
        objects = self.s3c.list_objects(Bucket=bucket, Prefix=prefix)
        paths = [x.get("Key") for x in objects.get("Contents", [])]
        return paths

    @errorhandler
    def list_dirs(self, prefix: str, delimiter="/", bucket: str = None) -> list:
        """
        List all folders one level within the prefix folder
        Maximum Len Returns: 1000
        """
        bucket = bucket or self.bucket
        objects = self.s3c.list_objects(
            Bucket=bucket, Prefix=prefix, Delimiter=delimiter)
        assert objects.get(
            "CommonPrefixes"), "No objects found inside the directory (Please provide existed directory)"
        paths = [x.get("Prefix") for x in objects.get("CommonPrefixes")]
        return paths

    @errorhandler
    def upload_file(
        self,
        prefix: str,
        path: str,
        filename: str = "",
        bucket: str = None
    ) -> None:
        bucket = bucket or self.bucket
        prefix = self.parse_prefix(prefix)
        if not filename:
            file = os.path.basename(path)
            self.s3c.upload_file(path, bucket, os.path.join(prefix, file))
        else:
            if "." not in filename:
                _, ext = self.parse_file_ext(path)
                filename += ext
            self.s3c.upload_file(path, bucket, os.path.join(prefix, filename))

    @errorhandler
    def upload_dir(
        self,
        prefix: str,
        path: str,
        include_root: bool = False,
        folder_name: str = "",
        upload_only: typing.List = [],
        bucket: str = None
    ):
        bucket = bucket or self.bucket
        if not folder_name:
            folder_name = self.parse_prefix(path).split("/")[-1]
        path = self.parse_prefix(path)
        cwd = str(Path.cwd())
        p = Path(os.path.join(Path.cwd(), path))
        dir = list(p.glob('**'))
        for d in tqdm.tqdm(dir, desc=f"Uploading artifacts"):
            files = glob.glob(os.path.join(d, "*"))
            for file in files:
                if not Path(file).is_dir():
                    file = self.parse_prefix(str(file).replace(cwd, ''), True)
                    if len(upload_only) > 0 and file.replace(path + "/", "").split("/")[0] not in upload_only:
                        continue
                    path = path.replace(".", "").replace("/", "")
                    if include_root:
                        s3Path = self.parse_prefix(
                            file.replace(path, folder_name), True)
                    else:
                        s3Path = self.parse_prefix(
                            file.replace(path, ""), True)
                    s3Path = os.path.join(self.parse_prefix(prefix), s3Path)
                    self.s3c.upload_file(file, bucket, s3Path)

    @errorhandler
    def download_file(
        self,
        prefix: str,
        save_path=".",
        rename_to="",
        bucket: str = None
    ) -> str:
        bucket = bucket or self.bucket
        filename = os.path.basename(prefix)
        filename = rename_to + \
            os.path.splitext(filename)[-1] if rename_to else filename
        path = os.path.join(save_path, filename)
        if not os.path.exists(os.path.dirname(path)):
            os.makedirs(os.path.dirname(path))
        self.s3c.download_file(bucket, prefix, path)
        return os.path.join(path)

    @errorhandler
    def download_file_from_uri(
        self,
        s3_uri,
        save_path=".",
        rename_to=""
    ) -> str:
        bucket, prefix = self.parse_s3_uri(s3_uri)
        return self.download_file(prefix, save_path, rename_to, bucket=bucket)

    @errorhandler
    def download_dir(self, prefix: str, save_path=".", bucket: str = None) -> None:
        bucket = bucket or self.bucket
        bucket = self.s3r.Bucket(bucket)
        for obj in bucket.objects.filter(Prefix=prefix):
            path = os.path.join(save_path, os.path.relpath(obj.key, prefix))
            if not os.path.exists(os.path.dirname(path)):
                os.makedirs(os.path.dirname(path))
            bucket.download_file(obj.key, path)

    @errorhandler
    def download_dir_from_uri(self, s3_uri: str, save_path=".") -> None:
        bucket, prefix = self.parse_s3_uri(s3_uri)
        self.download_dir(prefix, save_path, bucket=bucket)

    @staticmethod
    def parse_s3_uri(s3_uri: str) -> typing.Tuple[str, str]:
        uri = s3_uri.replace("s3://", "")
        bucket, prefix = uri.split("/")[0], '/'.join(uri.split("/")[1:])
        return bucket, prefix

    @staticmethod
    def parse_prefix(prefix: str, include_file: bool = False) -> str:
        """Turn prefix string to good format"""
        p = prefix.replace("/", " ").split()
        if not include_file:
            p = p[:-1] if "." in p[-1] else p
        return '/'.join(p)

    @staticmethod
    def parse_file_ext(path: str) -> typing.Tuple[str, str]:
        file = os.path.basename(path)
        return os.path.splitext(file)

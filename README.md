# AWS Python Boto3 Package Utility

## Supported Services

1. `S3` - AWS Simple Storage
2. `DYDB` - AWS DynamoDB
3. `SQS` - AWS Simple Queue Service

## How to use

```python
from aws import S3, DYDB, SQS ...

s3 = S3()

s3.upload_dir(...) # see type hinting
```

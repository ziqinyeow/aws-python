# AWS Python Boto3 Package Utility

Simple AWS Boto3 boilerplate code that simplify AWS Python devs.

## Supported Services

1. `S3` - AWS Simple Storage
2. `DYDB` - AWS DynamoDB
3. `SQS` - AWS Simple Queue Service

## How to use

### AWS S3 - [View More](/aws/s3.py)

```python
from aws import S3

s3 = S3()
s3.upload_dir(...) # see type hinting
```

### AWS DYDB - [View More](/aws/dydb.py)

```python
from aws import DYDB

dydb = DYDB()
dydb.get({id: "<id>"}, table = "table_name")
dydb.update({
    id: "<id>"
}, {
    attr: "this is a str",
    list_attr: ["this is a list"],
    bool_attr: False
}, table="table_name")
```

### AWS SQS - [View More](/aws/sqs.py)

```python
from aws import SQS, SQSMessage, SQSQueueSpecifications

# Initialize sqs queue
sqs = SQS()

# Create a standard queue
sqs.create_queue(
    "a",
)

# Create a fifo queue
sqs.create_queue(
    "a.fifo",  # Add .fifo at the end
    SQSQueueSpecifications(
        FifoQueue="true"
        # ... add other specs (type hinting)
    )
)

# Publish message
sqs.publish(
    queue="a.fifo", # or "a"
    message=SQSMessage(
        body={
            "hello": "world"
        }
    )
)

# Pool messages
messages = sqs.pool(
    queue="a" # or "a.fifo"
)

```

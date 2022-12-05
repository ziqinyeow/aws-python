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

import boto3
import os
import pytest
from moto import mock_aws

# Change the AWS environment variables for testing purposes
@pytest.fixture(scope="session", autouse=True)
def aws_credentials():
    os.environ['AWS_ACCESS_KEY'] = "testing"
    os.environ['AWS_SECRET_KEY'] = "testing"
    os.environ['AWS_DEFAULT_REGION'] = "eu-north-1"


# Create a fake SQS client to poll and send messages to
@pytest.fixture(scope="session")
def sqs_client(aws_credentials):
    with mock_aws():
        # Create a SQS client for the mocks
        client = boto3.client("sqs", region_name="eu-north-1")
        yield client


# Create a new P3 Queue for the purpose of testing
@pytest.fixture(scope="session", autouse=True)
def setup_sqs_queues(sqs_client, aws_credentials):
    with mock_aws():
        # Create queues for the mocks
        p3_url = sqs_client.create_queue(QueueName="p3Queue")["QueueUrl"]
        print(p3_url)
        # Set queues in our environment for testing
        os.environ["p3Queue_URL"] = p3_url
        yield

# Importantly, we want to load the app after setting up the env for testing
@pytest.fixture(scope="session", autouse=True)
def load_app(setup_sqs_queues):
    from app import app
    return app
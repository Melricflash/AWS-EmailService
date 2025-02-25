import threading
import pytest
import boto3
import os
from app import p3SESPush

# Load up app after imports and conftest
@pytest.fixture
def client(load_app):
    with load_app.test_client() as client:
        yield client

def test_get_message_from_p3(client, setup_sqs_queues, monkeypatch, mocker):
    queue_url = os.environ["p3Queue_URL"]

    # Patch p3Queue URL again as we load the app which may overwrite variables
    monkeypatch.setattr("app.p3QueueURL", queue_url)

    # Patch out SES functionality, dont want to send actual email out, just test consuming
    mocker.patch("app.ses.send_email", return_value=None)

    # Note we dont need to create an SES client because we only need to send a message to SQS for testing
    sqs_client = boto3.client("sqs", region_name="eu-north-1")

    # Compose a message to send to SQS
    message = {
        "title": "Email Title",
        "description": "Test description",
    }

    sqs_client.send_message(QueueUrl = queue_url, MessageBody = str(message))

    thread = threading.Thread(target=p3SESPush)
    thread.start()
    thread.join(timeout=5)

    # Attempt to stop the thread
    monkeypatch.setattr("app.stop_flag", True)
    thread.join()

    # Check that the message was consumed correctly by SQS
    response = sqs_client.receive_message(QueueUrl=queue_url)
    assert "Messages" not in response
import boto3
import os
from dotenv import load_dotenv
from flask import Flask
import threading

load_dotenv()

app = Flask(__name__)

AWS_ACCESS = os.getenv("AWS_ACCESS_KEY")
AWS_SECRET = os.getenv("AWS_SECRET_KEY")
AWS_REGION = os.getenv("AWS_DEFAULT_REGION")
p3QueueURL = os.getenv("p3Queue_URL")

SES_SOURCE = os.getenv("SES_SOURCE")
SES_TARGET = os.getenv("SES_TARGET")

# Create SQS Client
sqs = boto3.client('sqs',
                   aws_access_key_id = AWS_ACCESS,
                   aws_secret_access_key = AWS_SECRET,
                   region_name = AWS_REGION
                   )
# Create SES Client
ses = boto3.client('ses',
                   aws_access_key_id = AWS_ACCESS,
                   aws_secret_access_key = AWS_SECRET,
                   region_name = AWS_REGION)

# Change the HTML contents sent from the email
HTMLBody = "<h1> Hi! This is a test email. </h1>"

stop_flag = False

@app.route("/")
def healthCheck():
    return "<h1> P3 Service Healthy! </h1>"

def p3SESPush():
    global stop_flag
    while not stop_flag:
            try:
                # Attempt to read from the queue
                response = sqs.receive_message(
                    QueueUrl=p3QueueURL,
                    MaxNumberOfMessages=1,  # Just get one item from the queue for now
                    WaitTimeSeconds=20
                )

                if 'Messages' in response:
                    queueMessage = response['Messages'][0]
                    messageID = queueMessage['MessageId']  # Could be used for a JIRA ticket
                    receipt = queueMessage['ReceiptHandle']
                    contents = queueMessage['Body']

                    # Parse the message contents
                    parsedContents = eval(contents)
                    title = parsedContents['title']
                    description = parsedContents['description']

                    print(title)
                    print(description)
                    print(f"Source: {SES_SOURCE}")
                    print(f"Target: {SES_TARGET}")

                    # Compose the message using SES Client
                    response = ses.send_email(
                        Source = SES_TARGET, # Source doesn't work for now so we just send to ourselves

                        Destination = {
                            'ToAddresses': [SES_TARGET]
                        },
                        Message = {
                            'Subject': {
                                'Data': title,
                                'Charset': 'UTF-8'
                            },
                            'Body': {
                                'Text': {
                                    'Data': description,
                                    'Charset': 'UTF-8'
                                },
                                'Html': {
                                    'Data': HTMLBody,
                                    'Charset': 'UTF-8'
                                }
                            }
                        }
                    )
                    print(f"Sent email for SQS: {messageID}")

                    # Delete message from SQS
                    sqs.delete_message(QueueUrl=p3QueueURL, ReceiptHandle=receipt)
                    print("Deleted Message from SQS...")



                else:
                    print("No messages found in queue...")


            except Exception as err:
                print(f"An error occurred: {err}")

def background_thread():
    sqs_thread = threading.Thread(target=p3SESPush, daemon=True)
    sqs_thread.start()
    return sqs_thread

bg_thread = background_thread()


if __name__ == '__main__':
    #p3SESPush()
    try:
        app.run(host="0.0.0.0", port=8000)
    except KeyboardInterrupt:
        print("Shutting down...")
        stop_flag = True
        bg_thread.join()
import boto3
from botocore.exceptions import ClientError
from slack import WebClient
from slack.errors import SlackApiError
import config
import logging
from SlackMessage import SlackMessage
import json


logger = logging.getLogger("voicemail")
logger.setLevel(logging.DEBUG)

session = boto3.session.Session(region_name=config.DEFAULT_AWS_REGION)
ssm = session.client('ssm')


try:
    # retrieve the Slack API key from SSM parameter store
    response = ssm.get_parameter(
        Name=config.SLACK_API_PARAMETER_NAME,
        WithDecryption=True
    )
except ClientError as e:
    if e.response['Error']['Code'] == 'ParameterNotFound':
        assert KeyError(f'Could not find Slack API Key.  Store it in SSM Parameter Store as a SecureString named {config.SLACK_API_PARAMETER_NAME}')
    else:
        raise e
SLACK_API_TOKEN = response['Parameter']['Value']

try:
    slackClient = WebClient(token=SLACK_API_TOKEN)
except SlackApiError as e:
    # You will get a SlackApiError if "ok" is False
    assert e.response["error"]  # str like 'invalid_auth', 'channel_not_found'


def slack_send(msg):
    # get list of users
    userResponse = slackClient.users_list()
    users = userResponse['members']

    # check to see if the target channel is a valid user
    recipient = next((item for item in users if item["name"] == msg.channel), None)

    # if it isn't a user
    if recipient is None:

        # get list of channels
        channelResponse = slackClient.conversations_list(exclude_archived=1)
        channels = channelResponse['channels']

        # check to see if the target channel is a valid channel
        recipient = next((item for item in channels if item["name"] == msg.channel), None)

        # if it isn't a channel either, add a warning and send to default channel
        if recipient is None:
            message['warning'] = f'This message was sent to non-existent user/channel {target}'
            recipient = next((item for item in channels if item["name"] == config.DEFAULT_CHANNEL_NAME), None)

            # if even the default channel doesn't exist, raise an error
            if recipient is None:
                raise ValueError(f'Default channel {config.DEFAULT_CHANNEL_NAME} does not exist')

    try:
        postResponse = slackClient.chat_postMessage(
            channel=recipient['id'],
            text=f'{msg}'
        )
        return {
            'StatusCode': 200,
            'Channel': msg.channel,
            'Subject': msg.subject,
            'Message': msg.text
        }
    except SlackApiError as e:
        # You will get a SlackApiError if "ok" is False
        assert e.response["error"]  # str like 'invalid_auth', 'channel_not_found'


def lambda_handler(event, context):
    filename = event["Records"][0]["s3"]["object"]["key"].split('.')[0]
    logger.debug(filename)
    s3_client = boto3.client('s3')
    voicemail_recording = s3_client.get_object(Bucket="voicemailtest-voicemailstac-audiorecordingsbucket-1sckoc240lu5n", Key=f"recordings/{filename}.wav")
    voicemail_transcript = s3_client.get_object(Bucket="voicemail-transcripts-bucket", Key=f"{filename}.json")
    slack_data = {'recording': voicemail_recording, 'transcript': voicemail_transcript}
    logger.debug(voicemail_transcript)
    myUserName = 'Charlotte'

    myJsonMsg = {
        "subject": "New voicemail message",
        "channel": myUserName,
        "text": json.dumps(voicemail_transcript)
    }
    myMessage = SlackMessage(json.dumps(myJsonMsg))
    lambdaResponse = slack_send(myMessage)
    return lambdaResponse

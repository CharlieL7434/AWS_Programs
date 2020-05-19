import boto3
from botocore.exceptions import ClientError
from slack import WebClient
from slack.errors import SlackApiError
import config
import logging

session = boto3.session.Session()
ssm = session.client('ssm')

logger = logging.getLogger()
logger.setLevel(logging.INFO)

logger.debug('retrieving the Slack API key from SSM parameter store')
try:
    response = ssm.get_parameter(
        Name=config.SLACK_API_PARAMETER_NAME,
        WithDecryption=True
    )
except ClientError as e:
    if e.response['Error']['Code'] == 'ParameterNotFound':
        logger.error(f'Could not find Slack API Key.  Store it in SSM Parameter Store as a SecureString named {config.SLACK_API_PARAMETER_NAME}')
    else:
        logger.error(e)
SLACK_API_TOKEN = response['Parameter']['Value']

logger.debug('setup slack Webclient')
try:
    slackClient = WebClient(token=SLACK_API_TOKEN)
except SlackApiError as e:
    # You will get a SlackApiError if "ok" is False
    logger.error(e)


def slackSend(msg):
    logger.info(f'posting message to Slack/{msg.channel}')

    logger.debug(f'identifying {msg.channel}')
    logger.debug('retrieving user list from Slack')

    userResponse = slackClient.users_list()

    # Slack identifies users by their id, by their username, and optionally by their real_name and display_name
    # Build a searchable list of names
    userNames = []
    for user in userResponse['members']:
        userName = {"id": user['id']}
        for key in ['name', 'real_name']:
            if key in user.keys():
                userName[key] = user[key]
        if 'profile' in user.keys():
            if 'display_name' in user['profile'].keys():
                userName['display_name'] = user['profile']['display_name']
        userNames.append(userName)

    # iterate across searchable list of names to identify the user, or return None if not found
    recipient = next((item for item in userNames if msg.channel in item.values()), None)

    if recipient is None:
        logger.debug(f'{msg.channel} is not a Slack user name')
        logger.debug('retrieving channel list from Slack')

        channelResponse = slackClient.conversations_list(exclude_archived=1)
        channels = channelResponse['channels']

        # iterate across list of channels to identify the channel, or return None if not found
        recipient = next((item for item in channels if item["name"] == msg.channel), None)

        if recipient is None:
            logger.warning(f'{msg.channel} is not a Slack channel name.  Sending to default channel {config.DEFAULT_CHANNEL_NAME}')

            msg.warning = f'This message was sent to non-existent user/channel {msg.channel}'

            # iterate across list of channels to identify the default channel, or return None if not found
            recipient = next((item for item in channels if item["name"] == config.DEFAULT_CHANNEL_NAME), None)

            if recipient is None:
                logger.error (f'Default channel {config.DEFAULT_CHANNEL_NAME} was not found')
                return False
    logger.info(f"Requested destination: {msg.channel}.  Actual destination: {recipient['name']}")

    logger.debug(f"sending message")
    try:
        postResponse = slackClient.chat_postMessage(
            channel=recipient['id'],
            text=f'{msg}'
        )
        return {'ok': postResponse['ok']}
    except SlackApiError as e:
        # You will get a SlackApiError if "ok" is False
        logger.error(e)
        return False
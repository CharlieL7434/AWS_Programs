# Set the channel in Slack to which messages will be sent by default, including warnings and unaddressed messages.
DEFAULT_CHANNEL_NAME = "charlotte"

# Set the SNS topic name to be monitored for messages
SNS_TOPIC_NAME = "Slacker"

# Set the name of the SSM Parameter used to store the Slack API Key
SLACK_API_PARAMETER_NAME = "SLACK_AWS_SLACKER_API_TOKEN"

# Set the default AWS region
DEFAULT_AWS_REGION = "ap-southeast-1"

# Scopes required in Slack
SLACK_SCOPES = [
    "channels:read", "channels:join", "channels:manage",
    "chat:write",
    "groups:read",
    "im:read",
    "mpim:read",
    "users:read"
]

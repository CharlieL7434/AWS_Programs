import boto3
from botocore.exceptions import ClientError

import config
import logging

from SlackMessage import SlackMessage
from slackSend import slackSend


logger = logging.getLogger("voicemail")
logger.setLevel(logging.DEBUG)

# This is a slightly more complex structure than boto3 docs, but it gives better control over regions, profiles
# set up a session using region_name, profile_name parameters as necessary
session = boto3.session.Session(region_name=config.DEFAULT_AWS_REGION)
# create the client from the session
s3_client = session.client('s3')


def lambda_handler(event, context):
    # should normally use os.path to parse filenames or urllib3 to parse urls
    # however in this case, AWS Connect seems to be setting predictable filenames, so split should work.
    filename = event["Records"][0]["s3"]["object"]["key"].split('.')[0]
    logger.debug(f"Found recroding {filename}")

    # TODO: this retrieves a dict from s3 that describes the voicemail_recording, not the recording itself
    response = s3_client.get_object(
        Bucket="voicemailtest-voicemailstac-audiorecordingsbucket-1sckoc240lu5n",
        Key=f"recordings/{filename}.wav"
    )
    voicemail_recording = None
    presigned_url_to_vm_recording = None

    # TODO: this retrieves a dict that describes the transcript, not the file content
    response = s3_client.get_object(
        Bucket="voicemail-transcripts-bucket",
        Key=f"{filename}.json"
    )
    voicemail_transcript = None
    transcript_text = None

    myUserName = 'Charlotte'
    myMsg = f"Transcript: {transcript_text}"
    myMsg += f"Recording available at: {presigned_url_to_vm_recording}"

    myJsonMsg = SlackMessage(
        subject="New voicemail from PragmaConnect",
        channel=myUserName,
        text=myMsg
    )

    lambdaResponse = slackSend(myJsonMsg)
    return lambdaResponse

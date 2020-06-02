from pprint import pprint
import urllib3

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


def getUserNamefromAgentId(uid):
    dynamodb_client = boto3.client('dynamodb')
    response = dynamodb_client.query(
        ExpressionAttributeValues={
            ':v1': {
                'S': uid,
            },
        },
        KeyConditionExpression='agentId = :v1',
        TableName=config.USER_TABLE_NAME,
    )
    myUserName = response['Items'][0]['username']['S']
    return myUserName


def lambda_handler(event, context):
    # should normally use os.path to parse filenames or urllib3 to parse urls
    # however in this case, AWS Connect seems to be setting predictable filenames, so split should work.
    filename = event["Records"][0]["s3"]["object"]["key"]
    logger.debug(f"Found recording {filename}")
    try:
        recording_response = s3_client.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': config.AUDIO_RECORDINGS_BUCKET,
                'Key': f"recordings/{filename}.wav"
            },
            ExpiresIn=100)
    except ClientError as e:
        logging.error(e)

    presigned_url_to_vm_recording = recording_response

    try:
        transcript_response = s3_client.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': config.TRANSCRIPT_BUCKET,
                'Key': f"{filename}"
            },
            ExpiresIn=100)
    except ClientError as e:
        logging.error(e)

    http = urllib3.PoolManager()
    r = http.request('GET', transcript_response)
    transcript_json = eval(r.data)
    transcript_text = transcript_json['results']['transcripts'][0]['transcript']
    transcript_recording_file_object = s3_client.get_object(
        Bucket=config.AUDIO_RECORDINGS_BUCKET,
        Key=f"recordings/{filename}.wav")

    myAgentId = transcript_recording_file_object["Metadata"]["agent-id"]

    #runs a query on the Dynamodb usertable to get username which doubles as a slack channel name
    myUserName = getUserNamefromAgentId(myAgentId)

    myMsg = f"Transcript: {transcript_text}"
    myMsg += f"\n<{presigned_url_to_vm_recording}|click here to download your voicemail>"

    myJsonMsg = SlackMessage(
        subject="New voicemail from PragmaConnect",
        channel=myUserName,
        text=myMsg
    )
    lambdaResponse = slackSend(myJsonMsg)
    return lambdaResponse

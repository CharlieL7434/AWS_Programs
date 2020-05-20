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
    # TODO: do stuff
    return myUserName


def lambda_handler(event, context):
    # should normally use os.path to parse filenames or urllib3 to parse urls
    # however in this case, AWS Connect seems to be setting predictable filenames, so split should work.
    filename = event["Records"][0]["s3"]["object"]["key"].split('.')[0]
    logger.debug(f"Found recroding {filename}")

    try:
        recording_response = s3_client.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': "voicemailtest-voicemailstac-audiorecordingsbucket-1sckoc240lu5n",
                'Key': f"recordings/{filename}.wav"
            },
            ExpiresIn=100)
    except ClientError as e:
        logging.error(e)

    presigned_url_to_vm_recording = recording_response

    try:
        transcript_response = s3_client.generate_presigned_url('get_object',
                                                    Params={'Bucket': "voicemail-transcripts-bucket",
                                                            'Key': f"{filename}.json"},
                                                    ExpiresIn=100)
    except ClientError as e:
        logging.error(e)

    http = urllib3.PoolManager()
    r = http.request('GET', transcript_response)
    transcript_json = eval(r.data)
    transcript_text = transcript_json['results']['transcripts'][0]['transcript']
    myAgentId = None
    myUserName = getUserNamefromAgentId(myAgentId)

    dynamodb_client = boto3.client('dynamodb')

    response = dynamodb_client.query(
        ExpressionAttributeValues={
            ':v1': {
                'S': filename,
            },
        },
        KeyConditionExpression='contactId = :v1',
        TableName='VoicemailTest-VoicemailStack-SJ17OAJAXH9U-ContactVoicemailTable-1LK2JJUVO6F2Q',
    )
    pprint(response)

    myMsg = f"Transcript: {transcript_text}"
    myMsg += f"Recording available at: {presigned_url_to_vm_recording}"

    myJsonMsg = SlackMessage(
        subject="New voicemail from PragmaConnect",
        channel=myUserName,
        text=myMsg
    )
    quit()
    lambdaResponse = slackSend(myJsonMsg)
    return lambdaResponse

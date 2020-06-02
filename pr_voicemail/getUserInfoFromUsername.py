import boto3
import config


def lambda_handler(event, context):
    username = event["Details"]["Parameters"]["Agent"]
    if username == "":
        username = event["Details"]["ContactData"]["Attributes"]["Agent"]
    client = boto3.client('dynamodb')
    response = client.scan(TableName=config.USER_TABLE_NAME,
                           AttributesToGet=['userId', 'username', 'transcribeVoicemail', 'encryptVoicemail'],
                           )
    resultMap = {}
    for items in response['Items']:
        if items['username']['S'] == username:
            resultMap = {"agentId": items['userId']['S'], "transcribeVoicemail": items['transcribeVoicemail']['BOOL'],
                         "encryptVoicemail": items['encryptVoicemail']['BOOL'], "transferMessage": " ",
                         "saveCallRecording": True, "extensionNumber": "12"}
    return resultMap

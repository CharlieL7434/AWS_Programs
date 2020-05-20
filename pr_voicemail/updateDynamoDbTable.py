import pprint
import boto3
def lambda_handler (event, context):
    dynamodb_client = boto3.client('dynamodb')
    filename = event["Records"][0]["s3"]["object"]["key"].split('.')[0]
    s3_client = boto3.client('s3')
    object = s3_client.get_object(Bucket = "voicemailtest-voicemailstac-audiorecordingsbucket-1sckoc240lu5n", Key= f"recordings/{filename}.wav")
    print(object)
    quit()
    response = dynamodb_client.put_item(
        Item={
            'AlbumTitle': {
                'S': 'Somewhat Famous',
            },
            'Artist': {
                'S': 'No One You Know',
            },
            'SongTitle': {
                'S': 'Call Me Today',
            },
        },
        ReturnConsumedCapacity='TOTAL',
        TableName='VoicemailTest-VoicemailStack-SJ17OAJAXH9U-ContactVoicemailTable-1LK2JJUVO6F2Q',
    )
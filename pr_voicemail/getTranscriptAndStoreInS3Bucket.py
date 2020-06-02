import json
import boto3
import urllib3
import config


def lambda_handler(event, context):
    s3_client = boto3.client('s3')
    transcribe_client = boto3.client('transcribe')
    transcription_job_name = event['detail']['TranscriptionJobName']
    transcription_job = transcribe_client.get_transcription_job(TranscriptionJobName=transcription_job_name)
    transcription_job_uri = transcription_job['TranscriptionJob']['Transcript']['TranscriptFileUri']
    http = urllib3.PoolManager()
    r = http.request('GET', transcription_job_uri)
    transcript_json = eval(r.data)
    response = s3_client.put_object(Bucket=config.TRANSCRIPT_BUCKET, Key=transcription_job_name,
                                    Body=json.dumps(transcript_json))

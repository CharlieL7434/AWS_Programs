from SlackMessage import SlackMessage
from slackSend import slackSend
import boto3
import config
from datetime import datetime

def lambda_handler(event, context):
    myUsername = event["Details"]["Parameters"]["agentUsername"]
    customerNo = event["Details"]["Parameters"]["customerNumber"]
    now = datetime.now()
    time = now.strftime("%m/%d/%Y, %H:%M:%S")
    myMsg = f"You missed a call from {customerNo} at UTC {time}"
    myJsonMsg = SlackMessage(
        subject="Missed call on PragmaConnect",
        channel="Charlotte",
        text=myMsg
    )
    lambdaResponse = slackSend(myJsonMsg)
    return lambdaResponse
import os
import json
import uuid
import datetime
import boto3
from botocore.exceptions import ClientError
from botocore.vendored import requests

def handler(event , context):
    data = None
    try:
        data = json.loads(event['body'])
    except Exception as ex:
        return respond(ex.args[0],None)
    table_name = os.getenv('EVENTS_TABLE_NAME')  # Table from env vars or todo_test
    region_name = 'us-east-2'
    client = boto3.resource('dynamodb', region_name = region_name)
    j_data ={
                    "merchantRefNum":data['merchantRefNum'],
                    "amount":data['amount'],
                    "currencyCode": "USD",
                    "dupCheck":True,
                    "settleWithAuth":False,
                    "paymentHandleToken":data['paymentHandleToken'],
                    "customerIp":"172.0.0.1",
                    "description":"some"
    }
    headers ={
                    "Content-Type":"application/json",
                    "Authorization" : "Basic "+os.getenv('private_base64'),
                    "Simulator" : "EXTERNAL",
                    "Access-Control-Allow-Origin":"*"
            }
    body = json.dumps(j_data)
    res = requests.post(
                    "https://api.test.paysafe.com/paymenthub/v1/payments",
                    body, headers = headers
                )
    print(res.status_code)
    send_res = res.json()
    return respond(None, send_res)
    #return jsonify(None,res)
    #return respond(None,customer_info)

def respond(err, res=None):
    # In a real app error messages shouldn't be sent to the end user.
    # This is a security concern. However, in a demo, for debugging, it's okay.
    body = {}
    if err:
        body = json.dumps({'error': err})
    else:
        body = json.dumps(res)
    return {
        'statusCode': '400' if err else '200',
        'body': body,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
    }

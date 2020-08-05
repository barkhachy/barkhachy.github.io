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
    date = data['dob'].split("-")
    #api = cHVibGljLTc3NTE6Qi1xYTItMC01ZjAzMWNiZS0wLTMwMmQwMjE1MDA4OTBlZjI2MjI5NjU2M2FjY2QxY2I0YWFiNzkwMzIzZDJmZDU3MGQzMDIxNDUxMGJjZGFjZGFhNGYwM2Y1OTQ3N2VlZjEzZjJhZjVhZDEzZTMwNDQ=
    customer_info = {
                            "firstName":data['f_name'],
                             "lastName":data['l_name'],
                             "email":data['mail'],
                             "phone":data['phone'],    
                    }
    dateOfBirth =   {
                        "day":date[2],
                        "month":date[1],
                        "year":date[0]
    }
    billing_info = {
                            "nickName":data['f_name']+data['l_name'],
                            "street":data['street_1'],
                            "street2":data['street_2'],
                            "city":data['city'],
                            "zip":data['zip'],
                            "country":data['country'],
                            "state":data["state"]
            }
    j_data = {
                "merchantCustomerId":data['merchantRefNum'],
                "locale":os.getenv('locale'),
                "firstName":customer_info['firstName'],
                "lastName":customer_info['lastName'],
                "dateOfBirth":
                {
                    "year":1980,
                    "month":10,
                    "day":10
                },
                "email":customer_info['email'],
                "phone":customer_info['phone']
    }
    headers = {
                "Content-Type":"application/json",
                "Authorization" : "Basic cHJpdmF0ZS03NzUxOkItcWEyLTAtNWYwMzFjZGQtMC0zMDJkMDIxNDQ5NmJlODQ3MzJhMDFmNjkwMjY4ZDNiOGViNzJlNWI4Y2NmOTRlMjIwMjE1MDA4NTkxMzExN2YyZTFhODUzMTUwNWVlOGNjZmM4ZTk4ZGYzY2YxNzQ4",
                "Simulator" : "EXTERNAL",
                "Access-Control-Allow-Origin":"*"
    }
    body = json.dumps(j_data)
    table = client.Table(table_name)
    try:
        response = table.get_item(Key = {'mail_id':j_data['email']})
        table_res = response['Item']
    except:
        res = requests.post("https://api.test.paysafe.com/paymenthub/v1/customers", body, headers = headers)
        res_json = res.json()
        if res.status_code == 201:
            print(res_json)
            response = table.put_item(
                    Item={
                        'mail_id':j_data['email'],
                        'user_name':j_data['merchantCustomerId'],
                        'customer_id':res_json['id']
                        }
            )
            print("appending to table\n")
            customer_info['customer_id'] = res_json['id']
        else:

            return respond(None, res_json)
    else:
        customer_id = table_res['customer_id']
        customer_info['customer_id'] = customer_id
    j_data = {
        "merchantRefNum": data['merchantRefNum'],
        "paymentTypes":["CARD"]
    }
    body = json.dumps(j_data)
    id = customer_info['customer_id']
    url = "https://api.test.paysafe.com/paymenthub/v1/customers/"+id+"/singleusecustomertokens"
    print(url)
    res = requests.post(url, body, headers = headers)
    j_res = res.json()
    print(j_res['singleUseCustomerToken'])
    res = {"singleUseCustomerToken": j_res['singleUseCustomerToken'],
            "customer_id": id,
            "environemnt":os.getenv('environment'),
            "currency":os.getenv('currency'),
            "m_description":os.getenv('m_dynamicDescriptor'),
            "m_phone":os.getenv('m_phone'),
            "locale":os.getenv('locale'),
            "config":os.getenv('public_base64')
         }
    return respond(None,res)
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

import boto3
import base64
import requests
import json
from requests_aws4auth import AWS4Auth

region = 'us-east-1' # e.g. us-west-1
service = 'es'
credentials = boto3.Session().get_credentials()
awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, region, service, session_token=credentials.token)

host = 'https://search-[your_endpoint].es.amazonaws.com' # the Amazon ES domain, including https://
index = 'unstructured_documents-index'
doc_type = '_doc'
p_url = host + '/' + '_ingest/pipeline/attachment'
url = host + '/' + index + '/' + doc_type + '/' + '?pipeline=attachment'
headers = { "Content-Type": "application/json" }
s3 = boto3.client('s3')

# temparary variables
input_file = ''
index_id = ''

# Lambda execution starts here
def handler(event, context):
    for record in event['Records']:
        # Get the bucket name and key for the new file
        bucket = record['s3']['bucket']['name']
        key = record['s3']['object']['key']
        # Get file name and encode it into base64
        obj = s3.get_object(Bucket=bucket, Key=key)
        with open(obj['Body'], "rb") as attachment_file:
            encoded_data = base64.b64encode(attachment_file.read())   
        payload = { "data": encoded_data } 
        # create attachment pipeline
        p_data = {"description": "Field for processing file attachment", "processors": [ { "attachment": { "field": "data"} } ] }
        p = requests.put(p_url, auth=awsauth, data=json.dumps(p_data), headers=headers)
        print(p.text)
        # ingest a unstructured file
        r = requests.post(url, auth=awsauth, data=json.dumps(payload), headers=headers)
        print(r.text)

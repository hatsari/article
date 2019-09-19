import boto3
import base64
import requests
import json
from requests_aws4auth import AWS4Auth
import uuid

region = 'us-east-1' # e.g. us-west-1
service = 'es'
credentials = boto3.Session().get_credentials()
awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, region, service, session_token=credentials.token)

host = 'https://search-esfordocs-j7i6wjlelkxzfwdnwz654v3igq.us-east-1.es.amazonaws.com'    # the Amazon ES domain, including https://
index = 'documents-index'
doc_type = '_doc'
p_url = host + '/' + '_ingest/pipeline/attachment'
url = host + '/' + index + '/' + doc_type + '/' + '?pipeline=attachment'
i_url = host + '/' + index + '/' + '_settings'
i_data = { "index": {"highlight.max_analyzed_offset" : 100000000 }}
headers = { "Content-Type": "application/json" }
s3 = boto3.client('s3')

# Lambda execution starts here
def handler(event, context):
    for record in event['Records']:
        # Get the bucket name and key for the new file
        bucket = record['s3']['bucket']['name']
        key = record['s3']['object']['key']
        # Get file name and encode it into base64
#        obj = s3.get_object(Bucket=bucket, Key=key)
        download_path = '/tmp/{}{}'.format(uuid.uuid4(), key)
        s3.download_file(bucket, key, download_path)
#        obj_data = obj['Body'].read()
#        encoded_data = base64.b64encode(obj_data)   
    with open(download_path, "rb") as attachment_file:
        encoded_data = base64.b64encode(attachment_file.read())   
    print("download_path: " + download_path)
    payload = { "data": encoded_data } 
    # create attachment pipeline
    p_data = {"description": "Field for processing file attachment", "processors": [ { "attachment": { "field": "data"} } ] }
    p = requests.put(p_url, auth=awsauth, data=json.dumps(p_data), headers=headers)
    print("p text: " + p.text)
    p.close()
    r = requests.post(url, auth=awsauth, data=json.dumps(payload), headers=headers)
    print("r reason: " + r.text)
    r.close()
    # increase max_analyzed_offset
    # curl -XPUT $es_endpoint/pdf_doc/_settings -d '{ "index": {"highlight.max_analyzed_offset" : 100000000 }}' -H 'Content-Type: application/json'
    inc_para = requests.put(i_url, auth=awsauth, data=json.dumps(i_data), headers=headers)
    print("parameter text: " + inc_para.text)
    inc_para.close()

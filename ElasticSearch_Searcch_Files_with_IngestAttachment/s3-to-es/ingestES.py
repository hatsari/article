import boto3
import base64
import requests
import json
import urllib
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

# function to prevent filename containg space from casuing NoSuchKey error
def encode_key(bucket, key_raw):
    key_utf8 = urllib.unquote_plus(key_raw.encode('utf-8'))
    key = key_utf8.decode('utf-8')
    print('bucket name: ' + bucket + ', file name: ' + key)
    return key

# function to convert s3 object to base64 encoding
def create_doc_data(bucket, key):
    obj = s3.get_object(Bucket=bucket, Key=key)
    obj_data = obj['Body'].read()
    encoded_data = base64.b64encode(obj_data)
    return encoded_data

# Lambda execution starts here
def handler(event, context):
    for record in event['Records']:
        # Get the bucket name and key for the new file
        bucket = record['s3']['bucket']['name']
        key_raw = record['s3']['object']['key']
        key = encode_key(bucket, key_raw)
        # Get file name and encode it into base64
        #obj = s3.get_object(Bucket=bucket, Key=key)
        #obj_data = obj['Body'].read()
        #encoded_data = base64.b64encode(obj_data)   
        payload = { "data": create_doc_data(bucket, key) } 
        # create attachment pipeline
        p_data = {"description": "Field for processing file attachment", "processors": [ { "attachment": { "field": "data"} } ] }
        p = requests.put(p_url, auth=awsauth, data=json.dumps(p_data), headers=headers)
        print("pipeline created: " + p.text)
        p.close()
        # ingest a file into ES
        r = requests.post(url, auth=awsauth, data=json.dumps(payload), headers=headers)
        print("ingestion status: " + r.text)
        r.close()
        # increase max_analyzed_offset
        # curl -XPUT $es_endpoint/pdf_doc/_settings -d '{ "index": {"highlight.max_analyzed_offset" : 100000000 }}' -H 'Content-Type: application/json'
        inc_para = requests.put(i_url, auth=awsauth, data=json.dumps(i_data), headers=headers)
        print("parameter status: " + inc_para.text)
        inc_para.close()

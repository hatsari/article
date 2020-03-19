#!/bin/python
import os
import base64
import requests
#import elasticsearch
from elasticsearch import Elasticsearch
import logging
import json

#ES_HOST="https://search-[your_endpoint].es.amazonaws.com"
#ES_PORT="443"
obj="sample.pdf"
#INDEX_ID="4"
### new variables
host = 'https://search-[your_endpoint].es.amazonaws.com'
index = 'docs-index'
doc_type = '_doc'
index_id = '1'
p_url = host + '/' + '_ingest/pipeline/attachment'
url = host + '/' + index + '/' + doc_type + '/' + '?pipeline=attachment'
i_url = host + '/' + index + '/' + '_settings'
i_data = { "index": {"highlight.max_analyzed_offset" : 100000000 }}
headers = { "Content-Type": "application/json" }

if __name__ == '__main__':
#    logging.basicConfig(level=logging.ERROR)
#    es = connect_elasticsearch()
    with open(obj, "rb") as attachment_file:
        encoded_data = base64.b64encode(attachment_file.read())   
    payload = { "data": encoded_data } 
    headers = {"Content-Type": "application/json"}
    # create attachment pipeline
    print("p_url is" + p_url)
    p_data = {"description": "Field for processing file attachment", "processors": [ { "attachment": { "field": "data"} } ] }
    p = requests.put(p_url, data=json.dumps(p_data), headers=headers)
    print(p.text)
    # increase parameter
    inc_para = requests.put(i_url, data=json.dumps(i_data), headers=headers)
    # ingest pdf attachment
    r = requests.post(url, data=json.dumps(payload), headers=headers)
    print(r.text)
    print(r.reason)

'''
# create attachment pipeline
    p_data = {"description": "Field for processing file attachment", "processors": [ { "attachment": { "field": "data"} } ] }
    p = requests.put(ES_HOST +  "/_ingest/pipeline/attachment", data=json.dumps(p_data), headers=headers)
    print(p.text)
    inc_para = requests.put(i_url, auth=awsauth, data=json.dumps(i_data), headers=headers)
    print(inc_para.text)
    # ingest pdf attachment
    r = requests.post(ES_HOST +  "/pdf_doc/_doc/"+ INDEX_ID + "?pipeline=attachment", data=json.dumps(payload), headers=headers)
    print(r.text)
'''
'''
## delete index
# curl -XDELETE "https://search-[your_endpoint].es.amazonaws.com/[index_name]/*"
'''

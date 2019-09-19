#!/bin/python
# ref: https://towardsdatascience.com/getting-started-with-elasticsearch-in-python-c3598e718380
# ref2: https://www.elastic.co/guide/en/elasticsearch/plugins/current/using-ingest-attachment.html

import os
import base64
import requests
#import elasticsearch
from elasticsearch import Elasticsearch
import logging
import json

ES_HOST="https://search-docmgmt-iljka4hrox4iyfiscdbyedwvbe.us-east-1.es.amazonaws.com"
ES_PORT="443"
INPUT_FILE="sample_ko.pptx"
INDEX_ID="4"
'''
with open("sample2.pdf", "rb") as pdf_file:
    encoded_string = base64.b64encode(pdf_file.read())
b64_file = open("sample2.b64", "w")
b64_file.write(encoded_string)
b64_file.close()
'''

def connect_elasticsearch():
    _es = None
    _es = Elasticsearch([{'host': ES_HOST, 'port': ES_PORT}])
    if _es.ping():
        print("It is connected")
    else:
        print("Error: It's not Connected")
    return _es

def create_index(es_object, index_name='recipes'):
    created = False
    # index settings
    settings = {
        "settings": {
            "number_of_shards": 1,
            "number_of_replicas": 0
        },
        "mappings": {
            "members": {
                "dynamic": "strict",
                "properties": {
                    "title": {
                        "type": "text"
                    },
                    "submitter": {
                        "type": "text"
                    },
                    "description": {
                        "type": "text"
                    },
                    "calories": {
                        "type": "integer"
                    },
                }
            }
        }
    }
    try:
        if not es_object.indices.exists(index_name):
            # Ignore 400 means to ignore "Index Already Exist" error.
            es_object.indices.create(index=index_name, ignore=400, body=settings)
            print('Created Index')
            created = True
    except Exception as ex:
        print(str(ex))
    finally:
        return created
    
if __name__ == '__main__':
    logging.basicConfig(level=logging.ERROR)
    es = connect_elasticsearch()
    with open(INPUT_FILE, "rb") as pdf_file:
        encoded_data = base64.b64encode(pdf_file.read())   
    payload = { "data": encoded_data } 
    headers = {"Content-Type": "application/json"}

# create attachment pipeline
    p_data = p_data = {"description": "Field for processing file attachment", "processors": [ { "attachment": { "field": "data"} } ] }
    p = requests.put(ES_HOST +  "/_ingest/pipeline/attachment", data=json.dumps(p_data), headers=headers)
    print(p.text)
    # ingest pdf attachment
    if es is not None:
#        create_index()
        r = requests.post(ES_HOST +  "/pdf_doc/_doc/"+ INDEX_ID + "?pipeline=attachment", data=json.dumps(payload), headers=headers)
        print(r.text)

## increase the index setting
#curl -XPUT $es_endpoint/pdf_doc/_settings -d '{ "index": {"highlight.max_analyzed_offset" : 100000000 }}' -H 'Content-Type: application/json'

### sample index
#es_endpoint="https://search-lottechem-bqw3xcrcp2jbjd2jnizwdlz6fi.us-east-1.es.amazonaws.com"
#curl -XPUT $es_endpoint/cannon/_doc/1 -d '{"director": "Burton, Tim", "genre": ["Comedy","Sci-Fi"], "year": 1996, "actor": ["Jack Nicholson","Pierce Brosnan","Sarah Jessica Parker"], "title": "Mars Attacks!"}' -H 'Content-Type: application/json'
#### delete elasticsearch
#curl -XDELETE http://[you_host]:9200/[index_name]/_doc/*
#curl -XDELETE http://[your_host]:9200/[your_index_name_here]
#curl -XDELETE "http://[your_host]:9200/*"
#curl -X GET "http://[your_host]:9200/_stats/"
##### encoding test
'''
>>> import requests
>>> b64_file = open('sample.b64','rb')
>>> ES_HOST="https://search-lottechemicallab-csjd5dil4ks4jotd24ovg6patu.us-east-1.es.amazonaws.com"
>>> b64_data = b64_file.read()
>>> b64_file.close()
>>> with open("sample2.pdf", "rb") as b64_file:
...   b64_data = b64_file.read()
... 
>>> headers = {'Content-Type': 'application/json'}
>>> payload = {'data': b64_data}
>>> r = requests.post(ES_HOST +  "/myindex/1?pipeline=attachment", data=payload, headers=headers)
>>> 

'''

#os.system("curl -X PUT \"" + ES_HOST + "")
'''
# Example documents
curl -X PUT "localhost:9200/index_1/_doc/1?pretty" -H 'Content-Type: application/json' -d'
{
  "text": "Document in index 1"
}
'
curl -X PUT "localhost:9200/index_2/_doc/2?refresh=true&pretty" -H 'Content-Type: application/json' -d'
{
  "text": "Document in index 2"
}
'
curl -X GET "localhost:9200/index_1,index_2/_search?pretty" -H 'Content-Type: application/json' -d'
{
  "query": {
    "terms": {
      "_index": ["index_1", "index_2"] 
    }
  },
  "aggs": {
    "indices": {
      "terms": {
        "field": "_index", 
        "size": 10
      }
    }
  },
  "sort": [
    {
      "_index": { 
        "order": "asc"
      }
    }
  ],
  "script_fields": {
    "index_name": {
      "script": {
        "lang": "painless",
        "source": "doc[\u0027_index\u0027]" 
      }
    }
  }
}
'


curl -X PUT "localhost:9200/_ingest/pipeline/attachment?pretty" -H 'Content-Type: application/json' -d'
{
  "description" : "Extract attachment information",
  "processors" : [
    {
      "attachment" : {
        "field" : "data"
      }
    }
  ]
}
'
curl -X PUT "localhost:9200/my_index/_doc/my_id?pipeline=attachment&pretty" -H 'Content-Type: application/json' -d'
{
  "data": "e1xydGYxXGFuc2kNCkxvcmVtIGlwc3VtIGRvbG9yIHNpdCBhbWV0DQpccGFyIH0="
}
'
curl -X GET "localhost:9200/my_index/_doc/my_id?pretty"
'''

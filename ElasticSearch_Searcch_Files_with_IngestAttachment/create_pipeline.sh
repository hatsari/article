ES_HOST="https://search-lottechemicallab-csjd5dil4ks4jotd24ovg6patu.us-east-1.es.amazonaws.com"
curl -XPUT '$ES_HOST/_ingest/pipeline/attachment' -H 'Content-Type: application/json' -d'
{
  "description" : "Field for processing file attachments",
  "processors" : [
    {
      "attachment" : {
        "field" : "data"
      }
    }
  ]
}
'

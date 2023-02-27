curl -s -H 'Content-Type: application/json' -XPUT 'http://localhost:9200/_all/_settings?pretty' -d ' {
    "index":{
             "blocks" : {"read_only_allow_delete":"false"}
    }
}'
CREATE EXTERNAL TABLE hive_movies (
    hive_year double,
    hive_title string,
    hive_info map<string,string>
)
STORED BY 'org.apache.hadoop.hive.dynamodb.DynamoDBStorageHandler'
TBLPROPERTIES (
    "dynamodb.table.name" = "Movies",
    "dynamodb.column.mapping" = 
    "hive_year:year,hive_title:title,hive_info:info",
    "dynamodb.type.mapping" =
    "hive_year:N",
    "dynamodb.null.serialization" = "true"
);

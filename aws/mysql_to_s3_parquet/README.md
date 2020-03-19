# How to Move MySQL data to S3 with parquet format
ref: https://medium.com/@wwwbbb8510/migrate-on-premise-rdbms-mysql-data-to-aws-data-lake-553ffb7ae310
ref: https://aws.amazon.com/blogs/big-data/use-sqoop-to-transfer-data-from-amazon-emr-to-amazon-rds/

## Steps
1. create mysql rds on aws
2. dump example data into mysql
3. create EMR
4. migrate data from mysql to Hadoop using sqoop
5. migrate data from HDFS to S3 using distcp

## Create mysql rds on aws
easy

``` shell
mysql -u user -p -h xxx.endpoint.mysql.amazon
```
## dump example data into mysql
download sample data from github(https://github.com/datacharmer/test_db)

``` shell
git clone https://github.com/datacharmer/test_db.git
```

import employees.sql to mysql

``` shell
mysql -u user -p -h xxx.endpoint.mysql.amazon < employees.sql

select count(*) from employee;
```

## create EMR
- create cluster
- advanced setting
- selecting ' emr-5.29, hadoop, spark, sqoop '
- instance: m5.xlarge
- master: 1, slave: 2

### connect emr
- ssh connect

## migrate data from mysql to Hadoop using sqoop
### install jdbc driver

``` shell
wget http://dev.mysql.com/get/Downloads/Connector-J/mysql-connector-java-5.1.38.tar.gz
tar -xvzf mysql-connector-java-5.1.38.tar.gz
sudo cp mysql-connector-java-5.1.38/mysql-connector-java-5.1.38-bin.jar /usr/lib/sqoop/lib/
```
### create hdfs directory

``` shell
hadoop fs -mkdir /mysql/
```

### run sqoop command
- table name: employees
- rows: 30,024

``` shell
[hadoop@ip-172-31-0-61 ~]$ cat sqoop_import_mysql.sh
sqoop import --connect jdbc:mysql://db-rds.amazonaws.com/employees --username admin --P --table employees --target-dir /mysql/employees --m 2 --as-parquetfile --compress --compression-codec org.apache.hadoop.io.compress.SnappyCodec

[hadoop@ip-172-31-0-61 ~]$ sh -x sqoop_import_mysql.sh
```

### check parquet files

``` shell
hadoop fs -ls /mysql/employees
```

### copy parquet files to s3
- create s3 bucket

``` shell
aws s3 mb s3://alex-rds-s3/
```

- run distcp script

``` shell
hadoop distcp hdfs://emrcluster-dns.amazonaws.com:8020/mysql/employees s3a://alex-rds-s3/
```

- check parquet files on S3

``` shell
aws s3 mb s3://alex-rds-s3/employees/
```

### performance
#### employees table
- table name: employees
- rows: 300,024
- elapsed time: 49sec
  - sqoop time: 26sec
  - distcp time: 23 sec

#### salaries table
- table name: salaries
- rows: 2,844,047
- elapsed time: 52sec
  - sqoop time: 28sec
  - distcp time:24sec

### additional command
- delete directory including files
``` shell
[hadoop@ip-172-31-0-61 ~]$ hadoop fs -rm -r -f /mysql/salaries
```

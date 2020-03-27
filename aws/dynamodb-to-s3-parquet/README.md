# ETL - AWS Dynamodb to S3 parquet
date: 2020.03.27
written by: Kim Yongki

## Creating Sample Table
1. Copy the following program and paste it into a file named [MoviesCreateTable.py](MoviesCreateTable.py).
2. To run the program, enter the following command.
``` shell
$ python MoviesCreateTable.py
```
### references
- ref: https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/GettingStarted.Python.01.html

## Loading Sample Data
1. Download the sample data archive: [moviedata.zip](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/samples/moviedata.zip)
2. Extract the data file (moviedata.json) from the archive.
3. Copy the moviedata.json file into your current directory.

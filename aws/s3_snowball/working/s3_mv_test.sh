#!/bin/bash

s3_org=your-own-org-bucket
s3_dest=your-own-dest-bucket

dir_count=10
file_count_per_dir=10

function create_dir_structure {
    for i in $(seq 1 $dir_count);do
        mkdir dir$i
    done
}

function create_files {
    for i in $(seq 1 $dir_count);do
        for j in $(seq 1 $file_count_per_dir);do
            dd if=/dev/urandom of=dir$i/dir$i_file_$j.raw bs=1k count=200
        done
    done    
}

function create_s3_bucket {
    aws s3 mb s3://[$s3_org $s3_dest]
}

function file_sync {
    aws s3 sync . s3://$s3_org
}

function shuffle_files_on_s3 {
    for i in {1..100};do
        for j in {1..100};do
#            aws s3 mv s3://$s3_org/dir$i/dir$i_file_$j.raw s3://$s3_dest/dir$((i+10))/dir$((i+10))_file_$((j+10)).raw
            aws s3 mv s3://$s3_org/dir$i/file_$j.raw s3://$s3_dest/dir$((i+10))/dir$((i+10))_file_$((j+10)).raw
        done
    done
}

## main
create_dir_structure
echo "dir structures are created"

create_files
echo "files are created"

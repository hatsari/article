#!/bin/python

'''
using smart_open
working fine with streaming upload(reducing memory usage)
but, metadata can't be added
'''

import boto3
import smart_open
import tarfile
import io
import os.path
from datetime import datetime

## 'smart_open' package is needed to run this program
# pip install smart_open

bucket_name = "your-own-dest-seoul"
s3 = boto3.client('s3', 'ap-northeast-2')
transport_params = {'session': boto3.Session(profile_name='snowball'), 'resource_kwargs': { 'endpoint_url': 'https://s3.ap-northeast-2.amazonaws.com' }}
tarfiles_one_time = 2000
source_file = 'filelist_dir1_10000.txt' 

#org_file = ["Logs/a.txt", "Logs/b.txt"]
def rename_file(org_file):
    return org_file.replace('\n','') + "_new_buffer"
org_files = open(source_file).readlines()
target_files = list(map(rename_file, org_files))

#### don't need to modify from here
current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
error_file = ('error_tar_%s.log' % current_time)
successlog_file = ('success_tar_%s.log' % current_time)
batch_tar = ('snowball_batch_%s.tar' % current_time)
key_name = batch_tar

#s3_session = boto3.Session( aws_access_key_id='XXXXXXXXXXXXXXXXXXXX', aws_secret_access_key='XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX')
#transport_params = {'session': s3_session , 'resource_kwargs': { 'endpoint_url': 'https://s3.ap-northeast-2.amazonaws.com' }}
out = io.BytesIO()
line_break = len(org_files) / tarfiles_one_time + 1
final_line_list = [ i*tarfiles_one_time-1 for i in range(1,line_break)]
final_line_list.append(len(org_files)-1)
s3_location = "s3://" + bucket_name + "/" + batch_tar

def add_metadata_to_s3(bucket_name, batch_tar):
    s3.copy_object(Key=key_name, Bucket=bucket_name,
               CopySource={"Bucket": bucket_name, "Key": key_name},
               Metadata={"snowball-auto-extract": "true"},
               MetadataDirective="REPLACE")
def log_non_exist(org_file):
    with open(error_file,'a+') as err:
        err.write(org_file + " does not exist\r\n")
def log_success(target_file):
    with open(successlog_file,'a+') as success:
        success.write(target_file + " is archived successfully\r\n")

with smart_open.open(s3_location, 'wb', transport_params=transport_params) as fout:
    with tarfile.open(fileobj=out, mode="w") as tar:
        for index in range(len(org_files)):
            org_file = org_files[index].replace('\n','')
            target_file = target_files[index]
            if os.path.isfile(org_file):
                tar.add(org_file, arcname=target_file)
                #print target_file + " is uploading"
                log_success(target_file)
            else:
                log_non_exist(org_file)
                print org_file + " is not exist..............................................."
            #print "tar, out size: " + str(sys.getsizeof(out))
            if index in final_line_list:
                print "sending to s3..........................................................."
                #s3.upload_fileobj(out, bucket_name, 'batch41.tar',ExtraArgs={'Metadata': {'snowball-auto-extract': 'true'}})
                fout.write(out.getvalue())
                out.seek(0)
                out.truncate()
try:
    add_metadata_to_s3(bucket_name, batch_tar)
except:
    print "updating metadata failed"
else:
    print "metadata is updated"
    meta_out = s3.head_object(Bucket=bucket_name, Key=key_name)
    print ('metadata info: %s' % str(meta_out)) 
    log_success(str(meta_out))



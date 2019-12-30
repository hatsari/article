#!/bin/python

'''
status: completed
version: v7
way: using multi-part uploading
ref: https://gist.github.com/teasherm/bb73f21ed2f3b46bc1c2ca48ec2c1cf5
'''

import boto3
import tarfile
import io
import os.path
from datetime import datetime
import sys

bucket_name = "your-own-dest-seoul"
s3 = boto3.client('s3', region_name='ap-northeast-2')
#s3 = boto3.client('s3', region_name='ap-northeast-2', endpoint_url='https://s3.ap-northeast-2.amazonaws.com', aws_access_key_id=None, aws_secret_access_key=None)
tarfiles_one_time = 1000
source_file = 'filelist_dir1_10000.txt' 

## Caution: you have to modify rename_file function to fit your own naming rule
def rename_file(org_file):
    return org_file.replace('\n','') + "_new_buffer"
org_files_list = open(source_file).readlines()
target_files_list = list(map(rename_file, org_files_list))
## to use same name (org file name == target file name), uncomment below line
#target_files_list = org_files_list

#### don't need to modify from here
current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
error_file = ('error_%s_%s.log' % (source_file, current_time))
successlog_file = ('success_%s_%s.log' % (source_file, current_time))
batch_tar = ('snowball-batch-%s-%s.tar' % (source_file, current_time))
key_name = batch_tar
out = io.BytesIO()
parts = []

line_break = len(org_files_list) / tarfiles_one_time + 1
final_line_list = [ i*tarfiles_one_time-1 for i in range(1,line_break)]
final_line_list.append(len(org_files_list)-1)
s3_location = "s3://" + bucket_name + "/" + batch_tar

def add_metadata_to_s3(bucket_name, batch_tar):
    s3.copy_object(Key=key_name, Bucket=bucket_name,
               CopySource={"Bucket": bucket_name, "Key": key_name},
               Metadata={"snowball-auto-extract": "true"},
               MetadataDirective="REPLACE")
def log_error(org_file, str_suffix):
    with open(error_file,'a+') as err:
        err.write(org_file + str_suffix)
def log_success(target_file, str_suffix):
    with open(successlog_file,'a+') as success:
        success.write(target_file + str_suffix)

def flush_mem(out):
    out.seek(0)
    out.truncate()

def create_mpu():
    mpu = s3.create_multipart_upload(Bucket=bucket_name, Key=key_name, Metadata={"snowball-auto-extract": "true"})
    mpu_id = mpu["UploadId"]
    return mpu_id

def upload_mpu(mpu_id, data, index):
    part = s3.upload_part(Body=data, Bucket=bucket_name, Key=key_name, UploadId=mpu_id, PartNumber=index)
    parts.append({"PartNumber": index, "ETag": part["ETag"]})
    print ('parts list: %s' % str(parts))
    return parts

def complete_mpu(mpu_id, parts):
    result = s3.complete_multipart_upload(
        Bucket=bucket_name,
        Key=key_name,
        UploadId=mpu_id,
        MultipartUpload={"Parts": parts})
    return result

def main():
    mpu_id = create_mpu()
    parts_index = 1

    with tarfile.open(fileobj=out, mode="w") as tar:
        for index in range(len(org_files_list)):
            org_file = org_files_list[index].replace('\n','')
            target_file = target_files_list[index]
            if os.path.isfile(org_file):
                tar.add(org_file, arcname=target_file)
                #print target_file + " is uploading"
                log_success(target_file, " is archived successfully\n")
            else:
                log_error(org_file," does not exist\n")
                print org_file + " is not exist..............................................."
            #print "tar, out size: " + str(sys.getsizeof(out))
            if index in final_line_list:
                print "sending to s3..........................................................."
                print target_file + " is uploading"
                mpu_parts = upload_mpu(mpu_id, out.getvalue(), parts_index)
                parts_index += 1
                out.seek(0)
                out.truncate()

    print(complete_mpu(mpu_id, mpu_parts))
    ### print metadata
    meta_out = s3.head_object(Bucket=bucket_name, Key=key_name)
    print ('\n\n metadata info: %s' % str(meta_out)) 
    log_success(str(meta_out), '!!\n')

    print ("\n\n tar file: %s" % key_name)
    log_success(key_name, ' is uploaded successfully')

if __name__ == "__main__":
    main()

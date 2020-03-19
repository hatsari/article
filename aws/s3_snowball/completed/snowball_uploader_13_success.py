#-*- encoding: utf8 -*-
'''
status: failed
version: v11
way: using multi-part uploading
ref: https://gist.github.com/teasherm/bb73f21ed2f3b46bc1c2ca48ec2c1cf5
changelog:
  - 2020.02.22
    - limiting multi-thread numbers
    - adding multi-threading to improve performance 
    - adding fifo operation to reducing for big file which is over max_part_size 
  - 2020.02.19
    - removing tarfiles_one_time logic
    - spliting buffer by max_part_size
  - 2020.02.18:
    - supprt snowball limit:
      - max_part_size: 512mb
      - min_part_size: 5mb
  - 2020.02.14: 
    - modifying for python3 
    - support korean in Windows
  - 2020.02.12: adding features 
    - gen_filelist by size
  - 2020.02.10: changing filename from tar_to_s3_v7_multipart.py to snowball_uploader_8.py
  - adding features which can split tar file by size and count.
  - adding feature which create file list
  - showing help message
'''

import boto3
import tarfile
import io
import os.path
from datetime import datetime
import sys
import shutil
import threading
import time

bucket_name = "your-own-dest-seoul"
s3 = boto3.client('s3', endpoint_url='https://s3.ap-northeast-2.amazonaws.com')
#s3 = boto3.client('s3', region_name='ap-northeast-2', endpoint_url='https://s3.ap-northeast-2.amazonaws.com', aws_access_key_id=None, aws_secret_access_key=None)
target_path = '.'   ## very important!! change to your source directory
max_tarfile_size = 100 * 1024 ** 2 # 70GB
max_part_size = 6 * 1024 ** 2 # 100MB
min_part_size = 5 * 1024 ** 2 # 5MB
max_thread = 10  # max thread number
sleep_time = 3   # thread sleep time when reaching max threads
if os.name == 'nt':
    filelist_dir = "C:/tmp/fl_logdir_dkfjpoiwqjefkdjf/"  #for windows
else:
    filelist_dir = '/tmp/fl_logdir_dkfjpoiwqjefkdjf/'    #for linux

## Caution: you have to modify rename_file function to fit your own naming rule
#def rename_file(org_file):
#    return org_file.replace('\n','') + "_new_buffer"
#org_files_list = open(source_file).readlines()
#target_files_list = list(map(rename_file, org_files_list))
## to use same name (org file name == target file name), uncomment below line
#target_files_list = org_files_list
#s3_location = "s3://" + bucket_name + "/" + batch_tar

#### don't need to modify from here
current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
parts = []

def gen_filelist():
    sum_size = 0
    fl_prefix = 'fl_'
    fl_index = 1
    shutil.rmtree(filelist_dir,ignore_errors=True)
    try:
        os.mkdir(filelist_dir)
    except: pass
    print('generating file list by size %s bytes' % max_tarfile_size)
    for r,d,f in os.walk(target_path):
        for file in f:
            file_name = os.path.join(r,file)
            fl_name = filelist_dir + '/' + fl_prefix + str(fl_index) + ".txt"
            sum_size = sum_size + os.path.getsize(file_name)
            if max_tarfile_size < sum_size:
                fl_index = fl_index + 1            
                sum_size = 0
            print('%s' % file_name)
            with open(fl_name, 'a', encoding='utf8') as fl_content:
                fl_content.write(file_name + '\n')                
    print('file lists are generated!!')
    print('check %s' % filelist_dir)
    return os.listdir(filelist_dir)

def log_error(org_file, str_suffix):
    with open(error_file,'a+', encoding='utf8') as err:
        err.write(org_file + str_suffix)

def log_success(target_file, str_suffix):
    with open(successlog_file,'a+', encoding='utf8') as success:
        success.write(target_file + str_suffix)

def create_mpu():
    mpu = s3.create_multipart_upload(Bucket=bucket_name, Key=key_name, Metadata={"snowball-auto-extract": "true"})
    mpu_id = mpu["UploadId"]
    return mpu_id

def upload_mpu(mpu_id, data, index):
    #part = s3.upload_part(Body=data, Bucket=bucket_name, Key=key_name, UploadId=mpu_id, PartNumber=index, ContentLength=max_buf_size)
    part = s3.upload_part(Body=data, Bucket=bucket_name, Key=key_name, UploadId=mpu_id, PartNumber=index)
    parts.append({"PartNumber": index, "ETag": part["ETag"]})
    #print ('parts list: %s' % str(parts))
    return parts

def complete_mpu(mpu_id, parts):
    result = s3.complete_multipart_upload(
        Bucket=bucket_name,
        Key=key_name,
        UploadId=mpu_id,
        MultipartUpload={"Parts": parts})
    return result

def thread_max_check(sleep_time):
    running_thread = threading.activeCount()
    while running_thread >= max_thread:
        print ('current running thread: %s' % running_thread)
        print ('max threads reached')
        time.sleep(sleep_time)
        running_thread = threading.activeCount()
    else:
        print ('current running thread: %s' % running_thread)
        pass
def adjusting_parts_order(mpu_parts):
    return sorted(mpu_parts, key=lambda item: item['PartNumber'])

def copy_to_snowball(org_files_list, target_files_list):
    recv_buf = io.BytesIO()
    mpu_id = create_mpu()
    parts_index = 1
    lock = threading.Lock()
    with tarfile.open(fileobj=recv_buf, mode="w") as tar:
        for index in range(len(org_files_list)):
            org_file = org_files_list[index].replace('\n','')
            target_file = target_files_list[index].replace('\n','')
            if os.path.isfile(org_file):
                tar.add(org_file, arcname=target_file)
                print ('1. from %s is archiving' % target_file )
                log_success(" %s is archiving \n" % target_file )
                recv_buf_size = recv_buf.tell()
                if recv_buf_size > max_part_size:
                    print('multi part upload is starting, size: %s' % recv_buf_size)
                    chunk_count = int(recv_buf_size / max_part_size)
                    mpu_threads = []
                    for buf_index in range(chunk_count):
                        thread_max_check(sleep_time)
                        start_pos = buf_index * max_part_size
                        recv_buf.seek(start_pos,0)
                        mpu_threads.append(threading.Thread(target = upload_mpu, args = (mpu_id, recv_buf.read(max_part_size), parts_index)))
                        mpu_threads[-1].start()
                        parts_index += 1
                        print('thread numbers: %s' % threading.activeCount())
                    mpu_parts = [ th.join() for th in mpu_threads ]
                    tmp_buf = io.BytesIO()            # added for FIFO operation
                    tmp_buf.write(recv_buf.read())    # added for FIFO operation
                    recv_buf = tmp_buf
                    recv_buf_size = recv_buf.tell()
                else:
                    print('acculating files...')
            else:
                log_error(org_file," does not exist\n")
                print (org_file + ' is not exist...............................................\n')
    recv_buf.seek(0,0)
    mpu_parts = upload_mpu(mpu_id, recv_buf.read(), parts_index)
    parts_index += 1
    mpu_parts = adjusting_parts_order(mpu_parts)
    complete_mpu(mpu_id, mpu_parts)
    ### print metadata
    meta_out = s3.head_object(Bucket=bucket_name, Key=key_name)
    print ('\n\n metadata info: %s' % str(meta_out)) 
    log_success(str(meta_out), '!!\n')
    print ("\n\n tar file: %s" % key_name)
    log_success(key_name, ' is uploaded successfully\n')

def snowball_uploader_help(**args):
    print ("Usage: %s 'genlist | cp_snowball | help'" % sys.argv[0])

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print ("Usage: %s genlist | cp_snowball | help" % sys.argv[0])  
        sys.exit()
    elif sys.argv[1] == "genlist":
        gen_filelist()
    elif sys.argv[1] == "cp_snowball":
        source_files =  os.listdir(filelist_dir)
        for sf in source_files:
            error_file = ('error_%s_%s.log' % (sf, current_time))
            successlog_file = ('success_%s_%s.log' % (sf, current_time))
            source_file = os.path.join(filelist_dir, sf)
            org_files_list = open(source_file, encoding='utf8').readlines()
            target_files_list = org_files_list
            key_name = ('snowball-%s-%s.tar' % (sf[:-4], current_time))
            print ('\n0. #####################')
            print ('0. %s copy is starting' % sf)
            copy_to_snowball(org_files_list, target_files_list)
            print ('0. %s copy is done' % sf)
            print ('\n0. #####################')
            parts = []
    else:
        snowball_uploader_help()

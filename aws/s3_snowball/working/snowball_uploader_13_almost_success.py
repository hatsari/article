#-*- encoding: utf8 -*-
'''
status: failed
version: v11
way: using multi-part uploading
ref: https://gist.github.com/teasherm/bb73f21ed2f3b46bc1c2ca48ec2c1cf5
changelog:
  - 2020.02.19
    - adding fifo operation to reducing for big file which is over max_part_size 
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

bucket_name = "your-own-dest-seoul"
s3 = boto3.client('s3', endpoint_url='https://s3.ap-northeast-2.amazonaws.com')
#s3 = boto3.client('s3', region_name='ap-northeast-2', endpoint_url='https://s3.ap-northeast-2.amazonaws.com', aws_access_key_id=None, aws_secret_access_key=None)
#tarfiles_one_time = 1000
max_size = 100 * 1000 ** 2 # 70GB
max_part_size = 20 * 1024 ** 2 # 100MB
min_part_size = 5 * 1024 ** 2 # 5MB
target_path = '.'   ## very important!! change to your source directory
if os.name == 'nt':
    filelist_dir = "C:/tmp/fl_logdir_dkfjpoiwqjefkdjf/"  #for windows
else:
    filelist_dir = '/tmp/fl_logdir_dkfjpoiwqjefkdjf/'    #for linux

#source_file = ''

## Caution: you have to modify rename_file function to fit your own naming rule
#def rename_file(org_file):
#    return org_file.replace('\n','') + "_new_buffer"
#org_files_list = open(source_file).readlines()
#target_files_list = list(map(rename_file, org_files_list))
## to use same name (org file name == target file name), uncomment below line
#target_files_list = org_files_list

#### don't need to modify from here
current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
#key_name = ('snowball-batch-%s-%s.tar' % (source_file, current_time))
#key_name = ('snowball-batch-%s.tar' % ( current_time))

parts = []
#s3_location = "s3://" + bucket_name + "/" + batch_tar

def gen_filelist():
    sum_size = 0
    fl_prefix = 'fl_'
    fl_index = 1
    shutil.rmtree(filelist_dir,ignore_errors=True)
    try:
        os.mkdir(filelist_dir)
    except: pass
    print('generating file list by size %s bytes' % max_size)
    for r,d,f in os.walk(target_path):
        for file in f:
            file_name = os.path.join(r,file)
            fl_name = filelist_dir + '/' + fl_prefix + str(fl_index) + ".txt"
            sum_size = sum_size + os.path.getsize(file_name)
            if max_size < sum_size:
                fl_index = fl_index + 1            
                sum_size = 0
            print('%s' % file_name)
            with open(fl_name, 'a', encoding='utf8') as fl_content:
                fl_content.write(file_name + '\n')                
    print('file lists are generated!!')
    print('check %s' % filelist_dir)
    return os.listdir(filelist_dir)

#def add_metadata_to_s3(bucket_name, key_name):
#    s3.copy_object(Key=key_name, Bucket=bucket_name,
#               CopySource={"Bucket": bucket_name, "Key": key_name},
#               Metadata={"snowball-auto-extract": "true"},
#               MetadataDirective="REPLACE")
def log_error(org_file, str_suffix):
    with open(error_file,'a+', encoding='utf8') as err:
        err.write(org_file + str_suffix)
def log_success(target_file, str_suffix):
    with open(successlog_file,'a+', encoding='utf8') as success:
        success.write(target_file + str_suffix)

#def flush_mem(out):
#    out.seek(0)
#    out.truncate()

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

def copy_to_snowball(org_files_list, target_files_list):
    recv_buf = io.BytesIO()
    mpu_id = create_mpu()
    parts_index = 1
    with tarfile.open(fileobj=recv_buf, mode="w") as tar:
        for index in range(len(org_files_list)):
            org_file = org_files_list[index].replace('\n','')
            target_file = target_files_list[index].replace('\n','')
            print ('\n########################')
            print ('0. program is starting')
            if os.path.isfile(org_file):
                tar.add(org_file, arcname=target_file)
                print ('1. %s is archiving\n' % target_file )
                print ('1. recv_buf size: %s' % len(recv_buf.getvalue()))
                log_success(target_file, " is archived successfully\n")
            ###################
                print ('%s is uploading\n' % key_name )
                print ("2. recv_buf pos: %s" % recv_buf.tell())
                recv_buf_size = recv_buf.tell()
                cur_pos = 0
                if recv_buf_size > max_part_size:
                    print('max file is checked')
                    print('3.big recv_buf size: %s' % recv_buf_size)
                    print('3.big recv_buf pos : %s' % recv_buf.tell())
                    while recv_buf_size > max_part_size:
                        print('4.sending big : %s' % recv_buf.tell())
                        recv_buf.seek(0,0)
                        mpu_parts = upload_mpu(mpu_id, recv_buf.read(max_part_size), parts_index)
                        parts_index += 1
                        print('4.sent big : %s' % recv_buf.tell())
                        tmp_buf = io.BytesIO()            # added for FIFO operation
                        tmp_buf.write(recv_buf.read())    # added for FIFO operation
                        print('4.moved recv to tmp')
                        recv_buf = tmp_buf
                        #cur_pos = cur_pos + max_part_size + 1
                        print('4.1.big recv_buf pos: %s' % recv_buf.tell())
                        print('4.2.big recv_buf size: %s' % len(recv_buf.getvalue()))
                        recv_buf_size = recv_buf.tell()
                    if recv_buf_size >= min_part_size:
                        recv_buf.seek(0,0)
                        print('5.sending big-small peek : %s' % recv_buf.peek())
                        mpu_parts = upload_mpu(mpu_id, recv_buf.read(max_part_size), parts_index)
                        parts_index += 1
                        recv_buf.truncate(0)
                        print('5.big-small recv_buf size: %s' % len(recv_buf.getvalue()))
                        print('5.big-small recv_buf pos : %s' % recv_buf.tell())
                    else:
                        print('6 remaining buf of big is %s' % recv_buf_size )
                        #spared_buf_size = recv_buf_size
                        #pass
                else:
                    #if spared_buf_size:
                    #    cur_pos = spared_buf_size * -1
                    if recv_buf_size < min_part_size:
                        print('7. normal recev buffer should be passed')
                        print('7.1 recv_buf size: %s' % len(recv_buf.getvalue()))
                        print('7.2 recv_buf pos : %s' % recv_buf.tell())
                        #recv_buf.seek(0,0)
                        #mpu_parts = upload_mpu(mpu_id, recv_buf.read(), parts_index)
                        #parts_index += 1
                        #recv_buf.seek(0)
                        #recv_buf.truncate(0)
            ###################
            else:
                log_error(org_file," does not exist\n")
                print (org_file + ' is not exist...............................................\n')
    print ("8. final recv_buf size: " + str(len(recv_buf.getvalue())))
    print('8.1 final recv_buf pos : %s' % recv_buf.tell())
    recv_buf.seek(0,0)
    mpu_parts = upload_mpu(mpu_id, recv_buf.read(), parts_index)
    parts_index += 1
    print ("8. %s is uploaded" % key_name)
    complete_mpu(mpu_id, mpu_parts)
    ### print metadata
    meta_out = s3.head_object(Bucket=bucket_name, Key=key_name)
    print ('\n\n metadata info: %s' % str(meta_out)) 
    log_success(str(meta_out), '!!\n')
    print ("\n\n tar file: %s" % key_name)
    log_success(key_name, ' is uploaded successfully\n')

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
            #line_break = int(len(org_files_list) / tarfiles_one_time + 1)
            #final_line_list = [ i*int(tarfiles_one_time)-1 for i in range(1,line_break)]
            #final_line_list.append(len(org_files_list)-1)
            key_name = ('snowball-%s-%s.tar' % (sf[:-4], current_time))
            copy_to_snowball(org_files_list, target_files_list)
            parts = []
    else:
        print ("Usage: %s 'genlist | cp_snowball | help'" % sys.argv[0])

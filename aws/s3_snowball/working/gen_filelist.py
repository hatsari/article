#!/bin/python
import os
import shutil

target_path = '.'
sum_size = 0
max_size = 100000
fl_prefix = 'fl_'
fl_index = 1
filelist_dir = '/tmp/fl_logdir_dkfjpoiwqjefkdjf/'
shutil.rmtree(filelist_dir,ignore_errors=True)
os.mkdir(filelist_dir)
print('generating file list by size %s bytes' % max_size)
for r,d,f in os.walk(target_path):
    for file in f:
        file_name = os.path.join(r,file)
        fl_name = filelist_dir + '/' + fl_prefix + str(fl_index) + ".txt"        
        sum_size = sum_size + os.path.getsize(file_name)
        with open(fl_name, 'a') as fl_content:
            fl_content.write(file_name + "\n")                
        if max_size < sum_size:
            fl_index = fl_index + 1            
            sum_size = 0
print('file lists are generated!!')


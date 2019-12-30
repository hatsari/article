#!/bin/sh

list_file='100000_files.txt'

for org_file in $(cat $list_file);do
    #echo $org_file
    target_file=${org_file}_new
    #echo "$target_file is added"
    #tar --transform 's,$org_file,$target_file,S' -rvf org_add.tar  $org_file
    #tar --transform 's,$org_file,$target_file,S' -cvf org_add_new.tar  --add-file=$org_file
    #tar -rvf org_add.tar --transform 's,$org_file,$target_file,S' $org_file
    #tar -rvf org_add.tar --transform "s#^#$target_file#" $org_file
    tar -rf org_add_100000.tar --transform "flags=r;s|$org_file|$target_file|" $org_file
done

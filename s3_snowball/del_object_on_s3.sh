for i in $(aws s3 ls s3://alex-s3-mv-dest-seoul/ | grep snowball | awk '{print $4}');do aws s3 rm s3://alex-s3-mv-dest-seoul/$i;done

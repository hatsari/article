# S3 VPC Endpoint
- Date: 2020.04.29
## Overview
For the security reason, it needs to connect S3 with private endpoint. VPC endpoint helps to make it possible. As well, S3 public endpoint is also available.
## Create Endpoint
follow the below direction
- https://aws.amazon.com/ko/blogs/korea/anew-vpc-endpoint-for-amazon-s3/

[create vpc endpoint](https://media.amazonwebservices.com/blog/2015/vpc_config_endpoint_5.png)
## Connect S3 via Private Endpoint
- VPC Gateway Endpoint: S3, Dynamodb

If routing table is modified correctly, you don't need to change anything. Routing table will redirect the traffic into private PATH to S3.
``` shell
route -rn
pl-78a54011 (com.amazonaws.ap-northeast-2.s3, 52.92.0.0/20, 52.219.60.0/23, 52.219.56.0/22)	vpce-0988227c7be1a5135	active No
```

DNS resolving
``` shell
[ec2-user@ip-172-31-38-36 ~]$ dig +short http://alex-own-bucket.s3-website.ap-northeast-2.amazonaws.com
s3-website.ap-northeast-2.amazonaws.com.
52.219.58.88
```

## reference
- https://aws.amazon.com/ko/blogs/korea/anew-vpc-endpoint-for-amazon-s3/

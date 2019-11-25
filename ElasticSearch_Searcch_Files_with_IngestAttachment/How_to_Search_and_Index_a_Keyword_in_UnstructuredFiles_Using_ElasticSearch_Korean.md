# How to Search and Index a Keyword in Unstructured Files Using ElasticSearch
#엘라스틱서치를 활용하여 비정형 데이터에서 키워드 검색 방법
  - Date: 2019. 09.16
  - 김용기 Yongki, Kim (kyongki@)

## Background
## 배경
자료를 찾다보면 단순히 데이터베이스 뿐만이 아니라, doc,엑셀 또는 파워포인트 같은 오피스 문서 그리고 PDF 파일과 같은 비정형 데이터, 심지어는 jpeg, png 같은 이미지에서 키워드를 검색해야 할 때가 있다. 대부분 개인 사용자들은 자신의 PC 또는 회사 공유 폴더에 각종 자료들을 모두 모아놓기만 하고, 나중에 관련 자료를 찾고자 할 때는 엄청난 시간과 인고의 노력이 필요하다. 특히나 몇주 또는 몇개월(기간은 개인 편차가 큼) 이상 지난 자료의 경우에는 기억 저편의 희미한 단서를 기반으로 파일명만 뒤적거릴 수 밖에 없다. 이런 번거로움을 줄일 수 방법을 찾고자 엘라스틱서치의 기능을 조사하였고, 비록 쉽고 편리하진 않치만 큰 비용들이지 않고 AWS의 서비스를 활용하여 이 목적을 달성할 수 있는 방법을 찾게되었다. 그리고 이를 기록하여 다른 사람들에게 도움이 되고자 한다. 작동 방식은 오피스 문서와 같은 비정형 파일을 S3에 업로드하면, lambda에서 이를 감지하여 자동으로 엘라스틱서치로 보내고 키워드를 추출해내는 것이다. 사용자는 이후 kibana에 접속하여 필요한 검색어를 사용해서, 어떤 문서에 해당 키워드가 기록되어있는지 확인할 수 있다.

## 작동 방식
  1. pdf 또는 오피스 문서를 S3에 업로드
  2. 업로드된 파일을 인코딩하고 엘라스틱서치로 보내는(ingestion) lambda 함수 작성
  3. 엘라스틱 서치에서 index pattern 생성
  4. 키바나(Kibana)에서 키워드 검색

![elasticsearch_diagram](images/elasticsearch_diagram.png)

## 엘라스틱서치로 다양한 문서에서 키워드 검색
### AWS 엘라스틱서치 기본 구성
AWS 에서 엘라스틱서치 도메인을 생성하는 것은 매우 쉽다. 그래서 자세한 설정은 아래 링크를 참고하길 바라며, 테스트 목적으로 아래 몇 가지 옵션만 선택해 주길 바란다.
  - 설치가이드: https://docs.aws.amazon.com/elasticsearch-service/latest/developerguide/es-gsg.html

#### 테스트를 위한 Data 인스턴스 옵션
  - Availability Zone: *1-AZ*
  - Instance Type: *t2.small.elasticsearch*
  - Number of Instances: 1
![elasticsearch image](images/elasticsearch_configuration.png)

#### 접근 정책(access policy)
허가되지 않은 지역에서 접근을 방지하기 위해 *access policy*를 지정해야 한다. 이 정책을 통해 오직 특정 아이피만 엘라스틱서치에 접근할 수 있도록 설정할 수 있다.
  - 자신의 IP주소 확인 방법
    * 다음 페이지를 접속하여 자신의 IP 주소 확인(http://www.myipaddress.com/what-is-my-ip-address/)
  - 위에서 확인한 IP주소를 *access policy*에 기록
  ![elasticsearch_access_policy](images/elasticsearch_access_policy.png)

### S3 Bucket
오피스 문서를 저장할 S3 버킷 생성
- 버킷 이름: [yourname]-es-docs

``` shell
aws s3 mb s3://[yourname]-es-docs
```

### Lambda를 위한 IAM Role 설정
Lambda가 정상 작동하기 위해서는 S3, CloudWatch 그리고 엘라스틱서치에 대한 권한이 필요하며, 아래 *role policy* 를 활용하여 쉽게 설정할 수 있다.
  - role name: lambda_elasticsearch_execution
  - role policy:
``` shell
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Action": [
                "logs:*"
            ],
            "Effect": "Allow",
            "Resource": "*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "s3:Get*",
                "s3:List*"
            ],
            "Resource": "*"
        },
        {
            "Sid": "VisualEditor0",
            "Effect": "Allow",
            "Action": "es:ESHttp*",
            "Resource": "arn:aws:es:*:*:*"
        }
    ]
}
```

## Lambda 함수
S3에 문서파일이 업로드되었을 때, lambda 함수가 자동으로 실행된다. 이 lambda함수는 업로드된 문서를 base64 형식으로 인코딩하고 이를 엘라스틱서치에 저장시킨다. 엘라스틱서치에서 키워드를 추출하기 위해서는 반드시 위 인코딩 작업이 필요하다.
#### ingestES lambda 함수 생성 순서
  1. lambda 코드 작성
  2. function 패키지 준비
  3. "ingestES" 함수 생성
#### lambda 코드 작성
- file name: ingestES.py

``` python
import boto3
import base64
import requests
import json
import urllib
from requests_aws4auth import AWS4Auth
import uuid

region = 'us-east-1' # e.g. us-west-1
service = 'es'
credentials = boto3.Session().get_credentials()
awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, region, service, session_token=credentials.token)

host = 'https://search-[use_your_own_endpoint].us-east-1.es.amazonaws.com'    # the Amazon ES domain, including https://
index = 'documents-index'
doc_type = '_doc'
p_url = host + '/' + '_ingest/pipeline/attachment'
url = host + '/' + index + '/' + doc_type + '/' + '?pipeline=attachment'
i_url = host + '/' + index + '/' + '_settings'
i_data = { "index": {"highlight.max_analyzed_offset" : 100000000 }}
headers = { "Content-Type": "application/json" }
s3 = boto3.client('s3')

# function to prevent filename containg space from casuing NoSuchKey error
def encode_key(bucket, key_raw):
    key_utf8 = urllib.unquote_plus(key_raw.encode('utf-8'))
    key = key_utf8.decode('utf-8')
    print('bucket name: ' + bucket + ', file name: ' + key)
    return key

# function to convert s3 object to base64 encoding
def create_doc_data(bucket, key):
    obj = s3.get_object(Bucket=bucket, Key=key)
    obj_data = obj['Body'].read()
    encoded_data = base64.b64encode(obj_data)
    return encoded_data

# Lambda execution starts here
def handler(event, context):
    for record in event['Records']:
        # Get the bucket name and key for the new file
        bucket = record['s3']['bucket']['name']
        key_raw = record['s3']['object']['key']
        key = encode_key(bucket, key_raw)
        # Get file name and encode it into base64
        #obj = s3.get_object(Bucket=bucket, Key=key)
        #obj_data = obj['Body'].read()
        #encoded_data = base64.b64encode(obj_data)
        payload = { "data": create_doc_data(bucket, key) }
        # create attachment pipeline
        p_data = {"description": "Field for processing file attachment", "processors": [ { "attachment": { "field": "data"} } ] }
        p = requests.put(p_url, auth=awsauth, data=json.dumps(p_data), headers=headers)
        print("pipeline created: " + p.text)
        p.close()
        # ingest a file into ES
        r = requests.post(url, auth=awsauth, data=json.dumps(payload), headers=headers)
        print("ingestion status: " + r.text)
        r.close()
        # increase max_analyzed_offset
        # curl -XPUT $es_endpoint/pdf_doc/_settings -d '{ "index": {"highlight.max_analyzed_offset" : 100000000 }}' -H 'Content-Type: application/json'
        inc_para = requests.put(i_url, auth=awsauth, data=json.dumps(i_data), headers=headers)
        print("parameter status: " + inc_para.text)
        inc_para.close()
```
##### 코드에 대한 부가 설명
- 엘라스틱서치가 문서파일을 인덱스하기 위해서는 *ingest attachment*플러그인이 반드시 필요하다. 다행히 AWS 엘라스틱서치는 이미 이를 지원하고 있다.
- 지원플러그인: https://docs.aws.amazon.com/elasticsearch-service/latest/developerguide/aes-supported-plugins.html

Elasticsearch Version  | Plugins
-------- | -----------------------
7.1      | * ICU Analysis
7.1      | * Ingest Attachment Processor
7.1      | * Ingest User Agent Processor
7.1      | * Seunjeon Korean Analysis
7.1      | * more ...

- 코드에서 `<p = requests.put(p_url, auth=awsauth, data=json.dumps(p_data), headers=headers)>` 이 부분이 엘라스틱서치로의 저장을 위한 *attachment pipeline*을 생성한다.
- 그리고 실제 저장은 다음 명령에서 이루어진다. `<r = requests.post(url, auth=awsauth, data=json.dumps(payload), headers=headers)>`
- *host* 변수: ElasticSearch 의 엔드포인트 지칭
- *index* 변수: Index 이름으로, 엘라스틱서치의 사용자 데이터베이스이다.

#### function 패키지 준비
- 패키지 이름: ingestES.zip

```shell
1. 위 코드를 복사하여 ingestES.py 파일로 저장

2. 파이선 가상 환경 생성
$ virtualenv ~/venv
$ source ~/venv/bin/activate

3. 가상환경에서 라이브러리 설치
$ pip install boto3 requests requests_aws4auth

4. 필요한 라이브러리를 zip 파일로 압축
$ cd $VIRTUAL_ENV/lib/python2.7/site-packages
$ zip -r ~/ingestES.zip .

5. lambda 함수를 zip 파일에 추가
$ cd ~
$ zip -g ingestES.zip ingestES.py
```
#### lambda 함수 생성
- AWS 콘솔에 접속한 후, lambda 서비스 선택
- function name: *ingestES*
- Runtime: *Python2.7*
- Execution role > Use a existing role > *lambda_elasticsearch_execution*
- *Create function* 선택
- "+ Add trigger"
  - Trigger Configuration
  - *S3*
  - Bucket Name: *[yourname]-es-docs*
  - Event type: *All object create events*
  -  *Enable trigger* 체크
- Function code
  - Handler: *ingestES.handler*
  - code entry type: *Upload a .zip file*
  - Upload: *select a prepared IngestES.zip*
- Basic settings
  - Memory(MB): *512MB*
- *Save*

#### lambda 설정 예시
![elasticsearch image](images/elasticsearch_lambda.png)

### 문서를 S3 업로드 후 ElasticSearch 상태 확인
  1. sample.pdf 파일을 S3 버킷에 업로드
``` shell
aws s3 cp sample.pdf s3://[yourname]-es-docs/
```
  2. cloudwatch logs를 통해, lambda 함수가 정상 작동하는지 확인
  3. ElasticSearch Index 상태 확인

``` shell
curl -XGET https://[endpoint_of_elasticsearch]/documents-index/_stats
```

- 엘라스틱서치의 *Index*는 mysql의 database와 유사한 개념으로 모든 데이터는 index에 저장된다.
- 예시에서 *Index* 이름은 lambda 코드에서 <documents-index> 로 지정되었으며, 원하면 다른 이름으로 변경 가능하다.

### ElasticSearch 설정
엘라스틱서치의 기능은 파일, 로그 등을 저장하고 이에 대한 스키마와 인덱스를 생성하는 것이다. 키바나(Kibana)는 대시보드 기능을 하여 실제 키워드 검색은 키바나 콘솔을 접속해서 이루어진다. AWS 엘라스틱서치는 키바나콘솔을 기본 제공하고 있으므로 AWS 엘라스틱서치 도에인 정보 페이지에서 이 키바나 콘솔 주소를 확인할 수 있다.
![elasticsearch image](images/elasticsearch_domain.png)

#### 키바나에서 Index Pattern 생성
  - 키바나 콘솔 접속
  - 메뉴에서 *management* 클릭(화면 왼쪽의 *톱니바퀴*아이콘)
  - *Index Patterns* 클릭
  - *Create index pattern* 클릭
  - index pattern: "documents-index*"
  - *Next step* 클릭
  - Time Filter field name: *I don't want to use the time filter*
  - "Create index pattern" 문구 아래에 "documents-index*" 인텍스 패턴 확인
![elasticsearch_image](images/elasticsearch_indexpattern.png)

#### Discover 메뉴에서 키워드 검색
  - 키바나 콘솔 접속
  - *discover* 메뉴 클릭(화면 왼쪽 나침반 아이콘)
  - sample.pdf 파일 정보 라인 확인
  - 다음 필드 추가 (a.title, a.content_type)
![elasticsearch_image](images/elasticsearch_search.png)

## 검증
  - 다른 한글 PPT 문서 업로드
  - cloudwatch logs 를 확인하여, lambda가 정상작동하는지 확인
  - 키바나 콘솔을 접속하고 *Discover* 메뉴로 이동
  - Search a keyword in Filters 탭에서 키워드 검색

![elasticsearch_image](images/elasticsearch_result.png)

### 엘라스틱서치를 테스트하는데 유용한 *curl* 명령어
- Create sample index
```shell
$ curl -XPUT http://localhost:9200/[index_name]/_doc/1 -d '{"director": "Burton, Tim", "genre": ["Comedy","Sci-Fi"], "year": 1996, "actor": ["Jack Nicholson","Pierce Brosnan","Sarah Jessica Parker"], "title": "Mars Attacks!"}' -H 'Content-Type: application/json'
```

- Change Index setting
```shell
$ curl -XPUT http://localhost:9200/[index_name]/_settings -d '{ "index": {"highlight.max_analyzed_offset" : 100000000 }}' -H 'Content-Type: application/json
```

- Get Index Information
```shell
$ curl -XGET http://localhost:9200/[index_name]/_stats
```

- Delete Index Data
```shell
$ curl -XDELETE http://localhost:9200/[index_name/*
```

## 향후 단계
  - Textract을 통한 이미지에서 검색어 추출 (https://aws.amazon.com/blogs/machine-learning/automatically-extract-text-and-structured-data-from-documents-with-amazon-textract/)
  - 엘라스틱서치의 다른 사례와 접목하여 이 문서의 키워드 검색 방법에 대한 활용 확대(예, 해당 문서에서 가장 많이 사용된 용어 10개 등)

## 결론
시장에는 이미 많은 문서관리 솔루션들이 존재하며, 이 솔루션들은 여기서 보여준 오피스 문서의 키워드 검색 기능을 제공하고 있다. 하지만 이를 엘라스틱서치를 통해 직접 구현해보았고, S3에 데이터를 집중함으로써 방대한 데이터 속에서 유의미한 정보를 쉽게 찾을 수 있는 한 가지 방법이 되길 바란다. 끝으로 본 문서는 테스트용으로 만든 것이므로 상용환경에서는 많은 부분이 부족할 수 있다. 감사합니다.

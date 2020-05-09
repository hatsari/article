# AWS API Gateway - HTTP API Practical Guide
- Date: 2020.10.23
- Yongki Kim(kyongki@)
- ChangeLogs
  - 2020.10.23: initial version

----
![aws_api_gateway_architecture](https://d1.awsstatic.com/serverless/New-API-GW-Diagram.c9fc9835d2a9aa00ef90d0ddc4c6402a2536de0d.png)
공식문서: https://docs.aws.amazon.com/apigateway/latest/developerguide/http-api.html
## AWS AWS Gateway - HTTP API
2020년 3월 12일 AWS API Gateway의 기능중 HTTP API 가 출시되었습니다. HTTP API는 낮은 지연시간(low latency)로 높은 성능으로 API Gateway를 구축할 수 있는데 특히 프록시 기능을 통해 유입되는 HTTP 요청을 다른 경로로 변경하거나, Lambda와 연동하여 serverless 환경을 구축하는데 매우 유용합니다. 또한 HTTP API는 기존 REST API에 비해 70% 정도 저렴한 가격으로 AWS API Gateway를 사용할 수 있게 합니다. 하지만 Rest API가 제공하는 모든 기능을 제공하지는 않습니다. 가령 캐싱이나 WAF와의 연동 같은 기능이 지원되지 않으며 좀 더 자세한 사항은 다음 비교 [링크](https://docs.aws.amazon.com/apigateway/latest/developerguide/http-api-vs-rest.html)를 참고하시기 바랍니다.
HTTP API를 사용하기 위해 당연히 [공식문서](https://docs.aws.amazon.com/apigateway/latest/developerguide/http-api.html)를 참고하는 것이 좋치만, 이를 보고 적용하다가 실제 구현하는데 어려움이 몇 가지 있었기에 이를 공유하고 문서를 작성하게 되었습니다.
## 기본 HTTP API 생성
## 특정 URL로 전달(HTTP Integration)
## 하위 URL 포함하여 전달(Magic Variable)
- proxy+
## 라우팅 경로 가공
## Default 경로 생성($default route)
## VPC 내부의 사설 URL로 전달(VPCLink)
## API의 경로별 Throttling 제한
## CloudWatch Metric으로 모니터링
## Limit
- 30초
- 전달 포트 제한(80,443,1024 이상만 허용)
- VPC 내부에서 HTTP API로 연결(PrivateLink)
- REST API는 NLB만 지원
## references
- GA: https://aws.amazon.com/blogs/compute/building-better-apis-http-apis-now-generally-available/
- Official Docs: https://docs.aws.amazon.com/apigateway/latest/developerguide/http-api.html
- Rest api vs Http api: https://docs.aws.amazon.com/apigateway/latest/developerguide/http-api-vs-rest.html

## markdown example
![ddb_query_insight_architecture](images/architecture.png)

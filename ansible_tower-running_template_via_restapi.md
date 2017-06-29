# Ansible Tower - RestAPI를 통해 Playbook 실행하는 방법

## Objective
Ansible Tower의 Rest API를 통해 Job Template을 실행하는 방법 도출
- curl 명령과 host_key 인증을 통해서 외부의 서버에서 Job Template 실행 테스트
- tower-cli를 통해 외부 변수 전달 및 외부 호스트에서 job template 실행 테스트 
- rest api로 외부 시스템과 연동하기 쉬운 도구 선택 및 방법 제공

## Brief Conclusion
- Ansible Tower에 Rest API를 연동해서 사용하는 방법으로는 tower-cli를 사용할 것을 추천한다.
- 물론 API를 다른 프로그래밍언어와 연동해서 직접 사용하는 것도 가능하다. 하지만 이 부분은 테스트해보지 않았기 때문에 결론을 낼 수 없으며, 명령어 기반으로 연동하는 방법으로는 tower-cli를 권고한다. 그 이유는 tower-cli에서 이미 옵션을 통해 tower의 기능을 대부분 포함하고 있기 때문에 별도의 개발없이도 사용할 수 있도록 만들어놨기 때문이다.

## Test Environment
- ansible tower: 3.1.2
- ansible: 2.3.1
- Control Node
 - ansible-tower: 192.168.56.102
- Managed Nodes
 - rhel71: 192.168.56.101
 - rhel72: 192.168.56.110
 
## snippet of sample playbook
```
---
- name: simple api test playbook
  hosts: rhel71
  vars:
    - var1: "yongki"
    - var2: "alex"
  tasks:
    - name: touch meaningless file
      shell:
        "touch /tmp/foo; echo '$(date), {{ var1 }} {{ var2 }}' >> /tmp/foo"
    - name: print msg
      debug:
        msg: " variable is {{ var1 }} {{ var2 }} "
```

## Job template configuration
host_key를 사용해서 job template를 실행할 때는, api 호출을 시도하는 호스트가 플레이북의 "hosts: " 항목에 들어가 있어야한다.
그렇치 않을 경우에는 자신이 인증하지 않은 서버로 판단하여 해당 명령이 실행되지 않는다.
즉, 플레이북에서 "hosts: rhel71" 로 정의되었다면, 아래 call_simple_command.sh 명령은 rhel72에서만 정상적으로 작동한다.
당연한 얘기지만, 이 작업 전에는 rhel71 호스트가 먼저 inventory에 등록되어야 한다.

## test to run template using curl
이테스트를 위한 참고 문서는 아래와 같다.
- http://docs.ansible.com/ansible-tower/3.1.3/html/administration/tipsandtricks.html#launch-jobs-curl
- cat /usr/share/awx/request_tower_configuration.sh (on tower system)

### extra_var 아규먼트없이 실행 
먼저 Jobtemplate 설정 화면에서 만든 host_key를 기반으로 curl 스크립트를 작성한다.

1. REST API를 호출할 스크립트 생성
아래 스크립트는  rhel71 호스트에 생성

cat /root/call_simple_command.sh
``` sh
#!/bin/sh
curl -vvv -k --data "host_config_key=ac3ed6b919cc13b34fbf0b743d3a7efb" \
https://192.168.56.102:443/api/v1/job_templates/7/callback/
```

2. 스크립트로 템플릿 실행
해당 명령은 플레이북에 정의된 rhel71 에서 실행한다.

```
[root@rhel71 ~]# sh provison_callback.sh
* About to connect() to 192.168.56.102 port 443 (#0)
*   Trying 192.168.56.102...
* Connected to 192.168.56.102 (192.168.56.102) port 443 (#0)
* Initializing NSS with certpath: sql:/etc/pki/nssdb
* skipping SSL peer certificate verification
* SSL connection using TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384
* Server certificate:
*       subject: CN=www.ansible.com,O=Ansible,L=Raleigh,ST=NC,C=US
*       start date: Apr 05 17:08:40 2017 GMT
*       expire date: Jan 18 17:08:40 2291 GMT
*       common name: www.ansible.com
*       issuer: CN=www.ansible.com,O=Ansible,L=Raleigh,ST=NC,C=US
> POST /api/v1/job_templates/7/callback/ HTTP/1.1
> User-Agent: curl/7.29.0
> Host: 192.168.56.102
> Accept: */*
> Content-Length: 48
> Content-Type: application/x-www-form-urlencoded
>
* upload completely sent off: 48 out of 48 bytes
< HTTP/1.1 201 CREATED
< Server: nginx/1.10.2
< Date: Thu, 29 Jun 2017 02:02:26 GMT
< Transfer-Encoding: chunked
< Connection: keep-alive
< X-API-Time: 0.379s
< Allow: GET, POST, HEAD, OPTIONS
< Content-Language: en
< Vary: Accept, Accept-Language, Cookie
< Location: https://192.168.56.102/api/v1/jobs/68/
< X-API-Node: localhost
< Strict-Transport-Security: max-age=15768000
< X-Frame-Options: DENY
<
* Connection #0 to host 192.168.56.102 left intact
```
3. 실행 결과
- 원래 변수인 var1: yongki, var2: alex 가 정상적으로 출력된다.

![no_ext_var](https://github.com/hatsari/article/blob/master/no_vars_curl.png?raw=true)

### extra_var 아규먼트를 추가하여 실행
1. REST API를 호출할 스크립트 생성
아래 스크립트는  rhel71 호스트에 생성

cat /root/call_simple_command_with_extra_vars.sh
``` sh
#!/bin/sh
curl -k -f -H 'Content-Type: application/json' -XPOST  \
-d '{"host_config_key": "ac3ed6b919cc13b34fbf0b743d3a7efb", "extra_vars": "{\"var1\": \"hello\"}"}' \ 
https://192.168.56.102:443/api/v1/job_templates/7/callback/
```

2. 스크립트로 템플릿 실행
해당 명령은 플레이북에 정의된 rhel71 에서 실행한다.

```
[root@rhel71 ~]# sh call_simple_command_with_extra_vars.sh
* About to connect() to 192.168.56.102 port 443 (#0)
*   Trying 192.168.56.102...
* Connected to 192.168.56.102 (192.168.56.102) port 443 (#0)
* Initializing NSS with certpath: sql:/etc/pki/nssdb
* skipping SSL peer certificate verification
* SSL connection using TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384
* Server certificate:
*       subject: CN=www.ansible.com,O=Ansible,L=Raleigh,ST=NC,C=US
*       start date: Apr 05 17:08:40 2017 GMT
*       expire date: Jan 18 17:08:40 2291 GMT
*       common name: www.ansible.com
*       issuer: CN=www.ansible.com,O=Ansible,L=Raleigh,ST=NC,C=US
> POST /api/v1/job_templates/7/callback/ HTTP/1.1
> User-Agent: curl/7.29.0
> Host: 192.168.56.102
> Accept: */*
> Content-Type: application/json
> Content-Length: 95
>
* upload completely sent off: 95 out of 95 bytes
< HTTP/1.1 201 CREATED
< Server: nginx/1.10.2
< Date: Thu, 29 Jun 2017 02:18:00 GMT
< Transfer-Encoding: chunked
< Connection: keep-alive
< X-API-Time: 0.190s
< Allow: GET, POST, HEAD, OPTIONS
< Content-Language: en
< Vary: Accept, Accept-Language, Cookie
< Location: https://192.168.56.102/api/v1/jobs/70/
< X-API-Node: localhost
< Strict-Transport-Security: max-age=15768000
< X-Frame-Options: DENY
<
* Connection #0 to host 192.168.56.102 left intact
```
3. 실행 결과
- extra_vars 로 설정한 var1: hello 로 출력되지 않고, 원래 변수인 var1: yongki 출력되었다.

![no_ext_var](https://github.com/hatsari/article/blob/master/no_vars_curl.png?raw=true)

4. 디버깅
이슈 해결을 위해 권고하는대로 Ansible Tower GUI의 Job Template에서 "Prompt on launch" 를  활성화시켰다.
하지만 아래와 같은 메시지가 발생하며 에러가 발생하였다.

```
curl: (22) The requested URL returned error: 405 METHOD NOT ALLOWED
```

그래서 다음 방법인 tower-cli 로 방법을 전환하였다.(with sobbing)

## test to run template using tower-cli
tower-cli 참고 문서는 아래와 같다
- https://github.com/ansible/tower-cli

### tower-cli 설치
```
pip install ansible-tower-cli
```

### tower-cli 환경 파일

```
[root@rhel72 ~]# cat /etc/tower/tower_cli.cfg
host: 192.168.56.102
username: admin
password: MNQz7jJqQvzj
```

### tower-cli 틑 롱해 Job Template 실행 
1. REST API를 호출할 명령어 실행

extra-vars로 var1=hello, var2=world로 설정하고 이 변수가 결과로 반영되는지 확인하기위해 명령을 실행하겠다.
이 때, extra-vars를 변수로 전달하기 위해서는 Job Template 설정 화면에서 "Prompt on launch"가 활성화되어 있어야 한다.

```
[root@rhel72 ~]# tower-cli job launch --job-template=7 --extra-vars="var1=hello var2=world"
```

2. 실행 결과
위 명령은 rhel72에서 실행하였으며, 결과는 아래 화면과 같다.

![exec_tower-cli](https://github.com/hatsari/article/blob/master/exec_tower-cli.png?raw=true)

3. 결과 확인 

![result-ext-var-tower-cli](https://github.com/hatsari/article/blob/master/extra_vars_tower-cli.png?raw=true)

extra vars로 선언한 var1=hello, var2=world 모두 정상적으로 출력되는 것을 확인할 수 있다.
특히, tower-cli를 사용할 경우에는 inventory에 등록되지 않은 서버에서도 정상적으로 extra_vars를 전달할 수 있었다.

![tower-cli-on-external-host](https://github.com/hatsari/article/blob/master/tower-cli_external_host.png?raw=true)

### tower-cli를 통해 job 모니터링
rest api를 통해 명령을 실행하면 해당 명령의 실행결과를 연동 시스템에서 모니터링하고 실행결과를 알 수 있어야 한다.
이 때는 tower-cli job monitor 명령을 통해 알아낼 수 있다.

![tower cli job monitor](https://github.com/hatsari/article/blob/master/job_monitor_tower-cli.png?raw=true)

또는 tower가 제공하는 notification 기능 중 webhook 을 활용하여 작업이 끝나면 자동으로 결과를 전달하도록 할 수도 있을 것이다.
또는 playbook에서 uri 모듈을 이용하여 결과를 전달할 수 있다.

예제 YAML 코드
```
---
- block:
  - name: curl post to Heat
     uri:
       url: "{{ heat_endpoint }}"
       method: POST
       HEADER_X-Auth-Token: "{{ heat_token }}"
       HEADER_Content-Type: "application/json"
       HEADER_Accept: "application/json"
       body: '{"status": "SUCCESS"}'
       force_basic_auth: yes
       status_code: 200
       body_format: json
  rescue:
  - name: curl post to Heat to notify of failure
     uri:
       url: "{{ heat_endpoint }}"
       method: POST
       HEADER_X-Auth-Token: "{{ heat_token }}"
       HEADER_Content-Type: "application/json"
       HEADER_Accept: "application/json"
       body: '{"status": "FAILURE"}'
       force_basic_auth: yes
       status_code: 200
       body_format: json
```
참고사이트: [Open Stack Heat and Ansible Tower Orchestration](https://keithtenzer.com/2016/05/09/openstack-heat-and-ansible-automation-born-in-the-cloud/)

## Summary
Ansible Tower는 Web Portal 자체만으로도 매우 유용하지만, Rest API를 통해 다른 시스템과 연계되었을 때 더 큰 효용성을 발휘할 수 있다. 하지만 문서를 찾아보고 따라했을 때, 정상적으로 작동하지 않는 경우가 있어서 이를 정리하고자 이 글을 작성하게 되었다.
명령형 기반으로 ansible-tower를 연동하는 방법은 클라우드에서 새로운 인스턴스를 생성하고 그 인스턴스에 특정 작업을 수행시키고자 할 때 또는 외부 시스템에서 tower의 작업상태를 실행하고 모니터링할 때 많이 사용된다. 하지만 기존에 주로 사용했던 curl을 통한 API 호출이 어느 순간부터 정상적으로 작동하지 않게 되는 경험을 하게 되면서, tower-cli를 검토하게 되었다. tower-cli는 tower가 제공하는 거의 모든 기능을 명령형으로 수행할 수 있게끔 만들어주고 있어서 기존의 curl로 사용했던 작업을 훨씬 단순하고 쉽게 변화시켜 주었다.


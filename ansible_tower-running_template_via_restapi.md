# Ansible Tower - RestAPI를 통해 Playbook 실행하는 방법
## Objective
Ansible Tower의 Rest API를 통해 Job Template을 실행하는 방법 도출
- host_key 인증을 통해서 외부의 서버에서 Job Template 실행 
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
  hosts: rhel72
#  hosts: localhost
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

## Jobtemplate configuration
## test to run template using curl
ref: cat /usr/share/awx/request_tower_configuration.sh
### extra_var 아규먼트없이 실행 
먼저 Jobtemplate 설정 화면에서 만든 host_key를 기반으로 curl 스크립트를 작성한다.
cat call_simple_command.sh
``` sh
#!/bin/sh
curl -vvv -k --data "host_config_key=ac3ed6b919cc13b34fbf0b743d3a7efb" \
https://192.168.56.102:443/api/v1/job_templates/7/callback/
```


## test to run template using tower-cli


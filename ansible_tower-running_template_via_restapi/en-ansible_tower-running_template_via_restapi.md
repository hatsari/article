# Ansible Tower - How to Run Job Template via Rest API

## Objective
To Find a best way of running job template via ansible tower's rest api
- job template execution test with curl and host_key authentication
- job template execution test with tower-cli
- how to pass the extra_vars when using rest api
- In order to integrate with other solution, like ITSM, the host which runs api-call should not necessary to register in inventory.  

## Brief Conclusion
- I suggest ansible-tower-cli as a command-line tool, not curl.
- Of course, it is possible to use an api in programing language, like java or python. But if you have to run tower operation in command-line, it is better to make use of tower-cli. tower-cli already has almost all functions which provided by ansible-tower. So you don't need to any thing by yourself.

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
When you execute a job template with host_key, the host which calling api should be in "hosts:" statement. 
If not, that call doesn't be operated because tower thinks request host is not valid to run the template.
For instance, "hosts: rhel71" is defined in playbook, below call_simple_command.sh will run well on only rhrl71.
Also, before calling the job, rhel71 host should be in inventory though. 

![job_template_example](job_template_example.png)

## Test to execute job template using curl
reference document is below:
- http://docs.ansible.com/ansible-tower/3.1.3/html/administration/tipsandtricks.html#launch-jobs-curl
- cat /usr/share/awx/request_tower_configuration.sh (on tower system)

### Executing without extra_var argument
At first, create curl script based on host_key which get from Job template configuration GUI.

1. Creating script calling REST API

This scrip is located in rhel71 host.

cat /root/call_simple_command.sh
``` sh
#!/bin/sh
curl -vvv -k --data "host_config_key=ac3ed6b919cc13b34fbf0b743d3a7efb" \
https://192.168.56.102:443/api/v1/job_templates/7/callback/
```

2. Executing the script to call a job template

Absolutely, run the script on rhel71.

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
3. Execution result
- The result shows the original value, var1: yongki, var2: alex

![no_ext_var](no_vars_curl.png)

### Executing with extra_var argument
1. Creating script calling REST API

This scrip is located in rhel71 host as well.

cat /root/call_simple_command_with_extra_vars.sh
``` sh
#!/bin/sh
curl -k -f -H 'Content-Type: application/json' -XPOST  \
-d '{"host_config_key": "ac3ed6b919cc13b34fbf0b743d3a7efb", "extra_vars": "{\"var1\": \"hello\"}"}' \ 
https://192.168.56.102:443/api/v1/job_templates/7/callback/
```

* Notice that "var1" variable has "hello" value.

2. Executing the script to call a job template


Absolutely, run the script on rhel71 also.

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
3. Result of execution
- I intended to replace the value of "var1" from "yongki" to "hello", but the result shows just original value.
It didn't work properly.

![no_ext_var](no_vars_curl.png)

4. dubugging
To solve the issue, I activated "**Prompt on launch**" in Job Template Configuration GUI.
but it caused another error printing out below message.

```
curl: (22) The requested URL returned error: 405 METHOD NOT ALLOWED
```

It always has worked in ansible-tower 2.x to call the job using curl. But something is changed and It didn't work.
after several times test, I turned to tower-cli with sobbing.

## Test to run template using tower-cli

Reference document about tower-cli is below: 
- https://github.com/ansible/tower-cli

### Installaing tower-cli

```
pip install ansible-tower-cli
```

### tower-cli configuration file

tower_cli.cfg can be in /etc/tower or ~/.tower_cli.cfg

```
[root@rhel72 ~]# cat /etc/tower/tower_cli.cfg
host: 192.168.56.102
username: admin
password: MNQz7jJqQvzj
```

### Executing job template using tower-cli 
1. Executing the script to call a job template

I defined follwing extra_vars as argumenst and execute this command on rhel72.
- var1 = *hello*
- var2 = *world*

To pass the extra-vars to job template, it needs to activate "Prompt on launch"

```
[root@rhel72 ~]# tower-cli job launch --job-template=7 --extra-vars="var1=hello var2=world"
```

2. Result of execution


Result is below:

![exec_tower-cli](exec_tower_cli.png)

3. Verification

![result-ext-var-tower-cli](extra_vars_tower_cli.png)

You can see "**hello world**", it means values of extra_vars are changed correctly.
Especially, even the host which not registered in inventory can execute a job template using tower-cli.
Already I mentioned that curl command with host_key doesn't work at all on the host which not in inventory and "**hosts:**".

![tower-cli-on-external-host](tower_cli_external_host.png)

### job monitoring with tower-cli
It's needed to monitor the job status from integrated host when job running.
And this simple command shows the job log stream and the result of job.

![tower cli job monitor](job_monitor_tower_cli.png)

or you can choose the webhook of tower's notificaion feature so you can receive the result when it is finished or failed.
another option is to use *uri* module of playbook. Here is a simple playbook code.

Example YAML Snippet
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
reference: [Open Stack Heat and Ansible Tower Orchestration](https://keithtenzer.com/2016/05/09/openstack-heat-and-ansible-automation-born-in-the-cloud/)

## Summary
Ansible Tower is very useful as web portal as itself, but it can power up the ability of tower when integrating with other solution. Thesedays, everytihng is connected and integrated, and RestAPI is common method to combind all. But when I tried to look for how to use RestAPI, the guide from tower document didn't work for me. so I made a test and this document to share what I find out.
curl has been good tool in tower 2.x but better tool appears, tower-cli. tower-cli has most of features which provided with ansible tower. so most of tasks can be done in command-line. It makes me simpler and easier when I need to use ansible tower.

and thanks for reading this article. 


# ansible 작업 결과를 HTML 표로 출력하는 방법

ansible로 시스템 변경 작업을 많이 수행하지만, 시스템 정보를 모으기 위해 사용할 수도 있다. 이 때, HTML 포맷으로 출력하면 훨씬 보기가 좋기 때문에 Template을 사용하여 HTML 표로 수집한 값을 표현하는 방법을 설명하고자 한다.

구현 방법 요약
  - 출력하고자 하는 값을 변수로 저장
  - HTML 파일로 사용할 jinja2 파일 작성
  - template 모듈을 활용해서 html 파일 생성

## 인벤토리 파일
파일이름: inven.txt
```
[vagrant@ansible-tower playbook]$ cat inven.txt

[vms]
v2 ansible_ssh_host=172.28.128.4
v3 ansible_ssh_host=172.28.128.5
```

## 시스템 정보 수집 플레이북
아래는 시스템 정보를 수집하고 이를 html 파일로 표현하는 플레이북 예제이다.
수집할 정보는 "HOSTNAME", "CPU", "MEMORY", "DISK_PARTITION" 이며, "vms"로 정의된 그룹은 'v2', 'v3' 라는 이름의 두 대의 호스트로 구성되어 있다.
그럼 아래 예제를 보며, 각 task를 설명하도록 하겠다.

플레이북 파일이름: gather_info.yml
```
---
- name: gather system information
  hosts: vms
  vars:
    - title: "Automated Gathered System Information"
    - cols:
      - "HOSTNAME"
      - "CPU"
      - "MEMORY"
      - "DISK_PARTITION"

  tasks:
    - name: print hostname
      debug:
        var: ansible_hostname
    - name: gather df info
      shell: df | grep sda
      register: info_df
    - name: set info_df
      set_fact:
        info_df: "{{ info_df.stdout_lines }}"
    - name: create html report
      template:
        src: report.html.j2
        dest: /home/vagrant/playbook/result.html
      delegate_to: 127.0.0.1
      run_once: yes
```

1. "print hostname" 작업
  ansible_hostname 이라는 fact 변수가 정상적으로 작동하는지 확인

2. "gather df info" 작업
  shell 모듈을 통해 v2, v3 호스트의 디스크 정보를 수집하고 이를 register를 이용하여 info_df 라는 변수로 저장한다. 이 작업은 shell 모듈이 아닌 다른 어떤 모듈을 사용해도 가능하며 register를 통해 변수를 저장한다는 것이 중요하다.

3. "set info_df" 작업
  향후 다른 호스트에서도 info_df 변수를 사용할 수 있도록 set_fact 모듈을 사용한다. 

4. "create html report"
  템플릿 모듈을 활용하여 html 파일을 생성한다. 템플릿 파일은 report.html.j2 이며 이 템플릿을 이용해서 result.html 이라는 결과 html 파일이 만들어진다.  이때 delegate_to 지시어를 사용해서 해당 작업이 localhost에서 실행되게하고, run_once 지시어를 사용하여 한 번만 작동케한다.
이 작업은 html 리포트 파일을 만드는 것이니 두 번 작동할 필요가 없다.

## 템플릿 파일    
ansible의 템플릿은 jinja2 형식을 가지며, 동적으로 파일을 생성할 때 매우 유용하다. 여기서도 html 파일을 만들기 위해서 템플릿을 활용하였다. 그럼 템플릿 파일의 내용을 보도록 하겠다.

템플릿 파일이름: report.html.j2

```
<html>

<h1> Title: {{ title }} </h1>

<table border=1>
<TR>
{% for col in cols %}
   <TD class="c1"><SPAN> {{ col }} </SPAN></TD>
{% endfor %}
</TR>

{% for host in ansible_play_hosts %}
<TR>
   <TD class="c1"><SPAN> {{ hostvars[host]["ansible_hostname"] }} </SPAN></TD>
   <TD class="c2"><SPAN> {{ hostvars[host]["ansible_processor_cores"] }} </SPAN></TD>
   <TD class="c3"><SPAN> {{ hostvars[host]["ansible_memtotal_mb"] }} </SPAN></TD>
   <TD class="c4"><SPAN> {{ hostvars[host]["info_df"] }} </SPAN></TD>
</TR>
{% endfor %}

</table>

</html>
```

1. 제목 설정
  {{ title }} 변수를 활용해서 제목을 지정한다. 이 변수는 gather_info.yml 플레이북에서 지정하였다.

2. 테이블 헤더 표시
  cols 변수를 loop해서 상단의 컬럼명 부분을 표시하였다. 

3. 각 서버별 정보 표시
  ansible_play_hosts 변수는 ansible에서 제공하는 매직변수이며, 플레이에서 실행되는 모든 호스트이름을 포함하고 있다. 이 변수를 looping하여 서버별 호스트이름, CPU, Memory 그리고 shell로 설정한 변수값을 표 형식으로 출력할 수 있다.

## 플레이북 실행
플레이북 실행 명령은 다음과 같다.

```
#ansible-playbook -i inven.txt gather_info.yml
```

실행 결과 하면은 다음과 같다.

![cmd_result](cmd_result.jpg)

## 생성된 HTML 파일 확인
위 실행의 결과로 생성된 html 파일은 내용은 다음과 같다

파일이름: result.html

```
<html>
Title: Automated Gathered System Information
<table>
<TR>
   <TD class="c1"><SPAN> HOSTNAME </SPAN></TD>
   <TD class="c1"><SPAN> CPU </SPAN></TD>
   <TD class="c1"><SPAN> MEMORY </SPAN></TD>
   <TD class="c1"><SPAN> DISK_PARTITION </SPAN></TD>
</TR>


<TR>
   <TD class="c1"><SPAN> v2 </SPAN></TD>
   <TD class="c2"><SPAN> 1 </SPAN></TD>
   <TD class="c3"><SPAN> 992 </SPAN></TD>
   <TD class="c4"><SPAN> [u'/dev/sda1       41152736 1230456  37808796   4% /'] </SPAN></TD>
</TR>

<TR>
   <TD class="c1"><SPAN> v3 </SPAN></TD>
   <TD class="c2"><SPAN> 1 </SPAN></TD>
   <TD class="c3"><SPAN> 993 </SPAN></TD>
   <TD class="c4"><SPAN> [u'/dev/sda1       41152736    895464  38143788   3% /'] </SPAN></TD>
</TR>

</table>

</html>
```

### HTML 출력
![html_result](html_result.jpg)


## 맺음말
이와 같이 ansible의 템플릿을 활용해서 동적으로 HTML 파일을 만들게 되면 훨씬 가독성이 좋은 화면을 볼 수 있고, 이를 mail을 통해 전달하면 결과 내용을 좀 더 간편하게 확인할 수 있다.
그리고 html 표의 디자인을 아름답게 만드실 수 있는 분은 공유를 부탁드립니다. 

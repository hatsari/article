# Practical Guide to Create Instances on Openstack
Date: 2018. 07. 09

오픈스택에서 인스턴스를 생성하는 플레이북을 작성할 때 이를 검증하는 작업을 설명합니다. 기본 생성은 **ansible-doc os_server** 방법을 참고하면 되지만, 실제 작성할 때는 인스턴스 상태를 확인하는 과정이 필요하며 여기에서는 다음과 같은 기능을 구현하였습니다.
  - 인스턴스를 동시에 생성하기
  - 인스턴스 생성 완료 검증
  - 인스턴스에서 ssh 연결 가능 여부 검증

위 기능에 대한 구현 코드는 아래에 자세히 설명토록 하겠습니다.

## Spawning Instances Simultaneously
ansible은 기본적으로 instance를 생성할 때 하나씩 생성하게 합니다. loop를 돌리더라도 결국 하나씩 차례로 생성됩니다. 이에 대해 시간을 절약하기 위해서는 동시에 인스턴스를 생성하는 방법을 사용해야하며 플레이북에서는 **async** 방식을 활용할 수 있습니다. 아래 코드에서 **async: 120**와 **poll: 0** 설정이 동시에 인스턴스를 생성할 수 있는 부분입니다. 120초 동안 async를 진행하고 진행여부에 대해서는 확인하지 않도록 **poll** 부분은 0 으로 설정하였습니다. 

```yaml
# tasks file for openstack-instance
- name: Create a server instance
  os_server:
    auth: "{{ os_auth }}"
    name: "{{ instance_name }}{{ item }}"
    image: wwd_rhel
    meta: "group={{ group }},deployment_name={{ deployment }}"
    flavor: m2.small_generated_by_ansible
    security_groups: "{{ security_group_name }}"
    auto_ip: "{{ floating_answer }}"
    key_name: ansible_ssh
    wait: yes
    nics:
    - net-name: "{{ vm_nic }}"
  register: newnodes
  async: 120
  poll: 0
  with_sequence: start=1 end="{{ count }}"
```
단, 이 설정에서는 인스턴스의 생성이 정상적으로 되었는지 확인하지 않기 때문에, 인스턴스 생성을 확인하는 코드를 별도로 넣어줘야 합니다. 이를 확인하는 코드는 다음 장에서 보여드립니다. 

## Verifing Creation of Instances
아래 코드는 인스턴스 생성을 위해 **role**을 사용하였습니다. 그리고 해당 role을 목적에 따라 다른 형태를 가지도록 하기 위해 **with_items** 지시어를 사용하여, **web**, **was**, **db**를 변수로 받도록 하였습니다. 이 코드에서 인스턴스의 생성을 확인하는 부분은 두 번째 task인 **async_status** 구문입니다. 위 인스턴스 생성코드에서 **register**로 작업 상태를 **newnodes** 라는 변수로 저장하였으며, 아래코드에서 newnodes의 **ansible_job_id**를 기반으로 작업이 끝났는지 아닌지를 판별하게 됩니다. 이와 같이 작업의 완료 여부를 검증하지 않으면 차 후에 진행하게 될 **ssh** 연결상태 확인을 위한 **public_v4** 의 ip addr 정보를 확인할 수 없게 됩니다. 또한 해당 인스턴스에 애플리케이션을 설치한다거나 환경설정을 변경코자할 때, 인스턴스 생성이 완료되지도 않은 상태에서 변경을 이루려고 하기 때문에 에러가 발생하게 됩니다. 그러므로 인스턴스를 동시에 여러 개 생성코자 한다면 아래와 같은 확인 절차가 꼭 필요합니다.
```yaml
  tasks:
  - name: Create {{ item }} Instances
    include_role:
       name: openstack-instance
       vars_from: "{{ item }}.yaml"
    with_items:
      - web
      - was
      - db

  - name: Waiting for role includes to complete
    async_status:
      jid={{ newnodes['results'][0]['ansible_job_id'] }}
    register: my_async_job_status
    until: my_async_job_status.finished
    retries: 20

  - name: gather instance facts
    os_server_facts:
      auth: "{{ os_auth }}"
      server: db*
    register: result
```
참고로 위에서는 맨 마지막 인스턴스에 대해서만 확인 작업을 하였습니다. 모든 인스턴스를 대상으로 확인하는 것이 가장 좋으나 마지막이 되면 다 된다는 가당찮은 믿음으로 그냥 작성하였습니다.  위 코드에서 두 번째 확인까지 작업이 완료되면, 마지막으로 **os_server_facts** 작업을 통해 마지막 db 서버의 IP 정보를 변수로 저장시킵니다. 이 작업을 거쳐야만 SSH 접속을 테스트 할 수 있는 IP 정보를 가져올 수 있습니다. 
## Checking Enablement of SSH port
마지막은 **wait_for** 작업을 통해 원격으로 접속테스트를 합니다. 인스턴스가 생성된다하더라도 OS가 부팅하는데는 시간이 걸리기 때문에 SSH 연결을 확인하는 작업을 추가하게 되었습니다. 이 작업이 없으면 위에 설명한 바와 마찬가지로 인스턴스에 접속할 수 없으므로, 다음에 이어질 시스템 변경 작업에서 에러가 발생하게 됩니다.
```yaml
  - name: Wait for Last Instance to be available
    wait_for:
      host: "{{ openstack_servers[0]['accessIPv4'] }}"
      port: 22
      search_regex: OpenSSH
      timeout: 300
    delegate_to: "{{ inventory_hostname }}"

```
위 코드에서 **inventory_hostname** 은 **localhost**를 의미합니다. 그리고 300초 동안 22번 포트 접근을 시도하여 **OpenSSH**문자열을 받아올 수 있는지를 검사하는 방식을 사용하였습니다. 이 코드는 **ansible_doc wait_for**에서 확인하실 수 있습니다.
## Conclusion
오픈스택 또는 AWS, AZURE, GCP 등 다양한 클라우드나 가상화 환경에서 인스턴스를 생성하는 작업에 ansible을 많이 사용하고 있는데 단순히 생성만 하는 코드가 아닌, 실제 도움이 되는 코드를 작성하고자 이 글을 작성하게 되었습니다. 도움이 되었기를 바라며 다음에도 다른 유익한 정보를 가지고 돌아오겠습니다. 그럼 즐거운 IAC 되시기 바랍니다.

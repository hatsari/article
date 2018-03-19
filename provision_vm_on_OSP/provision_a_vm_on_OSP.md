# Provision an Instance on OpenStack
- Date: 2018. 03. 19
- Writer: Alex, YONGKI KIM

ansible을 사용하면 오픈스택 위에 쉽게 인스턴스를 생성하고, 관리할 수 있다. 오픈스택에 관련된 모듈은 'os_' 로 시작되며, 아래 페이지에서 확인할 수 있다.
*os_server* 모듈을 활용하면 인스턴스 생성 및 삭제를 손쉽게 할 수 있으며, *os_volume* 모듈을 활용하면 cinder 서비스를 통해 스토리지 볼륨도 쉽게 할당받을 수 있다.
- [openstack related modules](http://docs.ansible.com/ansible/latest/list_of_cloud_modules.html#openstack)

또한 생성된 인스턴스에 접근하여 패키지 설치 및 설정 변경도 자동으로 수행시킬 수 있기 때문에 운영 환경에 맞는 SOE(standard operating environment)구현도 자동화할 수 있다.


## Provisioning an Instance
인스턴스 생성은 *os_server* 모듈을 사용해서 기존에 정의되어 있는 glance 이미지로 만들어 진다. 이 때 필요한 정보는 아래와 같으며 security group, network 이름과 같은 기본 인프라 환경은 먼저 생성되어 있어야 한다.
인스턴스를 생성하는 샘플 코드는 아래와 같다.

``` yaml
  - name: Create a server instance
    os_server:
      cloud: "{{ cloud_name }}"
      name: "{{ item.name }}"
      state: "{{ dead_or_alive }}"
      image: "{{ image_name }}"
      meta: "group={{ item.group }},deployment_name={{ deployment }}"
      flavor: "{{ flavor_name }}"
      security_groups: "{{ sec_group }}"
      key_name: "{{ key_name }}"
      nics:
      - net-name: "{{ net_int }}"
      userdata: |
        #!/bin/bash
        curl -o /tmp/openstack.pub http://www.opentlc.com/download/ansible_bootcamp/openstack_keys/openstack.pub
        cat /tmp/openstack.pub >> /home/cloud-user/.ssh/authorized_keys
        curl -o /tmp/internal.repo http://www.opentlc.com/download/ansible_bootcamp/repo/internal.repo
        cp /tmp/internal.repo /etc/yum.repos.d/internal.repo
    with_items: "{{ the3tier_info }}"
```

### Explaing Arguments
위 코드에서 사용한 각 아규먼트에 대한 설명은 아래와 같다.
- *cloud:* 접속할 오픈스택 정보,  */etc/openstack/cloud.yml* 파일에 기록된 클라우드 접속 정보를 기반으로 오픈스택에 접속하게 된다.
- *name:* 인스턴스 이름, 위 예제에서는 *with_items* 를 통해 다수의 인스턴스를 생성하도록 loop를 사용하였다.
- *state:* 인스턴스를 생성할 때는 *present*, 삭제할 때는 *absent* 값을 주게 된다.
- *image:* 사용할 glance image 이름을 지정한다.
- *meta:* 오픈 스택의 메타 정보이며, AWS의 tag와 유사하게 사용될 수 있다.
- *flavor:* 사용할 flavor(하드웨어 스펙 정의)를 지정한다.
- *security_groups:* 방화벽 정책을 위한 security group을 지정한다.
- *key_name:* 인스턴스 접속을 위한 ssh 보안키를 지정한다.
- *nics:* 사용할 네트워크 정보를 지정한다.
- *userdata:* 인스턴스가 부팅할 이 후, 한 번만 실행될 스크립트를 지정한다. 여기서는 이 후 앤서블이 접속할 수 있도록 ssh 키와 패키지 설치를 위한 리포지토리 파일을 다운받도록 스크립트가 작성되었다.

## Intallation Custome Packages
### Inventory Registration
인스턴스가 생성된 이 후, 이 인스턴스에 변경 작업을 수행하기 위해서는 ansible이 해당 서버를 찾을 수 있도록 inventory에 등록해야하는데 이를 위한 방법은 두 가지가 있다. 하나는 in-memory inventory에 등록하는 것이며, 다른 하나는 dynamic inventory 스크립트를 사용하는 것이다.

#### In-memory Inventory
*add_host* 모듈을 사용하면 휘발성으로 특정 호스트를 인벤토리에 등록하여 플레이가 실행되는 동안에만 인벤토리에 등록시킬 수 있다.
in-memory inventory 방식을 사용한 예는 아래와 같다.

``` yaml
    - name: gather OSP instance info if instance is not included in inventory 
      block:
        - name: Fetch Instance Info
          os_server_facts:
            cloud: ospcloud
            region_name: RegionOne
          register: result
        - name: Add host to
          add_host:
            name: "{{ item.public_v4 }}"
            group: "{{ item.metadata.group }}"
          with_items: "{{result.ansible_facts.openstack_servers}}"
          changed_when: false
```
위 예제에서는 인스턴스를 생성할 때 지정한 metadata를 기준으로 그룹을 생성하였고, 이 그룹을 기준으로 호스트를 등록하였다.

#### Dynamic Inventory
동적 인벤토리는 스크립트를 실행하여, 해당 클라우드에서 실행되고 있는 인스턴스 정보를 가져오는 방식이다. 이 스크립트는 아래에서 다운 받을 수 있다.
[Dynamic Inventory](http://docs.ansible.com/ansible/latest/intro_dynamic_inventory.html)

##### built-in dynamic Inventory
- Open Stack 
- Amazon Web Service
- Google Cloud Engine
- Cobbler 등

그리고 사용 방법은 다음과 같다.
``` shell
ansible-playbook -i openstack.py install_packages_on_openstack_instances.yaml
```
### Package Installation
패키지를 설치하는 방법은 패키지 관리 프로그램(rpm-based or apt-based)에 따라 달라지며, ansible에서는 다양한 패키지 설치방식을 지원하고 있다. 레드햇 계열에서는 *yum* 모듈을 사용
해서 패키지를 설치하고 *service* 모듈을 사용해서 해당 서비스를 시작/중지할 수 있다.

#### Install Package and Start Service - sample code
``` yaml
- name: install docker
  yum:
    name: docker
    state: latest
- name: start and enable docker at boot
  service:
    name: docker
    state: started
    enabled: yes
```

## Conclusion
이상으로 오픈스택에서 인스턴스를 생성하고 해당 인스턴스에 패키지를 설치하고 서비스를 시작하는 방법에 대해 알아보았다.
ansible은 오픈스택 관련 모듈을 제공하기 때문에 인스턴스 생성 뿐 아니라 네트워크 설정 및 볼륨 생성까지도 쉽게 관리할 수 있음을 알게되었으며, 해당 인스턴스에서는 리눅스 OS를 관리하는 범용 모듈을 사용하여 다양한 설정 관리를 자동화할 수 있음을 볼 수 있었다. 


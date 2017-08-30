# AUTOMATING NETWORK DEVICES WITH ANSIBLE

원문: http://www.sipgateblog.de/automating-network-devices-with-ansible/

-----
예전에 우리는 독일 고객에게 우리의 네트워크 인프라스트럭처의 일부를 교체하기 위해 노력중이라고 말했었다. 그리고 이를 위해 최신 기술 변화를 발맞추기 위해 앤서블과 쥬니퍼(Juniper)를 활용해서 완전히 자동화된 네트워크 설정을 이룰 것을 결정했다. 이런 컨셉에 맞게 자료를 찾아보다보니 관련된 온라인 기술자료가 너무나 부족하다는 것을 알게 되었고, 유사한 환경을 구축하려는 사람들에게 도움을 주기위해 이 글을 쓰게 되었다.

-----
## The Basics – Git and Ansible

이전에는 사실 많은 고려사항이 필요하지 않았다. - 어떤 프로젝트든 또는 약간 복잡하더라도 버전 관리 시스템(git 이든 아니든 상관없이)을 사용하면 됐다. 그런데 왜 앤서블이지? 우리는 지금까지 몇 년동안 푸펫(pupper)과 앤서블을 사용하고 있었다. 푸펫은 대상 장비에 에이전트를 설치해야하고(물론 에이전트는 쥬니퍼를 지원한다), 이상적으로는 푸펫 마스트를 설치해야 하는 반면, 앤서블과 다른 추가 라이브러리는 각각의 워크스테이션에 설치되어야 한다.(또는 중앙 관리 서버에도 설치되야 한다). 

지난 몇년동안 푸펫을 활용해서 서버의 기본 설정(인증, 로깅, 패킷 소스 등)을 관리해왔고, 앤서블로는 보다 상위 레벨에 있는 LDAP, DNS 서버, 로드밸런서 그리고 하루에도 몇 번씩 배포해야하는 모든 내부 서비스를 관리해왔다. 하지만 앤서블이 푸펫보다 쉽고, 에이전트를 설치할 필요가 없으며 플레이북(playbook)과 롤(role)을 파악하기 쉽기 때문에 앤서블로 결정했다.

-----
## Ansible – now what?

앤서블의 가장 큰 장점은 수 많은 가용한 모듈들이다. 특히 2.0 버전 이 후로 네트워크 관련 모듈들이 많이 추가되었고 쥬니퍼 장비에 대한 지원도 많아졌다. 동시에 주니퍼에서도 앤서블 모듈을 제공하게 되어 기존 앤서블의 모듈을 대체해서 사용할 수 도 있게 되었다. 지금까지는 오직 앤서블에서 공식 제공하는 모듈만을 사용해왔다. 그 이유는 앤서블이 새로운 버전으로 업데이트되었을 때, 이 업그레이드를 쉽게 따라가기 위해서 였다. 하지만 우리가 원하는 기능이 앤서블 공식 버전에는 없고, 쥬니퍼에서 제공하는 모듈에만 있을 경우 또한 쥬니퍼의 모듈이 공식 버전으로 포함될 가능성이 없어 보일 경우에는 쥬니퍼 모듈을 사용하려고 한다. 우리 시스템은 대부분 Debian/Ubuntu 계열 기반이므로 이에 맞춰 앤서블 공식 모듈을 얻는 방법과 실행하는 방법을 설명토록 하겠다(사용한 Ansible 버전은 2.2이다).

```
apt-get install python-pip libxml2-dev libffi-dev python-dev libxslt1-dev libssl-dev pip install junos-eznc jxmlease
```

주니퍼 장비에서 정상적으로 ansible을 작동시키기 위해서는 "netconf over ssh"를 활성화 해야 한다.

```
set system services ssh 
set system services netconf ssh
```

패스워드 없이 인증키 기반 SSH 접속도 가능하다. 하지만 우리는 Radius기반 인증을 사용하기 때문에 username/password를 사용할 수 밖에 없다. 아래 코드는 예제 플레이북으로 사용자 이름과 암호를 물어보고, netconf 변수에 딕셔너리 형태로 저장해서 쥬니퍼 모듈을 설정하는데 사용케 한다. 사용법에 대해서는 다음 섹션에서 설명하겠다.

```
- hosts: core_switches
  serial: 1
  connection: local
  gather_facts: False
  vars_prompt:
    - name: "netconf_user"
      prompt: "Netconf login user"
      default: "root"
      private: no
    - name: "netconf_password"
      prompt: "Netconf login password"
      private: yes 
  vars:
    netconf:
      host: "{{ inventory_hostname }}"
      username: "{{ netconf_user }}"
      password: "{{ netconf_password }}"
      timeout: 30
  roles:
    - role: base_setup
    - role: core_setup
```

-----
## Templates, Templates everywhere!
앤서블의 장점 중 하나는 강력한 템플릿(template) 사용에 있다. 공식 앤서블 모듈은 이것을 직접 지원하지는 않아서 우리는 간단한 우회방법을 사용하였다.
```
  - name: generate dns configuration
    template: src=dns.j2 dest=/tmp/junos_config_deploy/{{ inventory_hostname }}/dns.conf
    changed_when: false

  - name: install dns configuration
    junos_config:
      src: /tmp/junos_config_deploy/{{ inventory_hostname }}/dns.conf
      replace: yes 
      src_format: text
      provider: "{{ netconf }}"
```

처음에 일반 설정파일을 로컬에서 변경한다. 이 후, 이 파일을 *junos_config* 모듈을 활용해서 장비로 옮긴다. Junos는 기본적으로 템플릿을 기존 설정과 합쳐버려 설정이 꼬여버릴 수가 있지만, 다행히도 *replace* 문법을 사용하면 기존 설정을 아예 바꿔버릴 수 있다. 그러므로 *replace* 문법을 사용하면 동일한 이름의 기존 설정을 모두 교체할 수 있다. 아래가 이에 해당하는 예제이다.
```
system {
    replace:
    name-server {
{% for ip in dns_ips %}
        {{ ip }};
{% endfor %}
    }
    host-name {{ inventory_hostname_short }};
    domain-name some.domain.here;
}
```

보는바와 같이, 이 예제는 약간 짧은 템플릿이다. 우리는 장비 설정을 작은 단위로 분리해서, 하나의 템플릿이 동일한 설정을 유지할 수 있는 주체가 되도록 강조하였다. 이러한 설정의 분리는 커다란 템플릿 파일 하나를 관리하는 것보다 많은 잇점을 가지고 있다. 예를 들어, 중요한 스위치 인터페이스 설정이 실패했는지, 네임서버 설정을 망쳤는지와 같이 에러 위치를 파악하는데 유리하다. 또한 앤서블의 롤(role)을 사용해서 설정의 일부만 선택하여 배포할 수도 있게 한다. 또한 당연한 것이지만 짧은 템플릿이 가독성도 좋다.

한가지 주목할 만한 단점은 플레이북 실행시간이다. 각 *junos_config* 작업은 적용완료(commit)가 되면서 끝나게 되는데, 어떤 경우는 수 초안에 끝나지만 어떤 경우는 영원히 끝나지 않을 때가 있다. 30대 정도 장비를 설정하면서 영원히 기다릴 수는 없지 않은가.

-----
## Block to the rescue!

앤서블은 에러 핸들링을 위해 try..catch 구문과 유사한 기법은 제공데 그것은 바로 block..rescue 이다. (이름을 변경한 이유는 있겠지만, 왜 이렇게 이름을 바꿨는지 모르겠다)
어쨌든 다음 템플릿처럼 block 구문을 사용하면 디버깅하기 훨씬 쉽다.

```
- block:
  - name: remove config preparation folder
    file: path=/tmp/junos_config_deploy/{{ inventory_hostname }} state=absent
    changed_when: False
  - name: generate config preparation folder
    file: path=/tmp/junos_config_deploy/{{ inventory_hostname }} mode=0700 state=directory
    changed_when: False

  [...]
  template/junos_config Tasks
  [...]

  - name: remove config preparation folder
    file: path=/tmp/junos_config_deploy/{{ inventory_hostname }} state=absent
    changed_when: False
    tags: syslog

  rescue:
    - debug: msg="configuring the switch failed. you can find the generated configs in /tmp/junos_config_deploy/{{ inventory_hostname }}/*.conf and try yourself"
    - debug: msg="scp the file to the switch and execute 'load replace <filename>' + 'commit' in conf mode"
    - fail: msg="stopping the playbook run"
```

플레이북의 처음 작업은 기존에 잘못됐을 수도 있는 설정 파일을 지운다. 두번 째는 설정파일을 위한 디렉토리를 생성하고 새로운 설정 파일을 생성하고 *junos_config* 모듈을 사용해서 장비에 적용시킨다. 이 작업들은 모두 *block* 구문으로 뭉쳐진다. 이 *block* 구문 안에서 하나의 작업이라도 실패하면, *rescue* 안의 작업이 실행되어 플레이북을 실행하는 사람에게 유용한 정보를 남길 수 있도록 하여 에러를 디버깅하기 쉽게 할 수 있다. 에러 메시지는 *junos_config* 모듈가 뿌려주는데 불행히도 이 에러메시지가 항상 도움이 되지는 않는다. 그래서 때로는 수동으로 설정 템플릿을 장비에 올리고, 테스트해보아야 한다.

-----
지금 작성한 글이 앤서블을 활용해서 네트워크 설정 자동화를 이룩하는데 도움이 되길 바라고, 앞으로도 계속 지켜봐주길 바란다.
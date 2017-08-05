# AUTOMATING NETWORK DEVICES WITH ANSIBLE

원문: http://www.sipgateblog.de/automating-network-devices-with-ansible/

예전에 우리는 우리의 독익 고객에게 네트워크 인프라스트럭처의 일부를 교체하기 위해 노력중이라고 말했었다. 그리고 요즘의 기술 변화를 발맞추기 위해 앤서블과 쥬니퍼(Juniper)를 활용해서 완전히 자동화된 네트워크 설정을 이룰 것을 결정했다. 이런 컨셉에 맞게 자료를 찾아보다보니 관련된 온라인 기술자료가 너무나 부족하다는 것을 알게 되었고, 유사한 환경을 구축하려는 사람들에게 도움을 주기위해 이 글을 쓰게 되었다.

## The Basics – Git and Ansible
The former does not need much consideration – any project even slightly complex should use a version control system, be it git or something else. But why Ansible? We at sipgate have been using Puppet as well as Ansible for quite some years now. While Puppet needs an agent on the target device (which is supported by Juniper) and ideally a Puppet master setup, Ansible and some additional libraries need to be set up on every workstation (or on a central management server).

이전에는 사실 많은 고려사항이 필요하지 않았다. - 약간 복잡한 프로젝트라도 굳이 버전 관리 시스템(git 이든 아니든 상관없이)을 사용할 이유가 없었다. 그런데 왜 앤서블이지? 우리는 지금까지 몇 년동안 푸펫(pupper)과 앤서블을 사용하고 있었다.푸펫은 대상 장비에 에이전트를 설치해야하고(물론 에이전트는 쥬니퍼를 지원한다), 이상적으로는 푸펫 마스트를 설치해야
## Ansible – now what?
## Templates, Templates everywhere!
## Block to the rescue!

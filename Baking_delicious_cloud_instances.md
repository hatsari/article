* 원본: https://blog.kintoandar.com/2017/06/Baking-delicious-cloud-instances.html


#맛있게 클라우드 인스턴스 굽는 방법, Baking delicious cloud instances

![baked cake](https://blog.kintoandar.com/images/cake.jpg)

최근 클라우드 인프라 환경에서는 형상관리(configuration management) 솔루션을 사용해야 운전석이 아닌 사장님 자리에 앉는 것 같은 편안함을 느낄 수 있다.
특히나 서비스가 미이라처럼 죽지 않고 불사조처럼 되살아나기를 바라는 사람들의 요구사항을 맞춰주기 위해서는, 더욱 더 많은 쉘 스크립트로 인스턴스를 관리하는 모습을 볼 수 있다.
대표적인 예는 Dockerfiles 일 것이다. 하지만 여기서 다루고자 하는 것이 컨테이너(container)는 아니다.

서버를 죽지 않도록 만드는 부분은 잠깐 접어두고, 불사조 서버와 부팅시 설정 관리 방법에 좀 더 알아보겠다. 
나는 요즘 시스템 설정을 좀 더 간단하고, 효율적으로 관리하는 방법이 분명히 있을 것이라 생각하고 그 부분을 테스트해보게 되었다.

## Amazon Web Services
![aws](https://blog.kintoandar.com/images/amazon_aws.png)

그동안 일해오면서 주로 다루던 환경은 베어메탈, Xen, KVM, LXC 컨테이너 였고, 클라우드로는 Vmware Vcloud, Openstack 이었다. 그런데 올해부터는 아마존 웹서비스(AWS) 자세히 들여다보게 되었고 여기에 AWS를 사용하면서 내가 느낀 점을 말해보도록 하겠다.
지금까지 사용하면서 나는 크게 두 가지 패턴을 보게 되었다.
- 입 맛에 맞는 최종 인스턴스가 생성되도록 하기 위해 부팅시에 복잡한 쉘 스크립트를 추가해서 인스턴스 구성.
- AMI 이미지에는 모든 환경 설정을 집어 넣고, 부팅시에 필요한 것만 불러와서 인스턴스 구성.

두 가지중 어떤 것을 선택하든 동일한 문제를 만나게 되는데, 첫째는 AMI 이미지를 만드는 과정이 필요한 것과 둘째는 이 후 부팅 이 후의 최종 설정을 맞춰야한다는 것이다.

혹자는 서비스 디스커버리(service discovery)는 나중에 해도 된다고 말할 수 있겠지만 여전히 사용자 서비스와 연동하는 부분에는 신경을 써야만 한다. 게다가 대부분의 서비스는 서비스 디스커버리를 지원하지 않는게 현실이다. 그래서 지금 이 부분은 깊게 파고 들어가지 않겠다.

## Configuration Management
지난 몇 년간 복잡한 인프라 환경에서 Chef와 Ansible을 사용해서, 다수의 Chef용 쿡북, 레시피, 프로바이더를 만들고 앤서블(ansible)용 플레이북, 롤, 모듈을 제작하고 있다. 이런 경험으로 인해 이 도구들 각각에 대해 확고한 사견을 가지게 되었다.

![chef](https://blog.kintoandar.com/images/Chef.png)

* Chef는 배우기 매우 어렵워서 머릿속에 넣고도 힘들다. 하지만 루비(ruby)언어와 DSL(domain specific language)를 사용해서 복잡한 시나리오를 쉽게 관리할 수 있는 장점이 있다.

![ansible](https://blog.kintoandar.com/images/ansible.png)

* 앤서블은 배우기도 가르치기도 진짜 쉽다. 하지만 복잡한 작업을 구현하려고 하면 문제가 
Ansible is dead simple to learn and teach, but quickly becomes problematic when complexity needs to be addressed. “Coding” YAML is a pain and Jinja templates are not a walk in the park either. On the modules’ side python helps quite a lot. 

Chef has a steep learning curve and it’s hard to get your head around it, but it allows easy management of complex scenarios by having ruby exposed alongside the domain specific language.

For the past few years I’ve been using Chef and Ansible in complex environments, authored several Chef cookbooks, recipes and providers as well as Ansible playbooks, roles and modules. As such, I have strong opinions regarding each one of these tools. In a nutshell:
## Infrastructure Management
## Cooking up a plan
## Components
## Tasting some baked goods
## Pro tips
## Ready to be served

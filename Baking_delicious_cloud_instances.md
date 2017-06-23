* 원본: https://blog.kintoandar.com/2017/06/Baking-delicious-cloud-instances.html


# 맛있게 클라우드 인스턴스 굽는 방법, Baking delicious cloud instances

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

* 앤서블은 배우기도, 가르치기도 진짜(dead simple) 쉽다. 하지만 복잡한 작업을 구현하려고 하면 문제가 발생하기 쉽다. YAML을 짜고 Jinja 템플릿 작성을 만드는  것도 쉽지만은 않다. 모듈 측면에서는 파이썬으로 만들면 상당히 도움이 된다.

> OH: "Principal YAML Engineer"
> — Joel (@kintoandar) June 10, 2017

하지만 오해는 마시라. 이 두개의 도구에 나는 정말 감사하고 있으며 내가 만들어온 배포 오케스트레이션의 대부분은 이 툴들을 사용하였고 이로인해 큰 도움을 받았다.

작업을 할 때 도구를 선택할 때는 항상 신중해야 하고 조직에 끼칠 수 있는 영향도 고려되어야 한다. 그러므로 당신이 직면하고 있는 요구사항에 가장 적합한 도구를 선택하기 위해 고민해야한다. 다음 몇 개의 빤짝거리는 도구를 사용해보고 "이 언어는 나한테 딱 맞아", "이 애쟈~일한 프레임웍은  딱 좋아" 같은 생각을 가질 수도 있지만, 당신이 추구하는 회사의 전체 성장 또는 고려해야할 사항들과 비교해보면 그런 것은 아무 의미 없다.

> 그치만, 역시 쉘스크립트가 최고야. 그렇치 않아?

당신 혼자만 관리하는 시스템이라면 그렇다. 하지만 모든 사람들에게 제공되는 도구라면 썩 좋치는 않다.

Brent([The Phoenix Project](https://www.goodreads.com/book/show/17255186-the-phoenix-project)의 IT 닌자)같은 사람이 되는 것이 이제 선택이 아닌 필수이다. 늘어나는 시스템 그리고 이에 따른 비즈니스의 성장을 잘 지원하기 위해서 기술력이 잘 전파되고 모든 사람이 우리가 만든 도구를 수정하고 개선하고 잘 활용할 수 있도록 해야 한다. 

## Infrastructure Management
![terraform](https://blog.kintoandar.com/images/terraform.png)
Terraform같은 툴은 전체 인프라를 관리할 때 오케스트레이션에서 발생할 수 있는 간극을 메워주고자 한다. 하지만 이 제품을 개별 관리를 위한 설정관리 도구라고 생각하지는 않는다. 적어도 인스턴스 측면에서는  인스턴스가 사설 서브넷망 안쪽에 존재하고, 작동방식이 user_data 설정을 모아주고, cloud-init 스크립트를 삽입하는 것을 가정하면 된다.

## Cooking up a plan
이렇게 여러가지를 둘러보면 한 가지 궁금한 점이 생긴다. "그럼 난 뭘 선택해야하지?"
- 프로세스 상으로 동일한 일을 반복하게 하지마라. [DRY](https://en.wikipedia.org/wiki/Don%27t_repeat_yourself) 
- 만들어진 스크립트와 최종 배포본을 누구라도 이해하고 자신있게 수정할 수 있도록 하라. 
- 코드를 재사용할 수 있도록 하라
- 동일 환경(Environment Parity)

내가 이 리스트를 만들때, 위 조건들을 모두 만족시키는 방법이 무엇일까를 고민하기 시작했고 이를 위한 작업흐름도(workflow)를 그려냈다. 다음 다이어그램이 작업흐름도를 표현하고 있다.

![workflow](https://blog.kintoandar.com/images/bakery_sequence.jpg)

의견: 솔직히 말해, 나는 앤서블보다는 Chef를 선호해 왔다. 하지만 더 많은 사람들과 연계되고 협업하면서 쉽게 설정 관리 지식을 공유할 수 있는 방법을 찾아야 했고 따라서 ,위에 언급한대로 사용하기 쉽기 때문에, 앤서블을 채택했다. 이로 인해 설정관리 부분에서 다른 개발자들과 협업하기 쉽고, 직관적이 되도록 노력하였다. 

## Components
이 작업 흐름도는 몇 가지 주요 구성요소를 가지고 있는데 각각이 자신이 담당하는 작업과 역할이 별도로 있다.

### Orchestrator
모든 작업이 촉발되는(triggered) 시점에 원하는 걸 하나 골라라.
- Jenkins
- Travis
- Thoughtworks Go
- ...

### Local Cache
프로젝트 저장소에 소스 파일이 생성되고 모든 의존성 파일들이 저장되었다. [앤서블 플레이북](https://github.com/kintoandar/bakery/)을 사용해서 이 경로는 백업될 것이고, /root/bakery에 AMI 형태로  보내지게 된다.

AMI가 cloud-init 파일로 인스턴스화 되었을 때, 앤서블 플레이북이 다시 작동해서 cloud_init을 덮어쓰고 다른 작업 흐름을 따르도록 변경시킬 것이다. 

### Ansible-Galaxy
당신이 굉장한 Berkshelf 와  berks 벤더에 익숙하다면, ansible-galaxy는 유사한 목적을 제공하고 있어서, 앤서블 롤(Role)의 의존성을 해결해주고 로컬로 복제본을 만들어 준다.
심지어 공개된 저장소가 아닌 사설 저장소도 만들 수 있으며 그 예제는 다음과 같다.

'''
~ $ cat requirements.yml
---
- src: git@github.com:PrivateCompany/awesome-role.git
  scm: git
  version: v1.0.0
  name: awesome-role
'''

다음 명령으로는 의존성있는 롤을 다운받을 수 있다.
'''
ansible-galaxy install -r ./requirements.yml -p ./roles
'''

### Ansible
롤을 사용하면 코드 재사용이 향상된다. 그리고 알아보기 힘든 sed 한줄코딩 대신에, 보기 편한 템플릿을 사용해라(물론 정규표현식 완소!)

롤을 작업 파일당 분리하기가 어렵다면, 설치된 것과 분리해서 템플릿 형태로 사용할 수도 있다. 이 경우에는 이미지를 만들거나, 부팅시 최종 설정을 할 때, 코드 워크플로우를 분리할 수 있기 때문에 매우 유용하다.

### packer
![packer](https://blog.kintoandar.com/images/packer.png)

[이전 글](https://blog.kintoandar.com/2015/01/veewee-packer-kickstarting-vms-into-gear.html)을 참고하라.

## Tasting some baked goods

## Pro tips
## Ready to be served

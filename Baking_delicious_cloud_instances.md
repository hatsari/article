원본: https://blog.kintoandar.com/2017/06/Baking-delicious-cloud-instances.html

#맛있게 클라우드 인스턴스 굽는 방법, Baking delicious cloud instances

![baked cake]
(https://blog.kintoandar.com/images/cake.jpg)

최근 클라우드 인프라 환경에서는 형상관리(configuration management) 솔루션을 사용해야 운전석이 아닌 사장님 자리에 앉는 것 같은 편안함을 느낄 수 있다.
특히나 서비스가 미이라처럼 죽지 않고 불사조처럼 되살아나기를 바라는 사람들의 요구사항을 맞춰주기 위해서는, 더욱 더 많은 쉘 스크립트로 인스턴스를 관리하는 모습을 볼 수 있다.
대표적인 예는 Dockerfiles 일 것이다. 하지만 여기서 다루고자 하는 것이 컨테이너(container)는 아니다.

서버를 죽지 않도록 만드는 부분은 잠깐 접어두고, 불사조 서버와 부팅시 설정 관리 방법에 좀 더 알아보겠다. 
나는 요즘 시스템 설정을 좀 더 간단하고, 효율적으로 관리하는 방법이 분명히 있을 것이라 생각하고 그 부분을 테스트해보게 되었다.

## Amazon Web Services
![aws](https://blog.kintoandar.com/images/amazon_aws.png)
그동안 일해오면서 주로 다루던 환경은 베어메탈, Xen, KVM, LXC 컨테이너 였고, 클라우드로는 Vmware Vcloud, Openstack 이었다. 그런데 올해부터는 아마존 웹서비스(AWS) 자세히 들여다보게 되었고
여기에 AWS를 사용하면서 내가 느낀 점을 말해보도록 하겠다.
지금까지 사용하면서 나는 크게 두가지를 느끼게 되었다. 

During my career I’ve worked with bare metal servers, XEN and KVM virtualization, LXC containers and 
private cloud environments like VMware vCloud and Openstack. This year,
I’ve been looking more closely into Amazon Web Services (AWS), so that’s what I’ll be addressing here


최근 클라우드 인프라 환경에서는 형상관리(configuration management) 솔루션을 사용해야 운전석이 아닌 사장님 자리에 앉는 것 같은 편안함을 느낄 수 있
최근 클라우드 인프라 환경에서는 형상관리(configuration management) 솔루션을 사용해야 운전석이 아닌 사장님 자리에 앉는 것 같은 편안함을 느낄 수 있다
## Configuration Management
## Infrastructure Management
## Cooking up a plan
## Components
## Tasting some baked goods
## Pro tips
## Ready to be served

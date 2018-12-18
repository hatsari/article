# Ansible Task Result with Prometheus and Grafana
ansible로 작업을 자동화하고 이에 대한 결과를 리포트로 만들어야 할 때가 있다. 또는 시스템의 정보를 ansible을 통해 가져오고 이를 대시보드로 보고자 할 때도 있다. 이런 작업은 ansible 또는 ansible-tower만 가지고는 지원하기 힘든 기능이기 때문에 grafana를 사용해서 표현할 수 있는 방법을 찾아보고자 이번 테스트를 진행하게 되었다. 또한 기존 데이터를 지속적으로 저장하고 기존과의 추이를 비교하기 위해서 prometheus도 같이 사용하였다. prometheus와 grafana는 최근 가장 많이 사용되는 모니터링 도구이기 때문에 ansible과의 연계도 이미 다른 사람이 진행했을 거라는 안일한 생각으로 시작했는데 막상 테스트하다보니 마땅한 자료를 찾기 힘들었다. 또한 위 두 솔루션에 대한 지식이 높이 않은 상태에서 진행하다보니 사소한 문제를 해결하는데도 많은 시간이 걸렸고, 아직도 해결 못한 문제가 몇가지 있는 상태이다. 

이번 테스트에서는 ansible의 facts 정보를 기반으로 시스템의 cpu와 메모리 정보를 불러오는 것과 grafana 쓰레드 사용개수를 변수로 저장하여 prometheus에 저장하고 이를 다시 grafana 로 표현하도록 하였다.

- 결과는 다음과 같다.
![result](images/grafana_result.png)

## Environment
- vagrant + virtualbox: VM을 생성하고 prometheus와 grafana를 설치
- ansible: 여러 시스템에 접속하여 Task를 수행하고 해당 결과를 pushgateway로 보냄
- prometheus: pushgateway로 부터 받은 데이터를 저장하고 grafana의 데이터소스로 활용
- node-exporter: 일종의 모니터링 agent로서 서버들에 설치되고, prometheus가 node-exporter 데몬에 접속하여 정보를 수집 
- pushgateway: prometheus는 기본이 pull 방식으로 자신이 직접 해당 데이터를 수집해감. 반대로 prometheus에 데이터를 밀어넣기(push) 하기 위해서는 pushgateway 설치가 반드시 필요.
- grafana: 오픈소스에서 가장 뜨거운 대시보드 솔루션

### Version
- node_exporter_version: 0.17.0
- prometheus_version: 2.5.0
- pushgateway_version: 0.7.0
- grafana: 5.1.3-1

## Installation
### VM on Vagrant
Vagrant 파일 내용은 아래와 같으며, ansible 플레이북 provision/prometheus.yml 으로 필요한 설정을 모두 구성토록 하였다. 
```ruby
Vagrant.configure("2") do |config|
  config.vm.box = "rhel7"
  config.vm.hostname = "prometheus"
  config.vm.network "private_network", ip: "172.28.128.3"
  config.vm.provision "ansible" do |ansible|
    ansible.playbook = "provision/prometheus.yml"
    ansible.inventory_path = "provision/inventory"
    ansible.limit = "all"
    ansible.verbose = "vv"
    ansible.become= "yes"
  end
end
```

### Prometheus, nodexporter, pushgateway, grafana Installation
prometheus.yml 플레이북은 다른 분이 작성한 내용을 일부 수정하여 사용하였고 원본에 아래 참고 페이지에 링크로 제공한다.
[playbook](vagrant/provision/prometheus.yml)
#### 해당 플레이북에서 볼 만한 내용은 다음과 같다.
- node-exporter와 pushgateway를 systemd job으로 등록하는 법
- unarchive 모듈이 작동하지 않아, shell 모듈로 압축파일을 풀었음
- 모든 패키지들은 /home/prometheus 하위 디렉토리에 설치(prometheus 설정파일인 prometheus.yml(플레이북 파일이름과 동일하나 전혀 다른 설정 파일) 파일은 /home/prometheus/prometheus-2.5.0.linux-amd64/ 에 위치)

## Configuration
### Data Flow
ansible task -> pushgateway -> prometheus -> grafana

![prometheus_data_flow](https://478h5m1yrfsa3bbe262u7muv-wpengine.netdna-ssl.com/wp-content/uploads/2018/08/kubernetes_prom_diagram2.png)

* 이미지 하단의 kubernetes는 관계없으므로 무시해도 됨.

설정 순서는 다음과 같다.
- grafana 접속 및 정상여부 확인
- node-exporter 설정을 위한 json 다운로드 및 설정 적용
- pushgateway로 데이터를 보내기 위한(push) ansible playbook 작성 및 실행
- prometheus에서 해당 metric을 정상적으로 수집했는지 확인
- grafana의 대시보드에서 ansible로 수집한 데이터 표현 

### Confirming Services
systemctl 명령으로 필요한 각 서비스들이 정상적으로 가동되었는지 확인

```shell
[root@prometheus ansible]# for i in  grafana-server prometheus node_exporter pushgateway ;do systemctl status $i;done

● grafana-server.service - Grafana instance
   Loaded: loaded (/usr/lib/systemd/system/grafana-server.service; enabled; vendor preset: disabled)
      Active: active (running) since Fri 2018-12-14 00:45:30 UTC; 3 days ago
	       Docs: http://docs.grafana.org
		    Main PID: 10249 (grafana-server)
			   CGroup: /system.slice/grafana-server.service
			              └─10249 /usr/sbin/grafana-server --config=/etc/grafana/grafana.ini --pidfile=/var/run/grafana/grafana-server.pid cfg:default.paths.logs=/var/log/grafana cfg:default...


● prometheus.service - Prometheus
   Loaded: loaded (/etc/systemd/system/prometheus.service; enabled; vendor preset: disabled)
      Active: active (running) since Sun 2018-12-16 03:48:37 UTC; 1 day 20h ago
	   Main PID: 16753 (prometheus)
	      CGroup: /system.slice/prometheus.service
		             └─16753 /home/prometheus/prometheus-2.5.0.linux-amd64/prometheus --config.file=/home/prometheus/prometheus-2.5.0.linux-amd64/prometheus.yml --storage.tsdb.path=/hom...
					 
● node_exporter.service - Node exporter
   Loaded: loaded (/etc/systemd/system/node_exporter.service; enabled; vendor preset: disabled)
      Active: active (running) since Fri 2018-12-14 05:23:59 UTC; 3 days ago
	   Main PID: 12405 (node_exporter)
	      CGroup: /system.slice/node_exporter.service
		             └─12405 /home/prometheus/node_exporter-0.17.0.linux-amd64/node_exporter --collector.textfile.directory=/var/lib/node_exporter/metrics

● pushgateway.service - Push Gateway
   Loaded: loaded (/etc/systemd/system/pushgateway.service; enabled; vendor preset: disabled)
      Active: active (running) since Fri 2018-12-14 04:24:30 UTC; 3 days ago
	   Main PID: 11680 (pushgateway)
	      CGroup: /system.slice/pushgateway.service
		             └─11680 /home/prometheus/pushgateway-0.7.0.linux-amd64/pushgatew
```

### Grafana basic configuration
#### web console access
웹브라우저를 통해 아래 grafana 대시보드를 접속
- web access: http://172.28.128.3:3000
- default id/pw: admin/admin

#### adding prometheus datasource
데이터를 수집할 prometheus를 데이터소스로 추가
1. grafana 웹하면의 왼쪽 메뉴에서 톱니바퀴 모양 클릭
2. *Data Sources* 선택
3. 내용을 입력하는 화면에서 *Name* 입력하고, *Type*에 *Prometheus* 선택, *URL* 부분에 "http://localhost:9090" 입력 후 *Save & Test* 확인
![grafana-datasource](images/datasource-2.png)
### node-exporter configuration
### pushgateway configuration
#### ansible playbook to gather information
#### send metric to prometheus
### prometheus - check if metric is stored

## Todo more
### ansible uri tasks
### grafana values
### 


## prometheus knowledge
- presenter: http://172.28.128.3:9090
### node-exporter
node_exporter is aimed to gather host information and send it to prometheus.
- systemctl status node_exporter
- curl http://172.28.128.3:9100/metrics





## References
download prometheus: https://prometheus.io/download/
simple prometheus explaination: https://itnext.io/monitoring-with-prometheus-using-ansible-812bf710ef43
ansible slack kibana grafana: https://dzone.com/articles/how-to-get-metrics-for-alerting-in-advance-and-pre
install promethus: https://fritshoogland.wordpress.com/2018/06/06/quick-install-of-prometheus-node_exporter-and-grafana/
node exporter: https://prometheus.io/docs/guides/node-exporter/
prometheus: http://www.markusz.io/posts/2017/10/27/monitoring-prometheus/
prometheus pushgateway: https://github.com/prometheus/pushgateway


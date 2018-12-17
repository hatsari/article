# Ansible Task Result with Prometheus and Grafana
ansible로 작업을 자동화하고 이에 대한 결과를 리포트로 만들어야 할 때가 있다. 또는 시스템의 정보를 ansible을 통해 가져오고 이를 대시보드로 보고자 할 때도 있다. 이런 작업은 ansible 또는 ansible-tower만 가지고는 지원하기 힘든 기능이기 때문에 grafana를 사용해서 표현할 수 있는 방법을 찾아보고자 이번 테스트를 진행하게 되었다. 또한 기존 데이터를 지속적으로 저장하고 기존과의 추이를 비교하기 위해서 prometheus도 같이 사용하였다. 

prometheus와 grafana는 최근 가장 많이 사용되는 모니터링 도구이기 때문에 ansible과의 연계도 이미 다른 사람이 진행했을 거라는 아닐한 생각이 시작했는데 막상 테스트하다보니 마땅한 자료를 찾기 힘들었다. 또한 위 두 솔루션에 대한 지식이 높이 않은 상태에서 진행하다보니 사소한 문제를 해결하는데도 많은 시간이 걸렸고, 아직도 해결 못한 문제가 많이 있는 상태이다.
이번 테스트에서는 ansible의 facts 정보를 기반으로 시스템의 cpu와 메모리 정보를 불러오는 것과 grafana 쓰레드 사용개수를 변수로 저장하여 prometheus에 저장하고 이를 다시 grafana 로 표현하도록 하였다.

- 결과는 다음과 같다.
![result](images/grafana_result.png)

## Environment
- ansible
- prometheus
- node-exporter
- pushgateway
- grafana
### Version
- node_exporter_version: 0.17.0
- prometheus_version: 2.5.0
- pushgateway_version: 0.7.0
- grafana: 5.1.3-1

## Installation

### prometheus knowledge
- presenter: http://172.28.128.3:9090
### node-exporter
node_exporter is aimed to gather host information and send it to prometheus.
- systemctl status node_exporter
- curl http://172.28.128.3:9100/metrics

## Configuration
### Grafana basic configuration
### node-exporter configuration
### pushgateway configuration
#### ansible playbook to gather information
#### send metric to prometheus
### prometheus - check if metric is stored

## Todo more
### ansible uri tasks
### grafana values
### 

## References
download prometheus: https://prometheus.io/download/
simple prometheus explaination: https://itnext.io/monitoring-with-prometheus-using-ansible-812bf710ef43
ansible slack kibana grafana: https://dzone.com/articles/how-to-get-metrics-for-alerting-in-advance-and-pre
install promethus: https://fritshoogland.wordpress.com/2018/06/06/quick-install-of-prometheus-node_exporter-and-grafana/
node exporter: https://prometheus.io/docs/guides/node-exporter/
prometheus: http://www.markusz.io/posts/2017/10/27/monitoring-prometheus/
prometheus pushgateway: https://github.com/prometheus/pushgateway


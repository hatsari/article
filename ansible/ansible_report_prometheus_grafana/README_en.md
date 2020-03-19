# Ansible Task Result with Prometheus and Grafana
Sometimes we need to create job report when playbook completed or when gathered the system information. At this time, AWX or Ansible Tower is not suitable for this kind of report. So I decided to use prometheus as storage and grafana as a dashboard and ansible will work as metric collector. These combination make the report more flexible and customize easily. Both prometheus and grafana are popular monitoring solution these days and combined well also provides many types of plugins. Frankly I thought another guy aleady made it so just finding a right research is enough for me. However I couldn't find exact proper article to fit me. So I studied prometheus and grafana and tried to find a way to integrate with ansible. Finally I made it but still remaining some lack of ability. 

In this test, I will show you how ansible facts or values can be used as metric and how to push and store these metrics to prometheus, lastly how to present it on grafana dashboard.

- Final dashboard is right here.
![result](images/grafana_result.png)

## Environments
- vagrant + virtualbox: To create VM and install and configure a prometheus and grafana.
- ansible: To connect several managed nodes, run tasks and push the changes to pushgateway of prometheus.
- prometheus: To save the metrics from pushgateway and work as datasource for grafana.
- node-exporter: a kind of monitoring agent for prometheus. It will be installed on managed nodes and gather system information. This agent is not necessary for ansible metric. but it will make the dashboard show more information as like system uptime, disk usages ans so on.
- pushgateway: prometheus's basic operation is to pull the metric from the exporter, so  to perform to push operation, pushgateway is needed.
- grafana: Open source dashboard solution. what else..

### Version
- node_exporter_version: 0.17.0
- prometheus_version: 2.5.0
- pushgateway_version: 0.7.0
- grafana: 5.1.3-1

## Installation
### VM on Vagrant
The contents of *Vagrantfile* is below. keep on an eye for ansible playbook *provision/prometheus.yml* which will configure all needed components.
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
*prometheus.yml* is adapted from other guy's playbook and revised it. I'll provide original page below. Thanks for your sharing!!
[playbook](vagrant/provision/prometheus.yml)

#### Bottom lines in playbook 
- To register node-exporter and pushgateway as systemd job.
- unarchive module didn't work so extracted with shell module.
- All packages are install under /home/prometheus.(same named file *prometheus.yml is located in /home/prometheus/prometheus-2.5.0.linux-amd64/, but it is prometheus config file, not playbook).

## Configuration
### Data Flow
ansible task -> pushgateway -> prometheus -> grafana

![prometheus_data_flow](https://478h5m1yrfsa3bbe262u7muv-wpengine.netdna-ssl.com/wp-content/uploads/2018/08/kubernetes_prom_diagram2.png)

* ignore the kubernetes image which is not relative to.

Here is the operation order.
1. connect the grafana web ui and confirm the access
2. download node-exporter json from grafana web site and apply it
3. write ansible playbook to make ansible metric and to push it to pushgateway
4. identify the metric in prometheus web console.
5. present the metric on grafana dashboard

### Confirming Services
Confirm the services, grafana-server, prometheus, node_exporter, pushgateway, are stared with below command.

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
Access the grafana dashboare via web broswer.
- web access: http://172.28.128.3:3000
- default id/pw: admin/admin

#### adding prometheus datasource
Add a datasource "Prometheus"
1. Click a *Gear* image on left menu of grafana web console(http://172.28.128.3:3000).
2. Select *Data Sources*
3. Input *Name* , select *Prometheus* in *Type*, input *URL* "http://localhost:9090" in *URL* field and press *Save & Test*
![grafana-datasource](images/datasource-2.png)

### node-exporter configuration
*node-exporter* is an monitoring agent to collect the system information on server. It is essential to show various system informations like cpu, memory, disk, network usages. So this test also adapted *Host Stats* dashboard as initial board.

1. Access [grafana-host_stats](https://grafana.com/dashboards/9096) and download *json*
2. Click *+* mark on left menu of grafana web console(http://172.28.128.3:3000)
3. Select *import*
4. On *import* page, upload the *Host Stats json* file
5. Select *data source* of *prometheus* registed previously
![granfana-dashboard](images/import-dashboard.png)
6. Confirm Dashboard: Select *Host Stats - Prometheus Node Exporter 0.17.0*, the you can see below screen.
![grafana-hoststats](images/host-stats.png)

- node_exporter reference: https://prometheus.io/docs/guides/node-exporter/

### pushgateway configuration
*pushgateway* is a prometheus plugin to push the metric into prometheus. As I told already, prometheus is to pull the metrics from exporter basically. with *pushgateway", PUSH operation is possible.

prometheus provides many clients for pushgateway, but we will use ansible to generate the metric and push the metrics using *curl* script to pushgateway. Later I'll show you the playbook to generate metric and shell script to push the data.

Metrics by ansible
- ansible_cpu_size: a number of CPU cores which collected by ansible facts
- ansible_memory_size: total memory size(MB) which collected by ansible facts
- ansible_freememory_size: free memory size(MB) which collected by ansible facts
- ansible_thread_grafana_count: a number of threads which collected by ansible task

I used curl script to push the metric, at first, I tried to implement it with *URI* module but I failed so just used the shell module. if you know the way of URI, please let me know.
But this way of executing the shell modue is very useful to make multi lines script.

- pushgateway reference: https://github.com/prometheus/pushgateway

#### ansible playbook to gather information
below *push-event.yaml* is to gather the metric data from server and trasfer it to pushgateway manipulating *push_data.j2*.

``` cat push-event.yaml ```

```yaml
---
- name: push event to prometheus
  hosts: localhost
  connection: local
  tasks:
	  #  - name: push cpu
	  #    uri:
	  #      url: "http://localhost:9091/metrics/job/cpu_num"
	  #      method: POST
	  ##      body_format: form-urlencoded
	  #      body_format: json
	  #      validate_certs: no
	  #      body: { sample_metric: 5 }
	  #    register: token_output
	  #    ignore_errors: yes
	  
	  #  - name: push hardware metric
	  #    shell: echo "cpu_num 100 mem_num 1000 | curl --data-binary @- http://localhost:9091/metrics/job/pushgateway/instance/localhost:9091"
	  #    shell: |
	  #      cat <<EOF | curl --data-binary @- http://localhost:9091/metrics/job/ansible_metric/instance/localhost:9091
	  #      ansible_cpu_size 100 \
	  #      ansible_memory_size 1000 \
	  #      EOF
	  
  - name: calculate thread count
    shell: ps -eL | grep grafana | wc -l
    register: thread_grafana_count

  - name: push system information
    shell: "{{ lookup('template', 'push_data.j2') }}"
    args:
      executable: /bin/bash
							
  - name: print values
    debug:
      var:  thread_grafana_count
```

#### send metric to prometheus
*push_data.j2* is jinja template which shell script can use ansible variable and invoke curl command.
``` cat push_data.j2 ```

```sh
cat <<EOF | curl --data-binary @- http://localhost:9091/metrics/job/ansible_metric/instance/localhost:9091
## TYPE ansible_ip_address summary
#ansible_hostname {{ ansible_hostname }}
# TYPE ansible_cpu_size counter
ansible_cpu_size {{ ansible_processor_cores }}
# TYPE ansible_memory_size gauge
ansible_memory_size {{ ansible_memtotal_mb }}
# TYPE ansible_freememory_size gauge
ansible_freememory_size {{ ansible_memfree_mb }}
# TYPE ansible_thread_grafana_count gauge
ansible_thread_grafana_count {{ thread_grafana_count.stdout }}
EOF
```
* When transfer the metric, I failed to transfer *string* as metric, even though *number* is fine. as well, I don't know why.

### prometheus - check if metric is stored
To use the *pushgateway*, prometheus.yaml configuration file should be changed.
the last part *job_name: ansible_metric* is the configuration to activate it.
 
```shell
[root@prometheus ansible]# cat /home/prometheus/prometheus-2.5.0.linux-amd64/prometheus.yml
scrape_configs:

  - job_name: 'prometheus'
    scrape_interval: 1s
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'node_exporter'
    scrape_interval: 1s
    static_configs:
      - targets: ['localhost:9100']

  - job_name: 'ansible_metric'
    scrape_interval: 1s
    honor_labels: true
    static_configs:
      - targets: ['localhost:9091']
```

#### connecting prometheus dashboard
prometheus, as well, provides a web console, using it, you can verify the metric is stored properly.
- prometheus web url: http://172.28.128.3:9090
- Press *insert metric at cursor* and find ansible_cpu_size metric whihch we made and press *execute* button and *graph* tab.

[prometheus-web](images/prometheus-web.png)
***
[prometheus-job](images/prometheus-job.png)
***

## ansible report dashboard in grafana
If you confirm the metrics on prometheus, now it's time to move to grafana
I will add one *grafana threads* single stat and two tables for *cpu numbers* and *memory size*.

### SingleStat Panel for threads
1. Access *host stats* dashboard (http://172.28.128.3:3000/d/Czz-xPBmz/host-stats-prometheus-node-exporter-0-17-0)
2. Select "add panel" on upper middle of screen
![add-panel](images/grafana-add-panel.png)
3. *SingleStat* -> *Panel Title* -> *Edit*
4. Input *ansible_thread_grafana_count* metirc on *Metrics* Tab
5. Check *show* on *Guage* on *Options* Tab
![grafana-thread](images/grafana-thread.png)

### Table Panel for cpu and memory
1. Access *host stats* dashboard (http://172.28.128.3:3000/d/Czz-xPBmz/host-stats-prometheus-node-exporter-0-17-0)
2. Select "add panel" on upper middle of screen
3. *Table*-> *Panel Title* -> *Edit*
4. Input *ansible_cpu_size*, *ansible_memory_size* and *ansible_freememory_size* metrics on *Metric* Tab and check *instant*
5. Confirm you can see the tables on upper screen
![grafana table](images/grafana-table.png)
6. Select *Back* button on right upper of screen.

## Final Dashboard
Now you can see the completed dashboard.
![final dashboard](images/final-dashboard.png)

## Conclusion
Combining prometheus, grafana and ansible, I explained how to present the result of ansible job task. It is not just for job result, more over, it can show us the changes which caused by ansible. Although the above example can be achieved by other system monitoring solution easily, the important thing is to use ansible value as a metric. using this metric, we can expand the visibility of automation task. at least, I think so ^^. if you have any question about this solution or any answer for my questions, please send me email. 
## Todo more
- ansible uri tasks: how to write a playbook using uri module to push the metric, not using curl.
- grafana comprised values: how to present the value of cpu and memory in one colume.
- grafana column name: how to change the column name on table.

## References
download prometheus packages: https://prometheus.io/download/
simple prometheus explaination: https://itnext.io/monitoring-with-prometheus-using-ansible-812bf710ef43
ansible slack kibana grafana: https://dzone.com/articles/how-to-get-metrics-for-alerting-in-advance-and-pre
install promethus: https://fritshoogland.wordpress.com/2018/06/06/quick-install-of-prometheus-node_exporter-and-grafana/
node exporter: https://prometheus.io/docs/guides/node-exporter/
prometheus: http://www.markusz.io/posts/2017/10/27/monitoring-prometheus/
prometheus pushgateway: https://github.com/prometheus/pushgateway
### prometheus knowledge
- presenter: http://172.28.128.3:9090
### node-exporter
node_exporter is aimed to gather host information and send it to prometheus.
- systemctl status node_exporter
- curl http://172.28.128.3:9100/metrics


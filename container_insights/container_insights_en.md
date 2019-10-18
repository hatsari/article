# Monitoring a Container with Container Insights on AWS ECS Environment

Date: 10/11 2019, by Yongki, Kim(kyongki@)

This lab explains how to monitor container status on ECS using *Container Insights* of CloudWatch. Container Insights shows each Task's CPU, memory, network usage etc, as well combining with *alarm* and *notification* of *CloudWatch*, user can receive an alarm or email in real time.

**Key Practices**
* Setting Container Insights on specific ECS Cluster
* Configuring Alarm and Notification for Container Insights Metric
* Viewing Event and Log on ECS console
* Expanding EC2 instance which running Tasks automatically

## *Container Insights* Configuration on AWS ECS Cluster
An User can activate *Container Insights* with **aws** command. This command should be typed on *ecs-lab-workstation* launched earlier lab.

### Before Activation
In order to use **aws** command on terminal, an user should upgrade *awscli* package and register user authentication to access AWS resources.

#### *awscli* upgrade
To enable monitoring through *Container Insights*, *awscli* package should be upgraded to version 1.16.200 or later. Below is the command to upgrade *awscli* using *pip*.

``` shell
$ sudo pip install --upgrade pip
$ sudo /usr/local/bin/pip install --upgrade awscli
```

#### Registering aws credential
In order for *aws ecs* command to work properly, an user should create *Access Key ID* and *Secret Access Key* on *IAM* console and register those keys on terminal.

``` shell
[ec2-user@ip-10-0-0-236 api]$ aws configure
AWS Access Key ID [None]: [your own access key]
AWS Secret Access Key [None]: [your own secret access key]
Default region name [None]: ap-northeast-2
```
 - *ap-northeast-2* means Seoul region, you have to change the region name to where your resources, especially ECS, exist.
 - **CAVEAT**: After finishing the lab, you mush delete those secret information. It will be saved on *~/.aws/credentials* file

### ECS Cluster list
Using **aws ecs list-clusters** command, user can confirm his own cluster list.

``` shell
$ aws ecs list-clusters

{
    "clusterArns": [
        "arn:aws:ecs:ap-northeast-2:xxxxxxxxxxxx:cluster/default",
        "arn:aws:ecs:ap-northeast-2:xxxxxxxxxxxx:cluster/EcsLabPublicCluster"
    ]
}
```

### Enabling Container Insights
Using **aws ecs update-cluster-setting** command, user can enable *Container Insights* function.

``` shell
$ aws ecs update-cluster-settings --cluster EcsLabPublicCluster --settings name=containerInsights,value=enabled
{
    "cluster": {
        "clusterArn": "arn:aws:ecs:ap-northeast-2:xxxxxxxxxxxx:cluster/EcsLabPublicCluster",
        "clusterName": "EcsLabPublicCluster",
        "status": "ACTIVE",
        "registeredContainerInstancesCount": 0,
        "runningTasksCount": 0,
        "pendingTasksCount": 0,
        "activeServicesCount": 0,
        "statistics": [],
        "tags": [],
        "settings": [
            {
                "name": "containerInsights",
                "value": "enabled"
            }
        ]
    }
}
```

### Verifying Container Insights feature enabled on ECS Web console
After accessing ECS web console, and select **Clusters** menu on left pane, then user will see the message, **CloudWatch monitoring container insights**, like below screenshot.
![container_insights_enabled](images/container_insights_enabled.png)

## Looking inside *Container Insights*
User can see *CloudWatch* dashboard after configuring the metric of *Container Insights*.

### Container Insight 사용 방법
- quoted from here: https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/ContainerInsights.html, adding screenshots.

  1. Open the CloudWatch console at https://console.aws.amazon.com/cloudwatch/
  2. In the upper left of the screen, select the down arrow next to **Overview** and choose **Container Insights**
    Several graphs appear, displaying metrics about your clusters. Below the graphs is a list of clusters, with health and basic metrics shown for each one.
    To filter the view to a certain cluster, use the box at the top in the middle.
    ![container_insights_menu](images/container_insights_menu.png)

  3. At the top left, where it shows Clusters, switch to see metrics at the node, pod, service, task, and namespace levels. When you do so, you can also filter those views to look only at individual pods and nodes. You can also switch between Amazon EKS and Amazon ECS metrics.
    ![container_insights_metric](images/container_insights_metric.png)

  4. In any graph, pause on a legend line to see more information about that resource.
  5. At the cluster level, to view logs about one of the clusters in the dashboard, select the button next to its name in the list at the bottom of the screen. Then choose **Actions** and select one of the options in the list.
    - A new browser appears, showing a CloudWatch Logs Insights query for that resource.
    - Choose **Run query**. The query results are displayed.
    ![container_insights_query](images/container_insights_query.png)

  6. At the node, pod, or task level, to view logs about one or more resources currently displayed in the list at the bottom of the page, select the check boxes next to the names of those resources. Then choose Actions and select one of the options in the list. You can view logs or AWS X-Ray traces of the resource.

## Using CloudWatch Logs Insights to View Container Insights Data
Container Insights collects metrics by using performance log events, which are stored in CloudWatch Logs. You can use CloudWatch Logs Insights queries for additional views of your container data.

For more information about CloudWatch Logs Insights, see Analyze Log Data with CloudWatch Logs Insights. For more information about the log fields you can use in queries, see .

### To use CloudWatch Logs Insights to query your container metric data
  1. Open the CloudWatch console at https://console.aws.amazon.com/cloudwatch/
  2. In the navigation pane, choose **Insights**
    - Near the top of the screen is the query editor. When you first open CloudWatch Logs Insights, this box contains a default query that returns the 20 most recent log events
  3. In the box above the query editor, select one of the Container Insights log groups to query. For the following example queries to work, the log group name must end with **performance**
    ![container_insights_performance](images/container_insights_performance.png)
  When you select a log group, CloudWatch Logs Insights automatically detects fields in the data in the log group and displays them in **Discovered fields** in the right pane. It also displays a bar graph of log events in this log group over time. This bar graph shows the distribution of events in the log group that matches your query and time range, not only the events displayed in the table.

### Query Examples
In query editor, replace the default query to below one, and press **Run query**

  1. CPU Average Usage per TaskFamily
  ```
  STATS avg(CpuUtilized) as avg_node_cpu_utilization by TaskDefinitionFamily
  | SORT avg_node_cpu_utilization DESC
  ```
  Below is the result of example query. The result show container's CPU average usage per TaskFamily
      ![container_insights_cpu](images/container_insights_cpu.png)

  2. Used EC2 per Cluster
  ```
  STATS avg(ContainerInstanceCount) as instance_count by ClusterName
  | SORT ClusterName desc
  ```
  Below is the result of example query. The result shows how many ec2 are running for container.
      ![container_insights_instances](images/container_insights_instances.png)

  3. Container Count per Service
  ```
  stats avg(RunningTaskCount) as container_count by ServiceName
  ```
  Below is the result of example query. The result shows how many containers are running on service
      ![container_insights_containers](images/container_insights_containers.png)

## Troubleshooting Scenario
For the lab scenario, you will create container(Task) creation issue deliberately, monitor the status, and check the alarm and notification. After that, you will resolve the problem. As an early step, you have to configure *alarm* and *notification* on CloudWatch, it will help you identify the issue promptly.

### Configuring Alarm and Notification on CloudWatch
*Alarm* and *Notification* send user an event which user wants to receive individually. *Alarm* is shown in CloudWatch's alarm area, and *Notification* can sends a message using email or other methods. In this lab, you will set up alarm and notification to receive a message when running Tasks can't increase to the desired Tasks through *Pending Tasks* metric of *EcsLabApi* service.

#### How to configure it
1. Press *Alarms* menu on CloudWatch, and Select *Create Alarm*
  ![container_insights_alarm](images/container_insights_alarm.png)
2. Choose *Select metric* of *Metric* item on *Create new alarm* menu \
  ![container_insights_smetric](images/container_insights_smetric.png)
3. Select **ECS/ContainerInsights** among the metrics, next select **ClusterName,ServiceName**, and check **PendingTaskCount** metric of *EcsLabApi* service, then press **Select Metric**
  ![container_insights_pending](images/container_insights_pending.png)
4. Input alarm parameters

  4.1 Input parameters of *Alarm details*
    - *Name*: alarm_ecslabapi_pending
    - *Description*: alarm for ecslabapi pending tasks

  4.2 Input parameters of *Actions*
    - *Sending notification to*: press *new list* , input *notification_list* as topic name
    - *Email list*: [your email address]
    - press *Create Alarm*

  4.3 check your mailbox of mail address you wrote at previous step
      - press *confirm subscription* link in your confirmation mail

  4.4 Press *View Alarm* on CloudWatch web console, then creation completed
    ![container_insights_notification](images/container_insights_notification.png)

## Making Trouble
Increase the Task counts more than EC2's memory capacity, then Tasks will fail to reach up to *desired Tasks*. In this lab, *desired tasks* value of *EcsLabApi* service will be adjusted to 4, then running tasks will increase automatically. Each Task is consuming 512MB memory as defined in *task definition* however, *running tasks* may not increase to 4 because EC2's memory capacity is total 1GB. User can identify the gap between *desired tasks* and *running tasks*.
### 장애 유발
Task의 개수를 EC2가 수용할 수 있는 메모리 용량보다 크게 하며 원하는 만큼의 Task 개수(Desired Tasks)를 실행하지 못하도록 합니다. 이번 Lab에서는 *EcsLabApi* 서비스의 *desired tasks* 개수를 4개로 조절하여 가동시키고자 하는 task 개수를 증가시킬 것입니다. 해당 task는 *task definition*에서 정의한대로 각 task가 512MB 메모리를 점유하며, 현재 task가 가동되는 EC2는 1GB 메모리가 할당되어 있는 상태이므로, 가동시키고자 하는 task개수(desired task)만큼 task가 가동되지 못할 것입니다. 이 현상은 *desired tasks* 개수와 *running tasks* 개수의 차이를 통해 확인할 수 있습니다.

#### Increase *desired tasks* of *EcsLabApi*
1. Select *EcsLabPublicCluster* Cluster on *Clusters* menu on Amazon ECS web console
  ![container_insights_service_cluster](images/container_insights_service_cluster.png)
2. Select *EcsLabApi* service on *Services* menu
  ![container_insights_service_service](images/container_insights_service_service.png)
3. Confirm that the value of *desired tasks* and *running tasks* is **1**
  ![container_insights_service_update](images/container_insights_service_update.png)
4. Press *Update* menu on upper left side of screen
5. Input **4**
#### EcsLabApi 서비스의 Desired Tasks 개수 증가
1. Amazon ECS 서비스의 *Clusters* 메뉴에서 "EcsLabPublicCluster" 클러스터 선택
  ![container_insights_service_cluster](images/container_insights_service_cluster.png)
2. *Services* 메뉴에서 *EcsLabApi* 서비스 선택
  ![container_insights_service_service](images/container_insights_service_service.png)
3. 화면에서 현재 *Desired count* 와 *Running count*가 *1*로 표기되어 있는 확인
  ![container_insights_service_update](images/container_insights_service_update.png)
4. 화면 우측 상단의 *Update* 메뉴를 선택
5. *Number of tasks* 개수를 *4*로 입력한 후 *Skip to review* 선택
  ![container_insights_service_config](images/container_insights_service_config.png)
6. *Update Service* 를 선택하여 변경 적용
  ![container_insights_service_confirm](images/container_insights_service_confirm.png)
7. *Cluster:EcsLabPublicCluster* 화면에서 *Desired tasks* 개수와 *Running tasks* 개수 불일치 확인
  ![container_insights_service_verify](images/container_insights_service_verify.png)

### 모니터링을 통한 장애 확인
클러스터, 서비스, 또는 Task에서 변경 또는 에러가 발생했을 때, 이에 대한 로그는 *Service* 메뉴의 *Event* 또는 *Cloud Watch*의 *container insights* 메뉴에서 확인할 수 있습니다.

#### Event 항목을 통학 에러 확인
*Service* 또는 *Task*의 상태를 변경하였을 때, 이에 해당하는 로그는 *Service* 메뉴의 *Event*탭에서 확인할 수 있습니다. 이 메뉴에서는 변경 사항에 대해 이벤트가 발생한 시간과 관련 메시지를 보여줍니다. 또한 이전 설정한 **ALARM** 과 **이메일알림** 을 통해서도 이슈를 확인할 수 있습니다.
  ![container_insights_event](images/container_insights_event.png)

#### Container Insights 대시보드를 통한 개수 불일치 확인
*Container Insights*는 *Desired Tasks*와 *Running Tasks*의 대시보드를 기본 제공합니다. 두 지표를 확인함으로써 원하는 만큼의 *Task*가 정상적으로 가동중인지 확인할 수 있습니다.
1. Cloud Watch 의 Container Insights 선택
    ![container_insights_menu](images/container_insights_menu.png)
2. *Desired Tasks*와 *Running Tasks*의 대시보드 확인
  - 대시보드 화면의 로그데이터를 받아오는 시간때문에 화면에 표시되는데 수분이 소요될 수 있습니다.
    ![container_insights_dashboard](images/container_insights_dashboard.png)


### 장애 해결
실습에서 발생시킨 이슈는 Task에서 필요로하는 메모리가 EC2가 보유하고 있는 메모리보다 많기 때문에 발생하는 것이므로 Task를 가동할 EC2 인스턴스의 개수를 증가시킴으로써 해결할 수 있습니다. ECS환경에서는 *Scale ECS Instances* 기능을 통해 필요시 클러스터 운영에 필요로하는 EC2 인스턴스를 손쉽게 추가할 수 있습니다.
1. 탐색 창에서 클러스터를 선택하고 조정할 클러스터를 선택
2. *Cluster*에서 *ECS Instances* 선택후, *Scale ECS Instances* 확인
  ![container_insights_scale](images/container_insights_scale.png)
3. Desired number of instances(원하는 인스턴스 개수)의 경우 클러스터를 조정할 인스턴스 개수를 입력하고 Scale(확장)을 선택합니다.
* 참고: *Scale ECS Instances* 메뉴가 없을 경우, *auto scaling group* 메뉴를 통해 인스턴스 확장이 가능합니다. 해당 인스턴스는 *CloudFormation* 템플릿에 의해 자동으로 설정되어 생성되기 때문에 *Desired Capacity* 와 *Max* 만 원하는 값으로 수정하고 저장하면 자동으로 인스턴스가 생성됩니다.

## 결론
이번 실습을 통해 ECS의 서비스 및 Task를 모니터링할 수 있는 Container Insights에 대해 알아보았습니다. Container Insights는 CloudWatch에서 제공하는 컨테이너 모니터링 도구이기 때문에 하나의 모니터링 도구에서 기존 EC2 환경뿐 아니라 컨테이너까지 성능지표를 확인할 수 있게 합니다. 또한 CPU, 메모리, 네트워크 사용량, 스토리지 사용량, 컨테이너 사용 개수 등 다양한 지표를 기본으로 제공하기 때문에 편리하게 컨테이너 상태를 알아볼 수 있습니다.

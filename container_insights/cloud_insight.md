# ECS 환경에서 Container Insight 활용
## 기존 Amazon ECS 클러스터에서 Container Insights 설정
기존 Amazon ECS 클러스터에서 Container Insights를 활성화하려면 다음 명령을 입력합니다.

### ECS 클러스터 목록 확인
aws ecs list-clusters 명령을 통해 현재 클러스터 목록을 확인합니다.
``` shell
$ aws ecs list-clusters

{
    "clusterArns": [
        "arn:aws:ecs:ap-northeast-2:1111oooo1111:cluster/default",
        "arn:aws:ecs:ap-northeast-2:1111oooo1111:cluster/EcsLabPublicCluster"
    ]
}
```
#### Container Insight 활성화
aws ecs update-cluster-settings 명령을 통해 container Insights 기능을 해당 클러스터에 활성화 합니다.
``` shell
$ aws ecs update-cluster-settings --cluster EcsLabPublicCluster --settings name=containerInsights,value=enabled
{
    "cluster": {
        "clusterArn": "arn:aws:ecs:ap-northeast-2:1111oooo1111:cluster/EcsLabPublicCluster",
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

## Container Insights 지표 보기
Container Insights를 설정하여 지표를 수집하고 난 후에는 CloudWatch 자동 대시보드에서 이러한 지표를 볼 수 있습니다.

### Container Insight 사용 방법
  1. https://console.aws.amazon.com/cloudwatch/에서 CloudWatch 콘솔을 엽니다.
  2. 화면 왼쪽 상단에서 개요 옆의 아래쪽 화살표를 선택하고 Container Insights를 선택합니다.
    클러스터에 대한 지표를 보여주는 그래프가 몇 개 나타납니다. 그래프 아래의 클러스터 목록에는 각 클 러스터에 대해 상태 및 기본 지표가 표시됩니다. 특정 클러스터에 대해 보기를 필터링하려면 가운데 상단의 상자를 사용합니다.
    ![container_insights_menu](images/container_insights_menu.png)

  3. Clusters(클러스터)가 표시된 왼쪽 상단에서 모드를 바꿔가며 노드, Pod, 서비스, 작업 및 네임스페이스 수준의 지표를 확인합니다. 이때 개별 Pod 및 노드만 보도록 이러한 보기를 필터링할 수도 있습니다. 또한 Amazon EKS 지표와 Amazon ECS 지표 사이를 전환할 수 있습니다.
    ![container_insights_metric](images/container_insights_metric.png)
  4. 어떤 그래프에서든 범례 줄에서 멈춰 있으면 해당 리소스에 대한 자세한 정보를 확인할 수 있습니다.
  5. 대시보드에서 클러스터 중 하나에 관한 클러스터 수준의 로그를 보려면 화면 하단의 목록에서 해당 이름 옆에 있는 버튼을 선택합니다. 그런 다음 작업을 선택하고 목록에서 옵션 중 하나를 선택합니다. 새 브라우저가 나타나고 해당 리소스에 대한 CloudWatch Logs Insights 쿼리가 표시됩니다. 쿼리 실행을 선택합니다. 쿼리 결과가 표시됩니다. CloudWatch Logs Insights에 대한 자세한 내용은 CloudWatch Logs Insights로 로그 데이터 분석을 참조 하십시오.
    ![container_insights_query](images/container_insights_query.png)
  6. 노드, Pod 또는 작업 수준에서 페이지 하단의 목록에 현재 표시된 한 개 이상의 리소스에 관한 로그를 보 려면 해당 리소스의 이름 옆에 있는 확인란을 선택합니다. 그런 다음 작업을 선택하고 목록에서 옵션 중 하나를 선택합니다. 그러면 해당 리소스의 로그 또는 AWS X-Ray 추적을 볼 수 있습니다. 새 브라우저가 나타나고 요청한 정보가 표시됩니다.

## CloudWatch Logs Insights을 사용하여 Container Insights 데이터 보기
Container Insights는 CloudWatch Logs에 저장된 성능 로그 이벤트를 사용하여 지표를 수집합니다. 컨테이 너 데이터에 대한 추가 보기에서 CloudWatch Logs Insights 쿼리를 사용할 수 있습니다.
CloudWatch Logs Insights에 대한 자세한 내용은 CloudWatch Logs Insights로 로그 데이터 분석을 참조하십시오.

### CloudWatch Logs Insights 사용 방법
  1. https://console.aws.amazon.com/cloudwatch/에서 CloudWatch 콘솔을 엽니다.
  2. 왼쪽 탐색 창에서 Insights를 선택합니다.
  화면 상단 근처에 쿼리 편집기가 있습니다. CloudWatch Logs Insights를 처음으로 열면 이 상자에는 최 신 로그 이벤트 20개를 반환하는 기본 쿼리가 포함되어 있습니다.
  3. 쿼리 편집기 위의 상자에서 쿼리할 Container Insights 로그 그룹을 선택합니다. 작업할 다음 예제 쿼리 에서는 로그 그룹 이름이 performance로 끝나야 합니다.
    ![container_insights_performance](images/container_insights_performance.png)
  로그 그룹을 선택하면 CloudWatch Logs Insights가 로그 그룹 내 데이터에서 필드를 자동으로 검색하고 오른쪽 창에 있는 검색된 필드에 표시합니다. 또한 이 로그 그룹의 로그 이벤트를 시간의 흐름에 따라 보 여주는 막대 그래프도 표시합니다. 이 막대 그래프에서는 테이블에 표시된 이벤트뿐만 아니라 쿼리 및 시간 범위와 일치하는 로그 그룹 내 이벤트의 분포를 보여줍니다.

### 예제 쿼리
쿼리 편집기에서 기본 쿼리를 다음 쿼리로 바꾸고 쿼리 실행을 선택합니다.
  1. TaskFamily별 평균 CPU 사용량
  ```
  STATS avg(CpuUtilized) as avg_node_cpu_utilization by TaskDefinitionFamily
  | SORT avg_node_cpu_utilization DESC
  ```
  이 쿼리는 컨테이너 목록을 평균적인  CPU 이용률에 따라 정렬하여 보여줍니다.

  2. 클러스터당 EC2 사용 개수
  ```
  STATS avg(ContainerInstanceCount) as instance_count by ClusterName
  | SORT ClusterName desc
  ```
  3. 서비스당 컨테이너 개수
  ```
  stats avg(RunningTaskCount) as container_count by ServiceName
  ```

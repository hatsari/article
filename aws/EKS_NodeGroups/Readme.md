# Handling Nodegroups In EKS
- Date: 2020.05.09
- Writer: Kim, Yongki

This article simply describes the steps to add new node groups in EKS Cluster. Current node group would be comprised of spot instances, and new node group will have on-demand instances.

## Steps
### Check the current node labels
- identify current node group

``` shell
[ec2-user@ip-172-31-38-36 ~]$ eksctl get ng --cluster alex-kube
CLUSTER		NODEGROUP	CREATED			MIN SIZE	MAX SIZE	DESIRED CAPACITY	INSTANCE TYPE	IMAGE ID
alex-kube	spot-workers	2020-05-09T03:57:41Z	2		5		0			m4.large	ami-09212c30a346e9475
```

- Check the current labels of nodes
Look at the *lifecycle=spot* label.
``` shell
[ec2-user@ip-172-31-38-36 ~]$ kubectl get nodes --show-labels
NAME                                                STATUS   ROLES    AGE   VERSION               LABELS
ip-192-168-27-202.ap-northeast-2.compute.internal   Ready    <none>   92m   v1.15.11-eks-af3caf   alpha.eksctl.io/cluster-name=alex-kube,alpha.eksctl.io/instance-id=i-028c7c9858c409638,alpha.eksctl.io/nodegroup-name=spot-workers,beta.kubernetes.io/arch=amd64,beta.kubernetes.io/instance-type=m4.large,beta.kubernetes.io/os=linux,failure-domain.beta.kubernetes.io/region=ap-northeast-2,failure-domain.beta.kubernetes.io/zone=ap-northeast-2a,kubernetes.io/arch=amd64,kubernetes.io/hostname=ip-192-168-27-202.ap-northeast-2.compute.internal,kubernetes.io/os=linux,*lifecycle=spot*,topology.ebs.csi.aws.com/zone=ap-northeast-2a
ip-192-168-50-93.ap-northeast-2.compute.internal    Ready    <none>   92m   v1.15.11-eks-af3caf   alpha.eksctl.io/cluster-name=alex-kube,alpha.eksctl.io/instance-id=i-04de155170bb9e4c2,alpha.eksctl.io/nodegroup-name=spot-workers,beta.kubernetes.io/arch=amd64,beta.kubernetes.io/instance-type=m4.large,beta.kubernetes.io/os=linux,failure-domain.beta.kubernetes.io/region=ap-northeast-2,failure-domain.beta.kubernetes.io/zone=ap-northeast-2c,kubernetes.io/arch=amd64,kubernetes.io/hostname=ip-192-168-50-93.ap-northeast-2.compute.internal,kubernetes.io/os=linux,*lifecycle=spot*,topology.ebs.csi.aws.com/zone=ap-northeast-2c
[ec2-user@ip-172-31-38-36 ~]$ kubectl get nodes
```
- check the *lifecycle* labels
``` shell
[ec2-user@ip-172-31-38-36 ~]$ kubectl get nodes -L lifecycle
NAME                                                STATUS   ROLES    AGE   VERSION               LIFECYCLE
ip-192-168-27-202.ap-northeast-2.compute.internal   Ready    <none>   93m   v1.15.11-eks-af3caf   *spot*
ip-192-168-50-93.ap-northeast-2.compute.internal    Ready    <none>   93m   v1.15.11-eks-af3caf   *spot*
```

### Attache label to current nodes(if with no label)
To distinguish with new nodegroup, existing nodegroup should have *spot* label, if there is no label in nodes.
``` shell
kubectl label nodes --all 'lifecycle=spot'
```

### Create new nodegroup

- Configuration for new nodegroup is defined in *nodegroup-ondemand.yaml*file.
``` yaml
apiVersion: eksctl.io/v1alpha5
kind: ClusterConfig
metadata:
  name: alex-kube
  region: ap-northeast-2
managedNodeGroups:
  - name: ondemand-workers
    labels:
      lifecycle: ondemand
    minSize: 2
    maxSize: 5
    instanceType: t3.medium
    desiredCapacity: 3
```

- *eksctl* command will create new nodegroup referring with *nodegroup-ondemand.yaml*
``` shell
[ec2-user@ip-172-31-38-36 new_nodegroup]$ eksctl create nodegroup -f nodegroup-ondemand.yaml
[ℹ]  eksctl version 0.18.0
[ℹ]  using region ap-northeast-2
[ℹ]  will use version 1.15 for new nodegroup(s) based on control plane version
...
...
[✔]  created 1 managed nodegroup(s) in cluster "alex-kube"
[ℹ]  checking security group configuration for all nodegroups
[ℹ]  all nodegroups have up-to-date configuration
```

- Confirm the new nodegroups

``` shell
[ec2-user@ip-172-31-38-36 new_nodegroup]$ eksctl get ng --cluster alex-kube
CLUSTER		NODEGROUP		CREATED			MIN SIZE	MAX SIZE	DESIRED CAPACITY	INSTANCE TYPE	IMAGE ID
alex-kube	ondemand-workers	2020-05-09T11:48:34Z	2		5		3			t3.medium
alex-kube	spot-workers		2020-05-09T03:57:41Z	2		5		0			m4.large	ami-09212c30a346e9475
```

- Check *lifecycle* label of all nodes

``` shell
[ec2-user@ip-172-31-38-36 new_nodegroup]$ kubectl get no -L lifecycle
NAME                                                STATUS   ROLES    AGE     VERSION               LIFECYCLE
ip-192-168-27-202.ap-northeast-2.compute.internal   Ready    <none>   7h52m   v1.15.11-eks-af3caf   spot
ip-192-168-31-157.ap-northeast-2.compute.internal   Ready    <none>   5m17s   v1.15.10-eks-bac369   ondemand
ip-192-168-49-209.ap-northeast-2.compute.internal   Ready    <none>   5m22s   v1.15.10-eks-bac369   ondemand
ip-192-168-50-93.ap-northeast-2.compute.internal    Ready    <none>   7h52m   v1.15.11-eks-af3caf   spot
ip-192-168-94-55.ap-northeast-2.compute.internal    Ready    <none>   5m21s   v1.15.10-eks-bac369   ondemand
```

- ref: https://eksctl.io/usage/eks-managed-nodes/

### Re-apply deployment by selector
- Confirm the all pods working on "lifecycle=spot" nodes, looking at ip address of nodes

``` shell
[ec2-user@ip-172-31-38-36 new_nodegroup]$ kubectl get po -o wide | sort -k 8
NAME                                 READY   STATUS    RESTARTS   AGE     IP               NODE                                                NOMINATED NODE   READINESS GATES
ecsdemo-frontend-7f4cdcc849-mh2lh    1/1     Running   0          7h53m   192.168.44.90    ip-192-168-50-93.ap-northeast-2.compute.internal    <none>           <none>
ecsdemo-frontend-7f4cdcc849-zfxns    1/1     Running   0          7h53m   192.168.61.55    ip-192-168-50-93.ap-northeast-2.compute.internal    <none>           <none>
nginx-789c9c76c8-bzfld               1/1     Running   0          6h38m   192.168.32.35    ip-192-168-50-93.ap-northeast-2.compute.internal    <none>           <none>
tomcat-deployment-56497cf847-dngqd   1/1     Running   0          7h53m   192.168.38.95    ip-192-168-50-93.ap-northeast-2.compute.internal    <none>           <none>
tomcat-deployment-56497cf847-p5zsd   1/1     Running   0          7h54m   192.168.46.205   ip-192-168-50-93.ap-northeast-2.compute.internal    <none>           <none>
ecsdemo-frontend-7f4cdcc849-6mdc9    1/1     Running   0          7h53m   192.168.10.201   ip-192-168-27-202.ap-northeast-2.compute.internal   <none>           <none>
tomcat-deployment-56497cf847-jdpjz   1/1     Running   0          7h54m   192.168.18.63    ip-192-168-27-202.ap-northeast-2.compute.internal   <none>           <none>
```

- Modify *nodeselector* of the deployment file([ondemand-deployment](ondemand-tomcat-deployment.yaml)) to choose the *ondemand* label nodes

``` yaml
apiVersion: extensions/v1beta1
kind: Deployment
metadata:
  name: "tomcat-deployment"
  namespace: "default"
spec:
  replicas: 3
  template:
    metadata:
      labels:
        app: "tomcat-alex"
    spec:
      containers:
      - image: 253679086765.dkr.ecr.ap-northeast-2.amazonaws.com/eks-tomcat:latest
        imagePullPolicy: Always
        name: "tomcat-alex"
        ports:
        - containerPort: 8080
      nodeSelector:
        lifecycle: ondemand
```

- re-deploy *ondemand-tomcat-deployment.yaml*
``` shell
[ec2-user@ip-172-31-38-36 new_nodegroup]$ kubectl apply -f ondemand-tomcat-deployment.yaml
deployment.extensions/tomcat-deployment configured
```

- monitor re-deployment

``` shell
[ec2-user@ip-172-31-38-36 new_nodegroup]$ kubectl get po -o wide
NAME                                 READY   STATUS              RESTARTS   AGE     IP               NODE                                                NOMINATED NODE   READINESS GATES
ecsdemo-frontend-7f4cdcc849-6mdc9    1/1     Running             0          8h      192.168.10.201   ip-192-168-27-202.ap-northeast-2.compute.internal   <none>           <none>
ecsdemo-frontend-7f4cdcc849-mh2lh    1/1     Running             0          8h      192.168.44.90    ip-192-168-50-93.ap-northeast-2.compute.internal    <none>           <none>
ecsdemo-frontend-7f4cdcc849-zfxns    1/1     Running             0          8h      192.168.61.55    ip-192-168-50-93.ap-northeast-2.compute.internal    <none>           <none>
nginx-789c9c76c8-bzfld               1/1     Running             0          6h46m   192.168.32.35    ip-192-168-50-93.ap-northeast-2.compute.internal    <none>           <none>
tomcat-deployment-56497cf847-dngqd   0/1     Terminating         0          8h      192.168.38.95    ip-192-168-50-93.ap-northeast-2.compute.internal    <none>           <none>
tomcat-deployment-56497cf847-jdpjz   1/1     Running             0          8h      192.168.18.63    ip-192-168-27-202.ap-northeast-2.compute.internal   <none>           <none>
tomcat-deployment-56497cf847-p5zsd   1/1     Running             0          8h      192.168.46.205   ip-192-168-50-93.ap-northeast-2.compute.internal    <none>           <none>
tomcat-deployment-5785794b45-7fqgs   0/1     ContainerCreating   0          6s      <none>           ip-192-168-31-157.ap-northeast-2.compute.internal   <none>           <none>
tomcat-deployment-5785794b45-sxchz   0/1     ContainerCreating   0          6s      <none>           ip-192-168-49-209.ap-northeast-2.compute.internal   <none>           <none>

[ec2-user@ip-172-31-38-36 new_nodegroup]$ sleep 5

[ec2-user@ip-172-31-38-36 new_nodegroup]$ kubectl get po -o wide | sort -k 8
NAME                                 READY   STATUS    RESTARTS   AGE     IP               NODE                                                NOMINATED NODE   READINESS GATES
ecsdemo-frontend-7f4cdcc849-mh2lh    1/1     Running   0          8h      192.168.44.90    ip-192-168-50-93.ap-northeast-2.compute.internal    <none>           <none>
ecsdemo-frontend-7f4cdcc849-zfxns    1/1     Running   0          8h      192.168.61.55    ip-192-168-50-93.ap-northeast-2.compute.internal    <none>           <none>
nginx-789c9c76c8-bzfld               1/1     Running   0          6h47m   192.168.32.35    ip-192-168-50-93.ap-northeast-2.compute.internal    <none>           <none>
tomcat-deployment-5785794b45-8r9hn   1/1     Running   0          18s     192.168.87.134   ip-192-168-94-55.ap-northeast-2.compute.internal    <none>           <none>
ecsdemo-frontend-7f4cdcc849-6mdc9    1/1     Running   0          8h      192.168.10.201   ip-192-168-27-202.ap-northeast-2.compute.internal   <none>           <none>
tomcat-deployment-5785794b45-7fqgs   1/1     Running   0          30s     192.168.2.73     ip-192-168-31-157.ap-northeast-2.compute.internal   <none>           <none>
tomcat-deployment-5785794b45-sxchz   1/1     Running   0          30s     192.168.35.185   ip-192-168-49-209.ap-northeast-2.compute.internal   <none>           <none>
```

### Another resources
- ondemand nodegroup configuration file: [nodegroup-ondemand.yaml](nodegroup-ondemand.yaml)
- spot nodegroup-ondemand configuration file: [nodegroup-spot.yaml](nodegroup-spot.yaml)
- ondemand deployment file: [ondemand-tomcat-deployment.yaml](ondemand-tomcat-deployment.yaml)
- spot deployment file: [spot-frontend-deployment.yaml](spot-frontend-deployment.yaml)

### Useful commands
- add a taint a node
```kubectl taint nodes node1 spotInstance=true:PreferNoSchedule```
- remove a taint from a node
```kubectl taint nodes node1 spotInstance:PreferNoSchedule-```
- evict pods from a node
```kubectl drain $NODE_NAME```
- mark a node unschedulable
```kubectl cordon $NODE_NAME```
- mark a node schedulable
```kubectl uncordon $NODE_NAME```

## References
- eksworkshop: https://eksworkshop.com/beginner/150_spotworkers/workers/
- docs.aws for spot instance: https://aws.amazon.com/ko/premiumsupport/knowledge-center/eks-multiple-node-groups-eksctl/

# EKS Install & Configuration Guide
- Date: 2020.04.30
- Writer: Yongki Kim (kyongki)
- ref: https://docs.aws.amazon.com/eks/latest/userguide/getting-started-eksctl.html
## pre-requsite
- awscli
- eksctl
## cluster installation
### preparing keypair
- create key pair
- retrieving pub key
```shell
ssh-keygen -y -f .ssh/alex-eks-key.pem
```
### creating kube cluster
```shell
eksctl create cluster \
--name alex-kube \
--region ap-northeast-2 \
--nodegroup-name standard-workers \
--node-type t3.medium \
--nodes 3 \
--nodes-min 1 \
--nodes-max 4 \
--ssh-access \
--ssh-public-key alex-eks-public-key.pub \
--managed
```

### verifing cluster
- kubectl get nodes
- kubectl get pods

### deploying simple pod
- deployment file
```shell
~/eks_environment/tomcat_container $ cat tomcat-deployment.yaml	
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

- deploy tomcat app
```shell
kubectl apply -f tomcat-deployment.yaml
```

- verifying pods
```shell
~/eks_environment/tomcat_container $ kubectl get pods
NAME                                 READY   STATUS    RESTARTS   AGE
tomcat-deployment-57c946c448-8d2hd   1/1     Running   0          9m4s
tomcat-deployment-57c946c448-wzwxh   1/1     Running   0          9m4s
tomcat-deployment-57c946c448-zvmm8   1/1     Running   0          9m4s

~/eks_environment/tomcat_container $ kubectl get svc
NAME         TYPE        CLUSTER-IP   EXTERNAL-IP   PORT(S)   AGE
kubernetes   ClusterIP   10.100.0.1   <none>        443/TCP   22m
```

### ingress controller
- ref: https://aws.amazon.com/blogs/opensource/kubernetes-ingress-aws-alb-ingress-controller/

#### deploy the relevant RBAC roles and role bindings as required by the AWS ALB Ingress controller
kubectl apply -f https://raw.githubusercontent.com/kubernetes-sigs/aws-alb-ingress-controller/v1.1.6/docs/examples/rbac-role.yaml

#### create an IAM policy named ALBIngressControllerIAMPolicy to allow the ALB Ingress controller to make AWS API calls on your behalf
aws iam create-policy \
    --policy-name ALBIngressControllerIAMPolicy \
    --policy-document https://raw.githubusercontent.com/kubernetes-sigs/aws-alb-ingress-controller/v1.1.6/docs/examples/iam-policy.json

#### set PolicyARN, get from previous command
export PolicyARN="......."

#### enable IAM OIDC provider
eksctl utils associate-iam-oidc-provider --region=ap-northeast-2 --cluster=alex-kube --approve

#### create a Kubernetes service account and an IAM role
create iamserviceaccount \
       --cluster=alex-kube \
       --namespace=kube-system \
       --name=alb-ingress-controller \
       --attach-policy-arn=$PolicyARN
       --override-existing-serviceaccounts \
       --approve

#### deploy alb-ingress-controller
curl -sS "https://raw.githubusercontent.com/kubernetes-sigs/aws-alb-ingress-controller/v1.1.6/docs/examples/alb-ingress-controller.yaml" \
     | sed "s/# - --cluster-name=devCluster/- --cluster-name=alex-kube/g" \
     | kubectl apply -f -

#### verify that the deployment was successful and the controller started
kubectl logs -n kube-system $(kubectl get po -n kube-system | egrep -o alb-ingress[a-zA-Z0-9-]+)

### apply to tomcat-alex
### check pod
kubectl exec -it tomcat-deployment-57c946c448-8d2hd -- /bin/bash

#### enable service
kubectl apply -f tomcat-service.yaml
```shell
[ec2-user@ip-172-31-38-36 tomcat_container]$ cat tomcat-service.yaml
apiVersion: v1
kind: Service
metadata:
  name: "tomcat-alex"
  namespace: "default"
spec:
  ports:
    - port: 80
      targetPort: 8080
      protocol: TCP
  type: NodePort
  selector:
    app: "tomcat-alex"
```
#### enable ingress controller
kubectl apply -f tomcat-ingress.yaml
```shell
[ec2-user@ip-172-31-38-36 tomcat_container]$ cat tomcat-ingress.yaml
apiVersion: extensions/v1beta1
kind: Ingress
metadata:
  name: "tomcat-alex"
  namespace: "default"
  annotations:
    kubernetes.io/ingress.class: alb
    alb.ingress.kubernetes.io/scheme: internet-facing
    alb.ingress.kubernetes.io/target-type: ip # ip | instance
  labels:
    app: tomcat-alex
spec:
  rules:
    - http:
        paths:
          - path: /*
            backend:
              serviceName: "tomcat-alex"
              servicePort: 80
```

## Confirm ALB creation 
### get dns 
```shell
[ec2-user@ip-172-31-38-36 tomcat_container]$ kubectl get ingress
NAME          HOSTS   ADDRESS                                                                      PORTS   AGE
tomcat-alex   *       f9f575ad-default-tomcatale-3618-923358832.ap-northeast-2.elb.amazonaws.com   80      93m
```
### access via broswer
```shell
c2-user@ip-172-31-38-36 tomcat_container]$ curl f9f575ad-default-tomcatale-3618-923358832.ap-northeast-2.elb.amazonaws.com/ip.jsp
<p>Remote Addr: 192.168.86.193</p><p>Remote Host: 192.168.86.193</p><p>X-Forwarded-For: 13.209.15.15</p>
```

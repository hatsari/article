# Container, ECR, and EKS workshop
- date: 2020.04.20
- writer: hatsari, Kim Yongki
## Test Environment
- kubernetes cluster: EKS on AWS
- image: tomcat

## Steps
### creating sample container
1. create base tomcat container
``` shell
node1$  docker pull tomcat
node1$  docker run -i -d -t -p 8080:8080 --name tomcat tomcat
node1$  docker ps
CONTAINER ID        IMAGE               COMMAND             CREATED             STATUS              PORTS                    NAMES
37b3406bef28        tomcat              "catalina.sh run"   10 seconds ago      Up 9 seconds        0.0.0.0:8080->8080/tcp   tomcat
```

2. make ip.jsp file and move to container
``` shell
node1$ cat << EOF > ip.jsp
> <%
> out.print("<p>LocalHost Addr: " + request.getLocalAddr() + "</p>");
> out.print("<p>Remote Addr: " + request.getRemoteAddr() + "</p>");
> out.print("<p>Remote Host: " + request.getRemoteHost() + "</p>");
> out.print("<p>X-Forwarded-For: " + request.getHeader("x-forwarded-for") + "</p>");
> %>
> EOF
node1$ sudo docker exec -i -t 37b3406bef28 /bin/sh
# mkdir webapps/ROOT
# exit

node1$  docker cp ip.jsp tomcat:/usr/local/tomcat/webapps/ROOT/
node1$ curl http://localhost:8080/ip.jsp
<p>Remote Addr: 172.17.0.1</p><p>Remote Host: 172.17.0.1</p><p>X-Forwarded-For: null</p>
```

3. create new image with tag
``` shell
node1$  docker commit tomcat tomcat-alex
```

4. validate new image

``` shell
node1$  docker stop tomcat
node1$  docker run -d -i -t -p 8080:8080 tomcat-alex
node1$ docker ps
CONTAINER ID        IMAGE               COMMAND             CREATED             STATUS              PORTS                    NAMES
5d5bc4c90e14        tomcat-alex         "catalina.sh run"   4 seconds ago       Up 4 seconds        0.0.0.0:8080->8080/tcp   lucid_borg
node1$ curl http://localhost:8080/ip.jsp
<p>Remote Addr: 172.17.0.1</p><p>Remote Host: 172.17.0.1</p><p>X-Forwarded-For: null</p>
node1$ docker stop 5d5bc4c90e14
```
#### ref:
- how to create TOMCAT container: https://sarc.io/index.php/tomcat/1290-docker-tomcat-install
- jsp to identify ip address: https://linuxism.ustd.ip.or.kr/810
### Uploading to ECR
1. Retrieve an authentication token and authenticate your Docker client to your registry.
``` shell
aws ecr get-login-password --region [region] | docker login --username AWS --password-stdin [your-account].ecr.[region].amazonaws.com/eks-tomcat
```

2. tag your image so you can push the image to this repository
``` shell
docker tag tomcat-alex [your-account].ecr.[region].amazonaws.com/eks-tomcat:latest
```

### Creating tomcat pod
1. create deployment file
``` shell
[ec2-user@tomcat_container]$ cat tomcat-deployment.yaml
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
```

2. apply tomcat-deployment
``` shell
[ec2-user@ip-172-31-38-36 tomcat_container]$ kubectl apply -f tomcat-deployment.yaml
deployment.extensions/tomcat-deployment create
```

3. confirm pods running
``` shell
[ec2-user@ip-172-31-38-36 tomcat_container]$ kubectl get pods
NAME                                 READY   STATUS              RESTARTS   AGE
nginx                                1/1     Running             0          51d
tomcat-deployment-5795c57fc9-h2mk4   0/1     ContainerCreating   0          8s
tomcat-deployment-5795c57fc9-kvjsx   0/1     ContainerCreating   0          8s
tomcat-deployment-5795c57fc9-rrdv6   0/1     ContainerCreating   0          8s
```
### alb-ingress-controller with ip mode
1. create service for tomcat

``` shell
[ec2-user@ip-172-31-38-36 tomcat_container]$ cat tomcat-service.yaml
apiVersion: v1
kind: Service
metadata:
  name: "tomcat-alex"
  namespace: "default"
spec:
  ports:
    - port: 8080
      targetPort: 8080
      protocol: TCP
  type: NodePort
  selector:
    app: "tomcat-alex"
```

4. troubleshooting alb creating
``` shell
kubectl logs -n kube-system   deployment.apps/alb-ingress-controller
```

#### ref:
- https://aws.amazon.com/premiumsupport/knowledge-center/eks-alb-ingress-controller-fargate/?nc1=h_ls
- alb-ingress-controller: https://aws.amazon.com/blogs/opensource/kubernetes-ingress-aws-alb-ingress-controller/
- dns issue: https://github.com/kubernetes-sigs/aws-alb-ingress-controller/issues/819


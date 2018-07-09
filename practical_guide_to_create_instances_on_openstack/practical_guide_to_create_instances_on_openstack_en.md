# Practical Guide to Create Instances on Openstack
Date: 2018. 07. 09

When you create instances on openstack, you can use ansible, though its instance creation are serial, not parallel, one by one. So I made these playbook code which is creating several instances simutaeoulsy and verifing the creation. These codes provide below functions.

  - Spawning Instances Simutaneously
  - Verifing Creation of Instances
  - Checking Enablement of SSH port

Detailed code and description is here

## Spawning Instances Simutaneously
Basically ansible creates instances one by one. Even though working in the **loop**, instance is generated in serial. so to reduce the creation time of instances, we have to use **async** directive. Look at below codes. **async: 120** and **poll: 0** is the right part to spawn all instances same time. especially focus on **poll: 0**, this means the task don't verify whether instances create successfully or not. Just run and don't care about it.

```yaml
# tasks file for openstack-instance
- name: Create a server instance
  os_server:
    auth: "{{ os_auth }}"
    name: "{{ instance_name }}{{ item }}"
    image: wwd_rhel
    meta: "group={{ group }},deployment_name={{ deployment }}"
    flavor: m2.small_generated_by_ansible
    security_groups: "{{ security_group_name }}"
    auto_ip: "{{ floating_answer }}"
    key_name: ansible_ssh
    wait: yes
    nics:
    - net-name: "{{ vm_nic }}"
  register: newnodes
  async: 120
  poll: 0
  with_sequence: start=1 end="{{ count }}"
```

With above codes, we don't know the result. so we have to make some verification code to find out the status of instances. that part is next.

## Verifing Creation of Instances
In this codes, I used **role** to create instances so it make me create many different purposed instances like **web**, **was** and **db** using different variable files. Important code is the second task. **async_status** directive can verify the status of instances. When I created instances, I saved the result with **register**. The saved variable is **newnodes**. Then, I checked the status with **ansible_job_id**. If we don't check that the creation job is finished or not, we may get failed next task like installing application or modifing system parameters. So after using **async** in ansible, we always have to check the status of job separately.   

```yaml
  tasks:
  - name: Create {{ item }} Instances
    include_role:
       name: openstack-instance
       vars_from: "{{ item }}.yaml"
    with_items:
      - web
      - was
      - db

  - name: Waiting for role includes to complete
    async_status:
      jid={{ newnodes['results'][0]['ansible_job_id'] }}
    register: my_async_job_status
    until: my_async_job_status.finished
    retries: 20

  - name: gather instance facts
    os_server_facts:
      auth: "{{ os_auth }}"
      server: db*
    register: result
```
In addtion, I just verified about last instance's creation. Though checking all instances is the best approach, I didn't do that, bleame my laziness ^^;;.
after completing the second task, I added the 3rd task to gather the information of instance. with this fact information, I will find the ip address for the next part.
## Checking Enablement of SSH port
Last job is to check the ssh port. We have to use ssh connection to modify the instances, just creating the instance is not enough for ansible, more things should be done with it. Normally OS booting takes a few mininutes but ansible don't wait for it, so we have to put some code to check the ssh connection. **wait_for** directive is good for checking the status. With **search_regx: OpenSSH**, we can know the readiness of ssh, so we can move forward. As you know, without ssh connection, we will fail in next task.
```yaml
  - name: Wait for Last Instance to be available
    wait_for:
      host: "{{ openstack_servers[0]['accessIPv4'] }}"
      port: 22
      search_regex: OpenSSH
      timeout: 300
    delegate_to: "{{ inventory_hostname }}"

```
In this code, **inventory_hostname** means **localhost**, so **localhost** try to connect to instances. I quoted this code from **ansible_doc wait_for**.
## Conclusion
On OpenStack or AWS or AZURE or GCP and any other cloud or virtualization environment, if you want to use ansible to create instances, it would be better to use **async**, **async_status** and **wait_for**. With these directives, you can create instances simutaneously and you can reduce much wasting-time.
Have good IAC time.

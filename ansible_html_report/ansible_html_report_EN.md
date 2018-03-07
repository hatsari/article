# ansible 작업 결과를 HTML 표로 출력하는 방법
# A Way of Creating HTML Formatter to Print The Result of Ansible
Normally, ansible is used to do system operation, but it can be useful to gather all your system information as well. At this time, if the result is a html table, it would be better to read. So I will explain how ansible makes "simple html file" using "Template".

_Operation Summary_
  - register the variable to want to print.
  - create jinja2 file as html mockup
  - generate html file using template module

## Target Host (inventory file)
filename: inven.txt
```
[vagrant@ansible-tower playbook]$ cat inven.txt

[vms]
v2 ansible_ssh_host=172.28.128.4
v3 ansible_ssh_host=172.28.128.5
```

## Playbook to gather system information
Below is the playbook example which gathers system information and generate html file.
"HOSTNAME", "CPU", "MEMORY", "DISK_PARTITION" items will be the column name and the inventory group defined as "vms" consists of two hosts, 'v2' and 'v3'.
Then, seeing the playbook example, let me explain each task in detail.

playbook filename: gather_info.yml
```
---
- name: gather system information
  hosts: vms
  vars:
    - title: "Automated Gathered System Information"
    - cols:
      - "HOSTNAME"
      - "CPU"
      - "MEMORY"
      - "DISK_PARTITION"

  tasks:
    - name: print hostname
      debug:
        var: ansible_hostname
    - name: gather df info
      shell: df | grep sda
      register: info_df
    - name: set info_df
      set_fact:
        info_df: "{{ info_df.stdout_lines }}"
    - name: create html report
      template:
        src: report.html.j2
        dest: /home/vagrant/playbook/result.html
      delegate_to: 127.0.0.1
      run_once: yes
```

### "print hostname" task
Verify *ansible_hostname* variable to confirm the fact operation. 

### "gather df info" task
Using shell module, gather the disk information of 'v2' and 'v3' hosts. And it saves the result into *info_df* with *register*. This task can be switched with any other one depending on what you wish to present. It is important to save the value with *register*.

### "set info_df" task
With *set_fact* module, define the *info_df* variable to use it on other host.

### "create html report" task
Generate html file with *template* module. the filename of template is *report.html.j2* and this file is the mockup of *result.html*. Also I used *delegate_to* to execute the task on localhost. There is no need to run it several times so I added *run_once: yes*.

## Template File
Template of ansibe has jinja2 format and it is very useful to create contents of file dynamically, so I also used it. Let's see the template file in detail.

template filename: report.html.j2

```
<html>

<h1> Title: {{ title }} </h1>

<table border=1>
<TR>
{% for col in cols %}
   <TD class="c1"><SPAN> {{ col }} </SPAN></TD>
{% endfor %}
</TR>

{% for host in ansible_play_hosts %}
<TR>
   <TD class="c1"><SPAN> {{ hostvars[host]["ansible_hostname"] }} </SPAN></TD>
   <TD class="c2"><SPAN> {{ hostvars[host]["ansible_processor_cores"] }} </SPAN></TD>
   <TD class="c3"><SPAN> {{ hostvars[host]["ansible_memtotal_mb"] }} </SPAN></TD>
   <TD class="c4"><SPAN> {{ hostvars[host]["info_df"] }} </SPAN></TD>
</TR>
{% endfor %}

</table>

</html>
```

### Adding Title
Show the title with *title* variable. This variable is defined on *gather_info.yml*.

### Printing The Column Name
Print the column name on the top of table looping the *cols* variable

### Printing The System Information of Each Host
*ansible_play_hosts* is an ansible's magic variable. this shows the all hosts running in play. As looping the each hosts' variables(hostname, CPU, Memory, Disk info), the generated file can show the result on table format.

## Playbook Execution
You can execute the playbook like below.

```
#ansible-playbook -i inven.txt gather_info.yml
```

Here is the output of execution.

![cmd_result](cmd_result.jpg)

## Dynamically Generated HTML File
Below is the contents of html file.

filename: result.html

```
<html>
Title: Automated Gathered System Information
<table>
<TR>
   <TD class="c1"><SPAN> HOSTNAME </SPAN></TD>
   <TD class="c1"><SPAN> CPU </SPAN></TD>
   <TD class="c1"><SPAN> MEMORY </SPAN></TD>
   <TD class="c1"><SPAN> DISK_PARTITION </SPAN></TD>
</TR>


<TR>
   <TD class="c1"><SPAN> v2 </SPAN></TD>
   <TD class="c2"><SPAN> 1 </SPAN></TD>
   <TD class="c3"><SPAN> 992 </SPAN></TD>
   <TD class="c4"><SPAN> [u'/dev/sda1       41152736 1230456  37808796   4% /'] </SPAN></TD>
</TR>

<TR>
   <TD class="c1"><SPAN> v3 </SPAN></TD>
   <TD class="c2"><SPAN> 1 </SPAN></TD>
   <TD class="c3"><SPAN> 993 </SPAN></TD>
   <TD class="c4"><SPAN> [u'/dev/sda1       41152736    895464  38143788   3% /'] </SPAN></TD>
</TR>

</table>

</html>
```

### HTML Result 
![html_result](html_result.jpg)


## Conclusion
Presenting the output in HTML format makes people read it easily and if you add *mail* module in the playbook, other administrator or yourself is possible to confirm the task result with more better and readable view.
Finally, give up the beautiful table format from me. It is beyong my ability. 

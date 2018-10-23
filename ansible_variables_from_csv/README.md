# Set ansible facts from csv file
Customer requested me to import variables from csv file in ansible playbook. \\
using csvfile module and with_lines, I solved the problem.

# sample csv file
Below is sample csv format for test. \\
File name: csv.txt
``` 
key1, value1
key2, value2
key3, value3
key4, value4
key5, value5
```

# Playbook file
This playbook will import variables from csv file. \\
File name: get_fact.yaml
``` yaml
---
- name: set fact from csv
  hosts: localhost
  vars:
    csv_filename: csv.txt
  tasks:
    - name: set variables
      set_fact:
        "{{ lookup('csvfile', item + ' file=' + csv_filename + ' col=0 delimiter=,') }}": "{{ lookup('csvfile', item + ' file=' + csv_filename + ' col=1 delimiter=,') }}"
      with_lines: /usr/bin/awk -F',' '!/^#/ && !/^$/ { print $1 }' {{ csv_filename}}
    - name: debug var
      debug:
        var: key1
```

# Execute playbook
``` sh
ansible-playbook get_fact.yaml -v

PLAY [set fact from csv] *********************************************************************************************************************************************************

TASK [Gathering Facts] ***********************************************************************************************************************************************************
ok: [localhost]

TASK [set variables] *************************************************************************************************************************************************************
ok: [localhost] => (item=key1) => {"ansible_facts": {"key1": " value1"}, "ansible_facts_cacheable": false, "changed": false, "item": "key1"}
ok: [localhost] => (item=key2) => {"ansible_facts": {"key2": " value2"}, "ansible_facts_cacheable": false, "changed": false, "item": "key2"}
ok: [localhost] => (item=key3) => {"ansible_facts": {"key3": " value3"}, "ansible_facts_cacheable": false, "changed": false, "item": "key3"}
ok: [localhost] => (item=key4) => {"ansible_facts": {"key4": " value4"}, "ansible_facts_cacheable": false, "changed": false, "item": "key4"}
ok: [localhost] => (item=key5) => {"ansible_facts": {"key5": " value5"}, "ansible_facts_cacheable": false, "changed": false, "item": "key5"}

TASK [debug var] *****************************************************************************************************************************************************************
ok: [localhost] => {
    "key1": " value1"
}

PLAY RECAP ***********************************************************************************************************************************************************************
localhost                  : ok=3    changed=0    unreachable=0    failed=0
```

# Conclusion
You can set many number of variables now!!




- [인프라와 자동화에 대한 소견](thought_about_IT_infra_and_automation.md)
- [Infrastructure as a code 가 무엇이며, 왜 써야 하는가?](1.what_is_infrastructure_as_a_code.md)
- [번역-클라우드 인프라스트럭쳐 맛있게 굽기](2.Baking_delicious_cloud_instances.md)
- [Ansible Tower - RestAPI를 통해 Playbook 실행하는 방법](ansible_tower-running_template_via_restapi/ansible_tower-running_template_via_restapi.md)
- [EN-Ansible Tower - How to Run Job Template via Rest API](ansible_tower-running_template_via_restapi/en-ansible_tower-running_template_via_restapi.md)
- [불변의_인프라스트럭처_소개](An_introduction_to_immutable_infrastructure.md)
- [앤서블을 통한 네트워크 설정 자동화](AUTOMATING_NETWORK_DEVICES_WITH_ANSIBLE.md)
- [Simple Git Tutorial](how_to_use_git/git_usage_20180113.org)


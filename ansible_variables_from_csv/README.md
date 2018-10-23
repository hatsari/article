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

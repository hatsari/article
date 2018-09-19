# Dictionary Type Variable in Ansible

## Normal Variable
ansible 에서 변수는 보통 list 형식으로 선언합니다.

most of variables in ansible are defined in list type.

```
vars:
  - apple
  - orange
  - banana
```
하지만 변수가 하나가 아닌 여러개를 묶어서 사용하고 싶을 때가 있습니다. 가령 파일을 복제할 때, 파일마다 다른 위치(src)의 파일을 다른 디렉토리(dest)로 지정하고 싶을 때가 있습니다.
이를 그냥 ansible 로 구현하면 다음과 같이 task를 각각 분리해서 만들어야 합니다.

Sometimes we have to put many variable in one variable to access it easily. For example, when copying file from different source to different destinaton, how will you deal withit?
without headache, you can make playbook with seperated task.

```
tasks:
  - name: copy file1 to src_file_dir1 to dest_file_dir1
    copy:
	  name: file1
	  src: src_file_dir1
	  dest: dest_file_dir1
  - name: copy file2 to src_file_dir2 to dest_file_dir2
    copy:
	  name: file2
	  src: src_file_dir2
	  dest: dest_file_dir2
  - name: copy file1 to src_file_dir3 to dest_file_dir3
    copy:
	  name: file3
	  src: src_file_dir3
	  dest: dest_file_dir3
```

이와 같은 방식은 동일한 task가 세 번이나 사용되기 때문에 보기 좋치 않다. 3번은 그렇다쳐도 5번 이상 넘어가면 쓸데없이 길어지는 문제가 있다.

same tasks duplicates 3 times. it works absolutely but not good to see, not good to maintain.

## Dictionary Variable
dictionary variable은 하나의 변수에 key/value 방식으로 여러개의 변수를 지정할 수 있게 한다. 아래 예제는 list 형식과 dic 형식이 혼합된 것이긴 하지만 플레이북을 훨씬 간결하게 만들 수 있다. 예제에서는 copy 모듈이 아닌 debug 모듈로 각 변수들이 어떻게 출력되는 가를 확인 할 수 있다. 또한 with_items 로 반복문을 사용할 수 있게되어 가독성이 훨씬 좋아지고 작업도 하나로 완료되게 되었다.

Dictionary variable can have multiple key/value variable. Even though below example comprises of list type and dic type, this code can restain code very concise and readable.
Below code is not using copy module to verify the each value. Before applying the real code, put in the debug module. This habit always help you to escape the error. 

playbook name: debug_variable.yml
```
---
- name: test of dictionary variables
  hosts: localhost
  vars:
    - target1:
        file: copy_file1
        src: src_file1
        dest: dest_file1
    - target2:
        file: copy_file2
        src: src_file2
        dest: dest_file2
    - target3:
        file: copy_file3
        src: src_file3
        dest: dest_file3
  tasks:
    - name: print each file ans src and dest
      debug:
        msg: "{{ item.file}} is copied from {{ item.src }} to {{ item.dest }}"
      with_items:
        - "{{ target1 }}"
        - "{{ target2 }}"
        - "{{ target3 }}"
```

## Practical Code
실제 파일을 복제하는 플레이북 코드는 아래와 같다.

Below is the real code to copy multi files from different each source to different each destination.

playbook name: copy_multi_file.yml
```
---
- name: test of dictionary variables
  hosts: localhost
  vars:
    - target1:
        file: copy_file1
        src: src_file1
        dest: dest_file1
    - target2:
        file: copy_file2
        src: src_file2
        dest: dest_file2
    - target3:
        file: copy_file3
        src: src_file3
        dest: dest_file3
  tasks:
    - name: print each file ans src and dest
      debug:
        msg: "{{ item.file}} is copied from {{ item.src }} to {{ item.dest }}"
      with_items:
        - "{{ target1 }}"
        - "{{ target2 }}"
        - "{{ target3 }}"
```

## Conclusion
모든 프로그래밍 언어가 그렇듯이 변수를 잘 다루면 작업이 엄청 편해진다. 

As like any other programming language, much more knowledge about variable makes you easy to work.

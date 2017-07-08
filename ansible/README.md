1. 采用 [Ansible](http://docs.ansible.com/) 来控制远程 Server、部署项目等。 

```
2. 配置 Server 相关设置，拉取代码，部署应用：
```sh
ansible-playbook -i inventory/root deploy_cookbook.yml
```
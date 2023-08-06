# serf-plugin-handler
A Serf event handler that uses a plugin scheme

Sometimes you need to invoke mutliple event handlers or want a plugable system.

For example:

```
├── handle.py
└── handlers
    ├── dns
    │   ├── member_join.py
    │   └── member_leave.py
    └── node
        ├── member_join.sh
        ├── query_deploy.py
```


## installation

just install the serf-plugin-handler via pip

```
pip install serf-plugin-handler
```
create a directory for your serf plugins f.e:

/opt/yourcomp/sph/handlers
copy the examples/handle.py file to  /opt/yourcomp/sph/

in you serf config just include /opt/yourcomp/sph/handle.py

See handle.py if you want to change

## development
Just start the dev vms.

```
vagrant up

vagrant ssh node-1
serf agent -config-file="/etc/sph/serf-node1.json

vagrant ssh node-2
serf agent -config-file="/etc/sph/serf-node2.json

vagrant ssh node-3
serf agent -config-file="/etc/sph/serf-node3.json

Test a little bit
```

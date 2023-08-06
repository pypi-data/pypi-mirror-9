etcd-cli CLI for Etcd based on schemas

Install
=======

.. code-block:: bash

  pip install etcd-cli

Examples
========

.. code-block:: bash

  $ etcd-cli -d set host --host foo.example.com --ip 10.130.197.17 \
  --netmask 255.255.255.0 --gw 10.130.197.254 --hwaddr 6c:ae:8b:60:46:ba \
  --site eur-1
  [INFO    ] Using config file: /etc/etcd-cli/etcd-cli.conf
  [INFO    ] Loading template: templates/host.jinja
  [INFO    ] Set: /host/foo.example.com/site: eur-1
  [INFO    ] Set: /host/foo.example.com/eth0/ip: 192.168.0.1
  [INFO    ] Set: /host/foo.example.com/eth0/hwaddr: 6c:ae:8b:60:46:ba
  [INFO    ] Set: /host/foo.example.com/eth0/netmask: 255.255.255.0
  [INFO    ] Set: /host/foo.example.com/eth0/gw: 192.168.0.254
  [INFO    ] Set: /hwaddr/3c:ae:6b:60:46:ca/interface: eth0
  [INFO    ] Set: /hwaddr/3c:ae:6b:60:46:ca/hostname: foo.example.com


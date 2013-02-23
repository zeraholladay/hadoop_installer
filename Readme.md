# hadoop_installer

A fabric installer to install CDH4 Hadoop on Ubuntu 12.04.

## Installation

Tested with:

    Fabric==1.5.3

Install:

    pip install --requirement=requirements.txt

## Install a two node cluster

Prerequisites and assumptions:

    1. A volume called /data exists and is mounted on each host.
    2. When installing datanodes from a different subnet, master=$name_node should be the internal hostname.
    3. There are no firewall rules stopping network traffic.

Install a namenode:

    name_node=...
    fab --hosts=$name_node install_namenode

Install a datanode on a separate host and the namenode:

    data_node=...
    fab --hosts=$data_node,$name_node install_datanode:master=$name_node

Restart:

    fab --hosts=$data_node,$name_node initd:restart

To verify, browse to http://$name_node:50070.  The "Live Nodes" count should be two.

## Contributing

1. Fork it
2. Create your feature branch (`git checkout -b my-new-feature`)
3. Commit your changes (`git commit -am 'Add some feature'`)
4. Push to the branch (`git push origin my-new-feature`)
5. Create new Pull Request

master=
master_local=
slaves=
key=~/.ssh/

fab -u ubuntu -i $key --hosts=ec2-54-243-136-131.compute-1.amazonaws.com install_namenode
fab -u ubuntu -i $key --hosts=ec2-23-21-29-134.compute-1.amazonaws.com,ec2-107-22-100-210.compute-1.amazonaws.com  install_datanode:master=ip-10-40-229-80

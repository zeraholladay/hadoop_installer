from fabric.api import run, env, settings

def add_cloudera():
    run("""
{ cat <<EOF
deb [arch=amd64] http://archive.cloudera.com/cdh4/ubuntu/precise/amd64/cdh precise-cdh4 contrib
deb-src http://archive.cloudera.com/cdh4/ubuntu/precise/amd64/cdh precise-cdh4 contrib
EOF
} | sudo tee /etc/apt/sources.list.d/cloudera.list > /dev/null
curl -s http://archive.cloudera.com/cdh4/ubuntu/precise/amd64/cdh/archive.key | sudo apt-key add -
sudo apt-get update
""")

def mkdir_data():
    run("""
sudo mkdir -p /data/hadoop
sudo chgrp hadoop /data/hadoop
sudo chmod 775 /data/hadoop
""")

def config_hadoop(master):
    run("""
{ cat <<EOF
<configuration>
<property>
<name>mapred.local.dir</name>
<value>/data/hadoop/mapred/local</value>
</property>
<property>
<name>mapred.map.tasks.speculative.execution</name>
<value>true</value>
</property>
<property>
<name>mapred.reduce.tasks.speculative.execution</name>
<value>false</value>
</property>
<property>
<name>mapred.system.dir</name>
<value>/hadoop/system/mapred</value>
</property>
<property>
<name>mapreduce.jobtracker.staging.root.dir</name>
<value>/user</value>
</property>
<property>
<name>mapred.compress.map.output</name>
<value>true</value>
</property>
<property>
<name>mapred.output.compression.type</name>
<value>BLOCK</value>
</property>
<property>
<name>mapred.child.java.opts</name>
<value>-Xmx550m</value>
</property>
<property>
<name>mapred.job.tracker</name>
<value>%s:8021</value>
</property>
</configuration>
EOF
    } | sudo tee /etc/hadoop/conf/mapred-site.xml > /dev/null

    { cat <<EOF
<configuration>
<property>
<name>hadoop.tmp.dir</name>
<value>/data/tmp/hadoop-\\${user.name}</value>
</property>
<property>
<name>io.file.buffer.size</name>
<value>65536</value>
</property>
<property>
<name>hadoop.rpc.socket.factory.class.default</name>
<value>org.apache.hadoop.net.StandardSocketFactory</value>
<final>true</final>
</property>
<property>
<name>hadoop.rpc.socket.factory.class.ClientProtocol</name>
<value></value>
</property>
<property>
<name>hadoop.rpc.socket.factory.class.JobSubmissionProtocol</name>
<value></value>
</property>
<property>
<name>fs.trash.interval</name>
<value>1440</value>
</property>
<property>
<name>fs.default.name</name>
<value>hdfs://%s:8020/</value>
</property>
</configuration>
EOF
    } | sudo tee /etc/hadoop/conf/core-site.xml > /dev/null

    { cat <<EOF
<configuration>
<property>
<name>dfs.permissions</name>
<value>false</value>
</property>
<property>
<name>dfs.replication</name>
<value>2</value>
</property>
<property>
<name>dfs.datanode.handler.count</name>
<value>6</value>
</property>
<property>
<name>io.file.buffer.size</name>
<value>65536</value>
</property>
<property>
<name>dfs.block.size</name>
<value>134217728</value>
</property>
<property>
<name>dfs.data.dir</name>
<value>/data/hadoop/hdfs/data</value>
</property>
<property>
<name>dfs.datanode.du.reserved</name>
<value>1073741824</value>
</property>
<property>
<name>dfs.name.dir</name>
<value>/data/hadoop/hdfs/name</value>
</property>
<property>
<name>fs.checkpoint.dir</name>
<value>/data/hadoop/hdfs/secondary</value>
</property>
<property>
<name>dfs.http.address</name>
<value>%s:50070</value>
</property>
</configuration>
EOF
    } | sudo tee /etc/hadoop/conf/hdfs-site.xml > /dev/null

    { cat <<EOF
export JAVA_HOME=/usr/lib/jvm/java-6-openjdk-amd64
EOF
    } | sudo tee /etc/hadoop/conf/hadoop-env.sh > /dev/null
""" % tuple(3 * [master]))

def install_namenode():
    if not len(env.hosts) == 1:
        raise Exception("There can be only one master: %s" % env.hosts)
    master = env.hosts[0]
    add_cloudera()
    run("sudo apt-get -y install openjdk-6-jdk hadoop-hdfs-namenode hadoop-0.20-mapreduce-jobtracker")
    mkdir_data()
    config_hadoop(master)
    run("sudo -u hdfs hdfs namenode -format")

def install_datanode(master):
    add_cloudera()
    run("sudo apt-get -y install openjdk-6-jdk hadoop-0.20-mapreduce-tasktracker hadoop-hdfs-datanode")
    mkdir_data()
    config_hadoop(master)

def initd(cmnd):
    with settings(warn_only=True):
        run("/etc/init.d/hadoop-0.20-mapreduce-jobtracker %s" % cmnd)
        run("/etc/init.d/hadoop-0.20-mapreduce-tasktracker %s" % cmnd)
        run("/etc/init.d/hadoop-hdfs-datanode %s" % cmnd)
        run("/etc/init.d/hadoop-hdfs-namenode %s" % cmnd)


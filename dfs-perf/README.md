# DFS-perf experiment for evaluating HDFS + PREACT
_**PREREQUISITE: the HDFS cluster should be setup on Cloudlab before running DFS-perf. If you haven't setup the HDFS cluster, please refer to the [README](../hdfs/README.md) in the `hdfs` folder**_


## Overview of running dfs-perf
There are two parts to running dfs-perf:
1. The first part is filling up the cluster with data using the `SimpleWrite` dfs-perf workload.
2. The second part involves running a read workload using the `SimpleRead` profile, and in parallel conducting a node migration from a set of nodes exercising one redundancy scheme (6-of-9 erasure code) to another redundancy scheme (7-of-10 erasure code). The HDFS cluster setup automatically creates a 20 node cluster such that 10 nodes are using the 6-of-9 erasure coding scheme and 10 nodes are using the 7-of-10 erasure coding scheme.


## Setting up dfs-perf
dfs-perf is *not* running on the same nodes as the HDFS cluster. So, assuming the HDFS setup guide has been followed correctly the HDFS cluster should be running on node0 through node21. Therefore, the dfs-perf workload generators will run on node21 through node41.
1. `cd dfs-perf`
2. You will require the private key (of the public key you used to ssh into the Cloudlab machine -- usually is the `~/.ssh/id_rsa` file on your local computer on Linux and Mac platforms) to be copied to `~/.ssh/` path of `node21`.
3. `bash run.sh` 


## Running dfs-perf read and migrate to generate the evaluation
1. This is the slightly tricky part. First, we need to start reading the data that was written using `SimpleWrite`. To do that, execute `bash bin/dfs-perf SimpleRead`. Once the reading has started, i.e. once you start seeing `Running: 20 slaves. Success: 0 slaves. Failed: 0 slaves.` continuously for about 30 seconds, the node migration has to be issued.
2. The node migration has to be done from the HDFS Namenode. To do that, `ssh` into node0 and `cd` into the repository directory from another shell (i.e. keep the `SimpleRead` command issued above keep running. It contains a Python script called `migrate_nodes.py`. Towards the end of the file, there is a `migration_list` array that currently contains `apt187.apt.emulab.net`. This needs to be modified to a node that is from the set of nodes which are using the 6-of-9 erasure coding scheme. One of those nodes can be found out by executing `cat /tmp/hadoop-3.2.0/etc/hadoop/RS-LEGACY-6-3-1024k.txt | head -n 1`. That should show a node of the form `apt<number>.apt.emulab.net`. Please replace the `migration_list` value in the `migrate_nodes.py` to the relevant node hostname. Once that change has been made, please execute `python3 migrate_nodes.py`. This will trigger a node to be migrated from the set of nodes using the 6-of-3 erasure coding scheme to 7-of-10 erasure coding scheme. The node migration will end once the control returns to the shell. Until then you should see periodically the status of all nodes being shown with one of the nodes being **decommissioned**. The output at the end of the `migrate_nodes` script should be something like:
    ```
    Removing nodes from the disk group and exclude nodes
    apt<number>.apt.emulab.net: Stopping datanode daemon
    apt<number>: Warning: Permanently added 'apt<number>.apt.emulab.net,128.110.96.2' (ECDSA) to the list of known hosts.

    apt<number>.apt.emulab.net: Deleting the data directory
    apt<number>: Warning: Permanently added 'apt<number>.apt.emulab.net,128.110.96.2' (ECDSA) to the list of known hosts.
    Adding the nodes to new disk-groups
    Refresh nodes successful
    Starting datanode daemons
    ```
3. Wait until the `SimpleRead` command finishes. It should take tens of minutes.


## Plotting the evaluation numbers
Once the `SimpleRead` dfs-perf ends (i.e. when the control returns on the dfs-perf master node; node21), the throughput and the latency can be plotted. In order to plot, first the logs need to be collected from all the dfs-perf worker nodes. `ssh` into the dfs-perf master node, i.e. node21, and `cd` into the dfs-perf directory in the cloned repository. Execute the `bash bin/dfs-perf-collect SimpleRead` command. The command will collect all the logs in `./result/slavelogs_SimpleRead/` as `slave-*.log`. The logs can be combined into a plottable csv using the following command `python3 filter.py -w SimpleRead -l call -o result.csv result/slavelogs_SimpleRead/slave-*`. The `result.csv` can be plotted using the following command `python3 ./graph_plotter.py result.csv`. The script will generate two png files, one for throughput and one for latency.


_**The plots generated from the script may not match the plots in Fig. 8, because the submission was based on experiments carried out in the PRObE cluster at CMU that has different hardware, compute and networking infrastructure. This experiment is intended to show that HDFS + PREACT works, and is not meant as a performance experiment. It has also been mentioned in the paper to the same effect.**_



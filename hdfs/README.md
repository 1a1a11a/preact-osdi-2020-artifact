# Evaluating HDFS + PREACT (not a main result)
This is the PREACT enabled HDFS that is intended to show that integrating PREACT in a real distributed file system is straightforward, and to essentially show that 'it works'. The graphs of this experiment are in Fig. 8 of the paper draft uploaded to hotcrp.


## HDFS cluster requirement
We have written this README based on our experiments conducted on the CloudLab infrastructure using the APT cluster and r320 nodes. All the setup scripts expect that the same cluster is re-used for the evaluation of our HDFS + PREACT artifact. We have confirmed with the OSDI artifact evaluation committee that usage of Cloudlab can be assumed for our experiment evaluation. If a different cluster is required, please contact saukad@cs.cmu.edu.


## Setting up the Cloudlab experiment
Instantiate a Cloudlab experiment using the following profile: `osdi-preact-artifact-eval`. This will spawn an experiment with 42 nodes. 21 of those nodes will be used for HDFS, whereas 21 nodes will be used for dfs-perf, which is the workload generator for our evaluation. dfs-perf instructions will be provided after HDFS has been setup.


## Cloning the repository in node0
Once the experiment has been instantiated, you can login into node0 and clone the repository in the directory of your choice. When testing, we used the shared NFS folder `/proj/<project>/` because it had more space than the user's home directory. But, you could choose any directory to clone the repository. The entire setup of the HDFS cluster will happen from the node0, which will also be the Namenode for the HDFS cluster that will be setup.


## Setting up the Cloudlab experiment
There are several steps involved in setting up the HDFS cluster to evaluate our experiment.
1. `cd hdfs` in our current repository
2. `cp ssh_config ~/.ssh_config`
3. You will need to change a few files to reflect the parameters based on the experiment that was launched. Each node launched in the Cloudlab experiment will have the following format: `node<number>.<user>-<experiment>.<project>.apt.emulab.net`. The `<user>, <experiment> and <project>` will be required for changing scripts to execute this evaluation. Please keep them handy. For example, our values for those variables were: `<user>: saukad, <experiment>: qv79471, <project>: redundancy-pg0`.
4. Change `./hadoop-common-project/hadoop-common/src/main/conf/core-site.xml` and replace `hdfs://node0.saukad-qv79471.redundancy-pg0.apt.emulab.net:9000` with your experiment details in the following format: `hdfs://node0.<user>-<experiment>.<project>.apt.emulab.net:9000`
5. Change `./hadoop-hdfs-project/hadoop-hdfs/src/main/conf/hdfs-site.xml` and replace `hdfs://node0.saukad-qv79471.redundancy-pg0.apt.emulab.net:9000` with your experiment details in the following format: `hdfs://node0.<user>-<experiment>.<project>.apt.emulab.net:9000`
6. Change `./hadoop-env.sh` and modify the first line from `USER=saukad` to your `<user>`
7. Execute `bash build-hadoop.sh`
8. Execute `bash copy-script.sh <user> <experiment> <project>`
9. Execute `bash setup-other-nodes.sh <user> <experiment> <project>`
10. Execute `bash hadoop-setup.sh <user> <experiment> <project>`


## Checking if the HDFS cluster is setup correctly
At this point the HDFS cluster should be setup on node0 through node20. node0 is the Namenode and node1 through node20 are the 20 Datanodes in this cluster. To check if the HDFS cluster is setup correctly, you can run the following command on the namenode:

`./hadoop-dist/target/hadoop-3.2.0/bin/hdfs dfsadmin -report | grep "Live datanodes"`

If the cluster is setup correctly, you should see the output as `Live datanodes (20):`

## DFS-perf configuration
Once the HDFS cluster has been setup, please refer to the README in the dfs-perf folder to run the workload and generate the evaluation numbers.

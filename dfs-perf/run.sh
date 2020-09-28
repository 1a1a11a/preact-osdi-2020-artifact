#!/usr/bin/env bash

set -e
# keep track of the last executed command
trap 'last_command=$current_command; current_command=$BASH_COMMAND' DEBUG
# echo an error message before exiting
trap 'echo "\"${last_command}\" command filed with exit code $?."' EXIT


source params.sh
echo user ${user} experiemnt ${exp} ${proj}

echo '############ setup config #############' 
cp ../hdfs/ssh_config ~/.ssh/config
echo "ssh" | sudo tee /etc/pdsh/rcmd_default >/dev/null

# echo '############ updating core-site.xml #############' 
# sed -i "s/saukad-qv79471.redundancy-pg0/${user}-${exp}.${proj}/g" hadoop-common-project/hadoop-common/src/main/conf/core-site.xml 

# echo '############ updating hdfs-site.xml #############' 
# sed -i "s/saukad-qv79471.redundancy-pg0/${user}-${exp}.${proj}/g" hadoop-hdfs-project/hadoop-hdfs/src/main/conf/hdfs-site.xml 

echo '############ node setup #############' 
bash node-setup.sh

echo '############ copy script #############' 
bash copy-script.sh ${user} ${exp} ${proj}

echo '############ setup other nodes #############' 
pdsh -w node[22-41].${user}-${exp}.${proj}.apt.emulab.net bash ~/node-setup.sh

echo '############ install dfs #############' 
mvn install

echo '############ create s***** #############' 
bash create-slaves.sh ${user} ${exp} ${proj}

echo '########### update config ############'
sed -i "s/USER=saukad/USER=${user}/g" conf/dfs-perf-env.sh
sed -i "s/EXP=qv79471/EXP=${exp}/g" conf/dfs-perf-env.sh
sed -i "s/PROJ=redundancy-pg0/PROJ=${proj}/g" conf/dfs-perf-env.sh

echo '############ hadoop setup #############' 
bash pdsh -w node[22-41].${user}-${exp}.${proj}.apt.emulab.net mkdir -p ~/preact-osdi-2020-artifact

echo '############ copy dfs #############' 
bash copy-dfs-perf.sh ${user} ${exp} ${proj}

echo '############ clean  #############' 
# Should output: `Clean the workspace /tmp/dfs-perf-works
bin/dfs-perf-clean

echo '############ fill cluster ############'
bash bin/dfs-perf SimpleWrite 

echo '############ checking fillup ############'
# `90 G  132.0 G  /tmp`
cd ../hdfs && /tmp/hadoop-3.2.0/bin/hdfs dfs -du -h / && cd -



#!/bin/bash
USER=$1
EXP=$2
PROJ=$3
for number in {1..20}
do
scp node-setup.sh node$number.$USER-$EXP.$PROJ.apt.emulab.net:~/
scp -r hadoop-dist/target/hadoop-3.2.0 node$number.$USER-$EXP.$PROJ.apt.emulab.net:~/
scp hadoop-env.sh node$number.$USER-$EXP.$PROJ.apt.emulab.net:hadoop-3.2.0/etc/hadoop/
done
exit 0

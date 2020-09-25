#!/bin/bash
USER=$1
EXP=$2
PROJ=$3
for number in {22..41}
do
scp -r ~/preact-osdi-2020-artifact/dfs-perf node$number.$USER-$EXP.$PROJ.apt.emulab.net:~/preact-osdi-2020-artifact/
done
exit 0

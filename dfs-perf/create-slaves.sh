#!/bin/bash
USER=$1
EXP=$2
PROJ=$3
for number in {22..41}
do
echo "node$number.$USER-$EXP.$PROJ.apt.emulab.net" >> preact_slaves 
done
cp preact_slaves conf/slaves
exit 0

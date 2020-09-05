#!/usr/bin/env bash

sudo apt-get update

# hadoop runtime prerequisite
sudo apt-get -y install openjdk-8-jdk
sudo apt-get -y install zlib1g-dev pkg-config libssl-dev libsasl2-dev
sudo apt-get -y install snappy libsnappy-dev
sudo apt-get -y install bzip2 libbz2-dev
sudo apt-get -y install libjansson-dev
sudo apt-get -y install fuse libfuse-dev
sudo apt-get -y install zstd

sudo apt-get -y install python3 python3-pip
pip3 install numpy matplotlib pandas seaborn

# DevOps utils
sudo apt-get -y install tree


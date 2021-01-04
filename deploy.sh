#!/bin/bash

# Install package on a remote Raspberry Pi for development, e.g.,
# ./deploy.sh raspberrypi.local pi

HOST=$1
USER=$2

ARCHIVE=tmp.tar
INSTALL_DIR=/home/$USER/openwifipass

# Archive project
tmpCommit=`git stash create`
if [ -z $tmpCommit ]; then tmpCommit=HEAD; fi
git archive -o $ARCHIVE $tmpCommit
git gc --prune=now

# Install on remote machine
scp -r $ARCHIVE $USER@$HOST:/home/$USER/
ssh $USER@$HOST "mkdir -p $INSTALL_DIR; tar xf $ARCHIVE -C $INSTALL_DIR/ && rm $ARCHIVE"
ssh $USER@$HOST "pip3 uninstall -y openwifipass; pip3 install $INSTALL_DIR/"

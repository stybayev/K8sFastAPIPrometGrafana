#!/bin/bash
until mongosh --host mongos1 --eval "sh.addShard(\"mongors1/mongors1n1\")"; do
  sleep 5
done

until mongosh --host mongos1 --eval "sh.addShard(\"mongors2/mongors2n1\")"; do
  sleep 5
done

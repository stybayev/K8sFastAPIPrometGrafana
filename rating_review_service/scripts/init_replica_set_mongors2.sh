#!/bin/bash
until mongosh --host mongors2n1 --eval "rs.initiate({_id: \"mongors2\", members: [{_id: 0, host: \"mongors2n1\"}, {_id: 1, host: \"mongors2n2\"}, {_id: 2, host: \"mongors2n3\"}]})"; do
  sleep 5
done

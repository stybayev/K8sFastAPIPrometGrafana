#!/bin/bash

PRIMARY_HOST=$(mongosh --quiet --host mongors1n1 --eval 'rs.status().members.filter(m => m.stateStr === "PRIMARY")[0].name')

echo "Primary host: $PRIMARY_HOST"

mongosh --host $PRIMARY_HOST <<EOF
use admin
db.createUser({
  user: "dos",
  pwd: "dos",
  roles: [{ role: "root", db: "admin" }]
})
EOF

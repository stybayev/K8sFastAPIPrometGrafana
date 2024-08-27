#!/bin/bash

PRIMARY_HOST=$(mongosh --quiet --host mongors1n1 --eval 'rs.status().members.filter(m => m.stateStr === "PRIMARY")[0].name')

echo "Primary host: $PRIMARY_HOST"

mongosh --host $PRIMARY_HOST <<EOF
use admin
db.createUser({
  user: "user",
  pwd: "password",
  roles: [{ role: "root", db: "admin" }]
})
EOF

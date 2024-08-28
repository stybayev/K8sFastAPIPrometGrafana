#!/bin/bash

mongosh --host mongos1 --port 27017 <<EOF
use admin
db.createUser({
  user: "user",
  pwd: "password",
  roles: [{ role: "root", db: "admin" }]
})
EOF


#!/bin/bash

mongosh --host ${MONGO_HOST} --port ${MONGO_PORT} <<EOF
use admin
db.createUser({
  user: "${MONGO_INITDB_ROOT_USERNAME}",
  pwd: "${MONGO_INITDB_ROOT_PASSWORD}",
  roles: [{ role: "root", db: "admin" }]
})
EOF

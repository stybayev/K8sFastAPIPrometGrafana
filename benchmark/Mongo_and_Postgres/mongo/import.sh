sleep 5
if [ "$(mongosh --host ${MONGO_HOST} -u ${MONGO_INITDB_ROOT_USERNAME} -p ${MONGO_INITDB_ROOT_PASSWORD} --eval 'use test_db' --eval 'db.users.countDocuments()')" -eq 0 ]
then
  mongoimport --host ${MONGO_HOST} -u ${MONGO_INITDB_ROOT_USERNAME} -p ${MONGO_INITDB_ROOT_PASSWORD} --authenticationDatabase admin --db ${MONGO_INITDB_DATABASE} --collection likes --type csv --file likes.csv -j 6 --headerline
  mongoimport --host ${MONGO_HOST} -u ${MONGO_INITDB_ROOT_USERNAME} -p ${MONGO_INITDB_ROOT_PASSWORD} --authenticationDatabase admin --db ${MONGO_INITDB_DATABASE} --collection users --type csv --file users.csv --headerline
  mongoimport --host ${MONGO_HOST} -u ${MONGO_INITDB_ROOT_USERNAME} -p ${MONGO_INITDB_ROOT_PASSWORD} --authenticationDatabase admin --db ${MONGO_INITDB_DATABASE} --collection films --type csv --file movies.csv --headerline
  mongosh --host ${MONGO_HOST} -u ${MONGO_INITDB_ROOT_USERNAME} -p ${MONGO_INITDB_ROOT_PASSWORD} --eval 'use test_db' --eval "db.likes.createIndexes([{'user_id': 1}, {'movie_id': 1}, {'likes': 1}])"
else
  echo 'Коллекция не пустая. Импорт не требуется'
fi
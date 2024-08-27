db = db.getSiblingDB(process.env.MONGO_INITDB_DATABASE);
db.createCollection('likes');
db.createCollection('films');
db.createCollection('users');
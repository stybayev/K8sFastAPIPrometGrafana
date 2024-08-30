#!/bin/bash


/opt/vertica/bin/vsql -U $VERTICA_USER -d $VERTICA_DB -c "ALTER USER dbadmin IDENTIFIED BY '$DB_PASSWORD';"
/opt/vertica/bin/vsql -U $VERTICA_USER -d $VERTICA_DB -w $DB_PASSWORD -c "CREATE TABLE $NAME_FEW_TABLE_VERTICA (user_id INTEGER NOT NULL, movie_id VARCHAR(256) NOT NULL, viewed_frame INTEGER NOT NULL);"
/opt/vertica/bin/vsql -U $VERTICA_USER -d $VERTICA_DB -w $DB_PASSWORD -c "CREATE TABLE $NAME_BD_TABLE_VERTICA (user_id INTEGER NOT NULL, movie_id VARCHAR(256) NOT NULL, viewed_frame INTEGER NOT NULL);"
/opt/vertica/bin/vsql -U $VERTICA_USER -d $VERTICA_DB -w $DB_PASSWORD -c "SELECT SET_CONFIG_PARAMETER('MaxClientSessions', 1000);"


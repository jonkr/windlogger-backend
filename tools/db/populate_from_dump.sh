#!/bin/sh
LOCAL_DB_NAME="windlogger"
LOCAL_DUMP_FILE="db.dump"

echo "Populating local postgres with content from ${LOCAL_DUMP_FILE}"
dropdb $LOCAL_DB_NAME
createdb $LOCAL_DB_NAME
pg_restore --no-acl --verbose -x -O -d $LOCAL_DB_NAME $LOCAL_DUMP_FILE
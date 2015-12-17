#!/usr/bin/env bash

# Dumps the DB contents to (remote local) disk

DB_URI=$1
EXCLUDE_CLAUSE=$2

pg_dump $EXCLUDE_CLAUSE --verbose -d $DB_URI -Fc -f /tmp/db.dump
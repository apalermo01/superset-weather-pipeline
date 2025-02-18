#!/bin/bash 

source .env

BACKUP_PATH="/tmp/superset-weather-pipeline-backup"
# remove old backup 
if [ -f "$BACKUP_PATH" ];
then 
    rm -f "$BACKUP_PATH";
fi

echo "Exporting production data..."

pg_dump $PRODUCTION_CONNECTION_STRING \
    --no-password \
    --format=t \
    --no-owner \
    --no-privileges \
    -f "$BACKUP_PATH"

echo "Restoring staging database"

psql $STAGING_CONNECTION_STRING \
    -c "DROP EXTENSION IF EXISTS postgis CASCADE"
pg_restore -d $STAGING_CONNECTION_STRING \
    "$BACKUP_PATH" \
    --no-password \
    --no-owner \
    --no-privileges \
    --clean \
    --if-exists \
    --exit-on-error

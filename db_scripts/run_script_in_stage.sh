#!/bin/bash 

source ./.env

if [ ! -f $1 ]; then
    echo "no file provided"
    exit
fi

echo "running file $1"
psql $STAGING_CONNECTION_STRING \
     --file=$1 



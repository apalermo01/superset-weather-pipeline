#!/bin/sh

source ./config
CURRENT_PATH=$(pwd)

docker compose down

cd $SUPERSET_PATH/superset
docker compose down

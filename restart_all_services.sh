#!/bin/bash

CURRENT_PATH=$(pwd)

source ./config 
cd $SUPERSET_PATH

echo "=========================="
echo "== CONFIGURING SUPERSET =="
echo "=========================="

if [[ ! -d $SUPERSET_PATH/superset ]]; then 
  echo "cloning superset..."
  git clone https://github.com/apache/superset
fi

cd $SUPERSET_PATH/superset
git checkout tags/4.1.1

echo "stopping existing containers..."
docker stop superset_worker_beat \
            superset_app \
            superset_init \
            superset_worker \
            superset_db \
            superset_cache

echo "removing existing containers..."
docker rm superset_worker_beat \
          superset_app \
          superset_init \
          superset_worker \
          superset_db \
          superset_cache

echo "rebuilding superset..."

docker compose -f docker-compose-image-tag.yml up --force-recreate --remove-orphans --detach

echo "superset is running in detached mode. Visit localhost:8088"

cd $CURRENT_PATH

echo "=========================="
echo "== CONFIGURING POSTGRES =="
echo "=========================="

docker stop weather_db \
            staging_weather_db 

docker rm weather_db \
          staging-weather-db

docker compose -f compose.yml up --detach

echo "=========================="
echo "===== SETUP COMPLETE ====="
echo "=========================="

echo "Superset: visit localhost:8088"
echo "Postgres: connect using psql postgresql://user:pass@localhost:5432/postgres"
echo "Postgres (staging database): connect using psql postgresql://user:pass@localhost:5000/postgres"


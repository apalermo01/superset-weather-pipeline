#!/bin/bash

for file in $(ls ./db_migrations)
do 
  psql -f $file
done

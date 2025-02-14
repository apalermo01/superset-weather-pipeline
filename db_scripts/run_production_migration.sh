#!/bin/bash 

# get connection strings
source ./.env

# check that an argument was passed
if [ ! -f $1 ]; then
    echo "no file provided"
    exit
fi

SQL_FILE="$1"
QUERY_CONTENT=$(cat "$SQL_FILE")
QUERY_HASH=$(echo -n "$QUERY_CONTENT" | sha256sum | awk '{print $1}')

# don't run scripts in the historical folder
case "$1" in 
    *historical* )
        echo "Cannot run a historical script in production. Exiting...";;
esac

# verify we want to run this in production
read -p "Warning: this will execute $1 in the production database. Do you want to continue (y/n)?" choice 

case "$choice" in 
    y|Y ) echo "proceeding with migration";;
    * ) echo "exiting";;
esac

# check that the script has not already been run 
RESULT=$(psql $PRODUCTION_CONNECTION_STRING -t -c "
    prepare migration_select(VARCHAR) AS
        select count(*)
        from public.migrations
        where query_hash = \$1;
    execute migration_select('$QUERY_HASH');
" | grep -o '[[:digit:]]')

if [ $RESULT -gt 0 ]; then 
    echo "Script already ran. Exiting..."
    # move script to migrations folder
    mv $1 "./db_migrations/historical"
    echo "Script moved to historical folder."
    exit
fi

# run the script
echo "running file $1"

psql $PRODUCTION_CONNECTION_STRING \
    --file=$1 \
    --variable ON_ERROR_STOP=1

if [ $? -ne 0 ]; then 
    echo "Migration failed"
    exit 1
else 
    echo "Migration successful"
fi

# insert script info into migrations table

psql $PRODUCTION_CONNECTION_STRING -c "
    prepare migration_insert(VARCHAR, VARCHAR) AS
        insert into public.migrations(file_name, query_hash)
        values(\$1, \$2);
    execute migration_insert('$SQL_FILE', '$QUERY_HASH');
" 

echo "Script added to migrations table."

# move script to migrations folder
mv $1 "./db_migrations/historical"
echo "Script moved to historical folder."

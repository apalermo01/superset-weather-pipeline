create table if not exists public.migrations(
    id serial primary key,
    date_created timestamp with time zone default current_timestamp,
    file_name varchar(255),
    query_hash varchar(255)
)

create table fact_tables.stations (
    id varchar(255) primary key,
    station_url varchar(255),
    type varchar(255),
    location geometry(POINT),
    location_lat decimal,
    location_long decimal,
    elevation_unit varchar(255),
    elevation decimal,
    station_name varchar(255),
    timezone varchar(255),
    forecast_url varchar(255),
    county_url varchar(255),
    fire_weather_zone_url varchar(255)
);

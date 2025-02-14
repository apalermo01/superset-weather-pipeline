import logging
from typing import Optional, Dict
from src.etl import apis
import psycopg
from psycopg import sql

from src.util.env_util import get_env

logger = logging.getLogger(__name__)


def upsert_records_from_list(func):
    """Assumes data is a list of dictionaries"""

    def wrapper():

        result = func()
        if not result:
            return

        assert len(result['data']) > 0
        columns = list(result['data'][0].keys())

        insert_query = sql.SQL("""
        insert into {}.{} ({})
        values ({})
        on conflict({})
        do update set
        {}
        """).format(sql.Identifier(result['schema']),
                    sql.Identifier(result['table']),
                    sql.SQL(', ').join(map(sql.Identifier, columns)),
                    sql.SQL(', ').join(sql.Placeholder() * len(columns)),
                    sql.SQL(', ').join(map(sql.Identifier, result['id_cols'])),
                    sql.SQL(', ').join(
                        sql.SQL('{} = excluded.{}').format(sql.Identifier(col), sql.Identifier(col))
                        for col in result['update_cols']
                    ))
        with psycopg.connect(get_env("PRODUCTION_CONNECTION_STRING")) as conn:
            with conn.cursor() as cur:
                cur.executemany(insert_query, [list(i.values()) for i in result['data']])
                logger.info(f"upsert affected {cur.rowcount} records")

    return wrapper

@upsert_records_from_list
def populate_stations() -> Optional[Dict]:
    try:
        data = apis.get_stations_by_state(["NC"])
    except Exception as e:
        logger.error(e)
        return None

    data_shaped = []
    for f in data["features"]:
        if f["geometry"]["type"] != "Point":
            raise ValueError(f"unexpected geometry type: {f['geometry']['type']}")
        long, lat = f["geometry"]["coordinates"]
        record = {
                "id": f["properties"]["stationIdentifier"],
                "station_url": f["id"],
                "type": f["properties"]["@type"],
                "location": f"SRID=4326;POINT({float(lat)} {float(long)})",
                "elevation_unit": f["properties"]["elevation"]["unitCode"],
                "elevation": f["properties"]["elevation"]["value"],
                "station_name": f["properties"]["name"],
                "timezone": f["properties"]["timeZone"],
                "forecast_url": f["properties"].get("forecast"),
                "county_url": f["properties"].get("county"),
                "fire_weather_zone_url": f["properties"].get("fireWeatherZone"),
            }
        data_shaped.append(record)
    return {
        'data': data_shaped,
        'schema': 'fact_tables',
        'table': 'stations',
        'id_cols': ['id'],
        'update_cols': ['station_url', 'type', 'location',
                        'elevation_unit', 'elevation', 'station_name',
                        'timezone', 'forecast_url', 'county_url', 'fire_weather_zone_url'],
        'succ': True
    }

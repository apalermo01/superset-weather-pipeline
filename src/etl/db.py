import logging

from src.etl import apis
import psycopg

from src.util.env_util import get_env

logger = logging.getLogger(__name__)


def insert_records(func):
    """Assumes data is a list of dictionaries"""

    def wrapper():
        data, table_name, succ = func()
        if not succ:
            return
        assert len(data) > 0
        columns = data[0].keys()
        num_columns = len(columns)

        insert_query = f"""
        insert into {table_name} ({','.join(columns)})
        values ({'%s,'*(num_columns-1) + '%s'})
        """
        logger.info(f"insert query = {insert_query}")
        with psycopg.connect(get_env("PRODUCTION_CONNECTION_STRING")) as conn:
            with conn.cursor() as cur:
                pass
    return wrapper

@insert_records
def populate_stations():
    try:
        data = apis.get_stations_by_state(["NC"])
    except Exception as e:
        logger.error(e)
        return None, None, False

    data_shaped = []
    for f in data["features"]:
        if f["geometry"]["type"] != "Point":
            raise ValueError(f"unexpected geometry type: {f['geometry']['type']}")
        data_shaped.append(
            {
                "id": f["properties"]["stationIdentifier"],
                "station_url": f["id"],
                "type": f["properties"]["@type"],
                "location": f["geometry"]["coordinates"],
                "elevation_unit": f["properties"]["elevation"]["unitCode"],
                "elevation": f["properties"]["elevation"]["value"],
                "station_name": f["properties"]["name"],
                "timezone": f["properties"]["timeZone"],
                "forecast_url": f["properties"].get("forecast"),
                "county_url": f["properties"].get("county"),
                "fire_weather_zone_url": f["properties"].get("fireWeatherZone"),
            }
        )
    return data_shaped, 'public.stations', True

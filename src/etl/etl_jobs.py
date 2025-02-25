import json
import logging
from typing import Optional

from . import apis, db

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


@db.upsert_records_from_list
def populate_stations_by_state(states: list) -> Optional[dict]:
    try:
        data = apis.get_stations_by_state(states)
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
            "location_lat": float(lat),
            "location_long": float(long),
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
        "data": data_shaped,
        "schema": "fact_tables",
        "table": "stations",
        "id_cols": ["id"],
        "update_cols": [
            "station_url",
            "type",
            "location",
            "elevation_unit",
            "elevation",
            "station_name",
            "timezone",
            "forecast_url",
            "county_url",
            "fire_weather_zone_url",
        ],
        "succ": True,
    }


def get_latest_observations_by_station_ids(station_ids: list):
    for i in station_ids:
        get_latest_observations_by_station(i)


def get_latest_observations_by_station(station_id: str) -> Optional[dict]:
    try:
        print("getting observations for ", station_id)
        data = apis.get_latest_observations(station_id)
    except Exception as e:
        logger.error(e)
        return None

    record = {
        "observation_id": data["properties"]["@id"],
        "station_id": data["properties"]["station"].split("/")[-1],
        "timestamp": data["properties"]["timestamp"],
        "temperature_unit": data["properties"]["temperature"].get("unitCode"),
        "temperature_value": data["properties"]["temperature"].get("value"),
        "temperature_quality_control": data["properties"]["temperature"].get(
            "qualityControl"
        ),
        "dewpoint_unit": data["properties"]["dewpoint"].get("unitCode"),
        "dewpoint_value": data["properties"]["dewpoint"].get("value"),
        "dewpoint_quality_control": data["properties"]["dewpoint"].get("qualityControl"),
        "wind_direction_unit": data["properties"]["windDirection"].get("unitCode"),
        "wind_direction_value": data["properties"]["windDirection"].get("value"),
        "wind_direction_quality_control": data["properties"]["windDirection"].get(
            "qualityControl"
        ),
        "wind_speed_unit": data["properties"]["windSpeed"].get("unitCode"),
        "wind_speed_value": data["properties"]["windSpeed"].get("value"),
        "wind_speed_quality_control": data["properties"]["windSpeed"].get("qualityControl"),
        "wind_gust_unit": data["properties"]["windGust"].get("unitCode"),
        "wind_gust_value": data["properties"]["windGust"].get("value"),
        "wind_gust_quality_control": data["properties"]["windGust"].get("qualityControl"),

        "barometric_pressure_unit": data["properties"]["barometricPressure"].get("unitCode"),
        "barometric_pressure_value": data["properties"]["barometricPressure"].get("value"),
        "barometric_pressure_quality_control": data["properties"]["barometricPressure"].get(
            "qualityControl"
        ),
        
        "sea_level_pressure_unit": data["properties"]["seaLevelPressure"].get("unitCode"),
        "sea_level_pressure_value": data["properties"]["seaLevelPressure"].get("value"),
        "sea_level_pressure_quality_control": data["properties"]["seaLevelPressure"].get(
            "qualityControl"
        ),
        "visibility_unit": data["properties"]["visibility"].get("unitCode"),
        "visibility_value": data["properties"]["visibility"].get("value"),
        "visibility_quality_control": data["properties"]["visibility"].get(
            "qualityControl"
        ),
        "max_temperature_last_24_hours_unit": data["properties"]["maxTemperatureLast24Hours"].get("unitCode"),
        "max_temperature_last_24_hours_value": data["properties"]["maxTemperatureLast24Hours"].get("value"),
        "max_temperature_last_24_hours_quality_control": data["properties"]["maxTemperatureLast24Hours"].get(
            "qualityControl"
        ),
        "min_temperature_last_24_hours_unit": data["properties"]["minTemperatureLast24Hours"].get("unitCode"),
        "min_temperature_last_24_hours_value": data["properties"]["minTemperatureLast24Hours"].get("value"),
        "min_temperature_last_24_hours_quality_control": data["properties"]["minTemperatureLast24Hours"].get(
            "qualityControl"
        ),
        "precipitation_last_3_hours_unit": data["properties"]["precipitationLast3Hours"].get("unitCode"),
        "precipitation_last_3_hours_value": data["properties"]["precipitationLast3Hours"].get("value"),
        "precipitation_last_3_hours_quality_control": data["properties"]["precipitationLast3Hours"].get(
            "qualityControl"
        ),
        "relative_humidity_unit": data["properties"]["relativeHumidity"].get("unitCode"),
        "relative_humidity_value": data["properties"]["relativeHumidity"].get("value"),
        "relative_humidity_quality_control": data["properties"]["relativeHumidity"].get(
            "qualityControl"
        ),
        "wind_chill_unit": data["properties"]["windChill"].get("unitCode"),
        "wind_chill_value": data["properties"]["windChill"].get("value"),
        "wind_chill_quality_control": data["properties"]["windChill"].get(
            "qualityControl"
        ),
        "heat_index_unit": data["properties"]["heatIndex"].get("unitCode"),
        "heat_index_value": data["properties"]["heatIndex"].get("value"),
        "heat_index_quality_control": data["properties"]["heatIndex"].get(
            "qualityControl"
        ),
        "cloud_layers": data["properties"]["cloudLayers"]
    }

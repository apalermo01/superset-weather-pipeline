from . import apis
from .ingestion import UpsertDataStruct, upsert_records_from_list


@upsert_records_from_list
def run_stations_ingestion(states: list, use_cache: bool = True) -> UpsertDataStruct:
    """calls stations endpoint to populate fact table"""
    raw_data = apis.get_stations_by_state(states, use_cache)
    data_shaped = []
    for f in raw_data["data"]["features"]:
        if f["geometry"]["type"] != "Point":
            raise ValueError("unexpected geometry type: " + f"{f['geometry']['type']}")
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
        "succ": True
    }

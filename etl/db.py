import apis
import psycopg2

#Test

def populate_stations():
    data = apis.get_stations_by_state(["NC"])
    data_shaped = []
    for f in data["features"]:
        if f["geometry"]["type"] != "Point":
            raise ValueError(f"unexpected geometry type: {f['geometry']['type']}")
        data_shaped.append(
            {
                "id": f["properties"]["stationIdentifier"],
                "station_url": f["id"],
                "type": f["properties"]["@type"],
                "location": f["geometry"]['coordinates'],
                "elevation_unit": f["properties"]["elevation"]["unitCode"],
                "elevation": f["properties"]["elevation"]["value"],
                "station_name": f["properties"]["name"],
                "timezone": f["properties"]["timeZone"],
                "forecast_url": f["properties"].get("forecast"),
                "county_url": f["properties"].get("county"),
                "fire_weather_zone_url": f["properties"].get("fireWeatherZone"),
            }
        )
    print("data = ", data_shaped)


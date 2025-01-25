import requests
import json

# TODO: handle pagination

class APIHandler:
    base_url = "https://api.weather.gov"

def api_wrapper(func):
    def wrapper(*args, **kwargs):
        response = func(*args, **kwargs)
        response.raise_for_status()
        return response.json()
    return wrapper

@api_wrapper
def get_stations():
    return requests.get(f"{APIHandler.base_url}/stations")

@api_wrapper 
def get_stations_by_state(states: list):
    states_str = ",".join(states)
    url = f"{APIHandler.base_url}/stations?state={states_str}"
    print("url = ", url)
    return requests.get(url)

@api_wrapper 
def get_latest_observations(station_id: str):
    url = f"{APIHandler.base_url}/stations/{station_id}/observations/latest"
    return requests.get(url)

def main():
    # print(get_stations_by_state(['NC']))
    # station_id = '059PG'
    data = get_latest_observations("ELRN7")
    print("data = ", data)

    with open("response_data.json", "w") as f:
        json.dump(data, f, indent=2)


if __name__ == '__main__': 
    main()

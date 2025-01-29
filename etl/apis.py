import json
import logging
from typing import Literal

import requests

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class APIHandler:
    base_url = "https://api.weather.gov"
    max_tries = 10


def call_api(url: str, method: Literal["get"], arrs: list):

    allowed_methods = ["get"]
    if method not in allowed_methods:
        raise ValueError(f"Invalid method. {method} is not one of {allowed_methods}")

    funcs = {"get": requests.get}

    all_data = {a: [] for a in arrs}

    keep_going = True
    count = 0

    while keep_going and count < APIHandler.max_tries:
        logger.info(f"pinging url {url} with method {method}")
        response = funcs[method](url=url)
        response.raise_for_status()
        data = response.json()

        for a in arrs:
            logger.info(f"{a} got {len(data[a])} records")
            if len(data[a]) == 0:
                keep_going = False
            all_data[a].extend(data[a])

        if "pagination" not in data:
            logger.info(f"pagination entry not found in response. Stopping...")
            keep_going = False

        elif "next" not in data["pagination"]:
            logger.info(f"next url not found in response. Stopping...")
            keep_going = False

        else:
            url = data["pagination"]["next"]

        count += 1

    return all_data


def get_stations():
    return requests.get(f"{APIHandler.base_url}/stations")


def get_stations_by_state(states: list):
    states_str = ",".join(states)
    print("states str = ", states_str)
    url = f"{APIHandler.base_url}/stations?state={states_str}"
    return call_api(url, "get", ["features"])


def get_latest_observations(station_id: str):
    url = f"{APIHandler.base_url}/stations/{station_id}/observations/latest"
    return requests.get(url)

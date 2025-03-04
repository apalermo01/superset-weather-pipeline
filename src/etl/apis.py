import datetime
import glob
import json
import logging
from typing import Literal, Optional

import requests

from ..util.env_util import get_env

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

RAW_PATH = get_env("RAW_PATH")


class APIHandler:
    base_url = "https://api.weather.gov"
    max_tries = 10


def check_cache(func):

    def wrapper(*args, **kwargs):
        logger.info("checking if we're using cache...")
        logger.info(f"kwargs = {kwargs}")
        if kwargs.get("use_cache"):
            logger.info("inspecting cache...")
            url = args[0]
            path_glob = f"{url.replace('/', '%2F')}*"
            matches = glob.glob(path_glob, root_dir=RAW_PATH)
            if len(matches) > 0:

                matches = sorted(
                    matches,
                    key=lambda x: datetime.datetime.strptime(
                        x.split("::::")[1].split(".json")[0], "%Y-%m-%d::%H:%M:%S.%f"
                    ),
                    reverse=True
                )
                cached_file = matches[0]
                path = f"{RAW_PATH}/{cached_file}"
                logger.info(f"reading from cached file {path}")
                with open(path, "r") as f:
                    result = json.load(f)
                    return {"data": result, "cached": True}

            else:
                logger.info("cached data not found. Calling api...")

        result = func(*args, **kwargs)
        return result

    return wrapper


@check_cache
def call_api(
    url: str,
    method: Literal["get"],
    use_cache: bool = False,
) -> dict:
    """API handler for calling the weather api.

    This does NOT handle pagination / large number of records
    """
    allowed_methods = ["get"]
    if method not in allowed_methods:
        raise ValueError(f"Invalid method. {method} is not one of {allowed_methods}")
    funcs = {"get": requests.get}
    response = funcs[method](url=url)
    response.raise_for_status()
    return {"data": response.json(), "cached": False}


@check_cache
def call_api_with_pages(
    url: str,
    method: Literal["get"],
    arrs: Optional[list] = None,
    use_cache: bool = False,
) -> dict:
    """API handler meant to get batches of records with pagination"""

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

        if arrs:
            for a in arrs:
                logger.info(f"{a} got {len(data[a])} records")
                if len(data[a]) == 0:
                    keep_going = False
                all_data[a].extend(data[a])

        if "pagination" not in data:
            logger.info("pagination entry not found in response. Stopping...")
            keep_going = False

        elif "next" not in data["pagination"]:
            logger.info("next url not found in response. Stopping...")
            keep_going = False

        else:
            url = data["pagination"]["next"]

        count += 1

    return {"data": all_data, "cached": False}


def get_stations_by_state(
    states: list, use_cache: Optional[bool] = False, limit: Optional[int] = 500
) -> tuple[dict, str]:

    logger.info(f"collection stations for {states}")
    states_str = ",".join(states)
    url = f"{APIHandler.base_url}/stations?state={states_str}&limit={limit}"
    data = call_api_with_pages(url, "get", arrs=["features"], use_cache=use_cache)
    return {"data": data["data"], "url": url, "cached": data["cached"]}


def get_latest_observations(
    station_id: str, use_cache: bool = False
) -> tuple[dict, str]:
    url = f"{APIHandler.base_url}/stations/{station_id}/observations/latest"
    data = call_api(url, "get", use_cache=use_cache)
    return {"data": data["data"], "url": url, "cached": data["cached"]}

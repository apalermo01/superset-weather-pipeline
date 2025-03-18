from datetime import datetime as dt
import glob
import json
import logging

from ..util.env_util import get_env

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

RAW_PATH = get_env("RAW_PATH")


def check_cache(func):

    def wrapper(*args, **kwargs):
        logger.info("checking if we're using cache...")
        if kwargs.get("use_cache"):
            logger.info("inspecting cache...")
            url = kwargs.get("url", args[0])
            path_glob = f"{url.replace('/', '%2F')}*"
            matches = glob.glob(path_glob, root_dir=RAW_PATH)
            if len(matches) > 0:

                matches = sorted(
                    matches,
                    key=lambda x: dt.strptime(
                        x.split("::::")[1].split(".json")[0], "%Y-%m-%d::%H:%M:%S.%f"
                    ),
                    reverse=True,
                )
                cached_file = matches[0]
                path = f"{RAW_PATH}/{cached_file}"
                logger.info(f"reading from cached file {path}")
                with open(path, "r") as f:
                    result = json.load(f)
                    return {"data": result, "url": url, "cached": True, "path": path}

            else:
                logger.info("cached data not found. Calling api...")

        result = func(*args, **kwargs)

        return insert_into_raw(result)

    return wrapper


def insert_into_raw(result):

    if not result:
        return

    url = result["url"]
    data = result["data"]
    cached = result["cached"]

    if cached:
        return result["path"]

    filename = f"{url.replace('/', '%2F')}::::{str(dt.now()).replace(" ", "::")}"

    with open(f"{RAW_PATH}/{filename}.json", "w") as f:
        json.dump(data, f, indent=4)

    result["path"] = f"{RAW_PATH}/{filename}.json"
    return result

import logging

from src.etl import etl_jobs

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def main():

    etl_jobs.populate_stations_by_state(["NC"], use_cache=True)

    # etl_jobs.get_latest_observations_by_station_ids(["0422W"])


if __name__ == "__main__":
    main()

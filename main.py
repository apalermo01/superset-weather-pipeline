import logging

from src.etl import db

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def main():

    db.populate_stations()


if __name__ == "__main__":
    main()

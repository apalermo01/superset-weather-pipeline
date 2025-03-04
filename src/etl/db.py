import json
import logging
from datetime import datetime
from typing import Optional

import psycopg
from psycopg import sql

from src.util.env_util import get_env

logger = logging.getLogger(__name__)

CONN_STRING = get_env("STAGING_CONNECTION_STRING")
RAW_PATH = get_env("RAW_PATH")


def insert_into_raw(func):

    def wrapper(*args, **kwargs):

        if kwargs.get("use_cache"):
            # todo: logic to query table for cached data
            pass
        result = func(*args, **kwargs)
        if not result:
            return
        url = result["url"]
        data = result["data"]
        cached = result["cached"]
        if cached:
            return

        filename = (
            f"{url.replace('/', '%2F')}::::{str(datetime.now()).replace(" ", "::")}"
        )
        with open(f"{RAW_PATH}/{filename}.json", "w") as f:
            json.dump(data, f, indent=4)

    return wrapper


def upsert_records_from_list(func):
    """Assumes data is a list of dictionaries"""

    def wrapper():

        result = func()
        if not result:
            return

        assert len(result["data"]) > 0
        columns = list(result["data"][0].keys())

        insert_query = sql.SQL(
            """
        insert into {}.{} ({})
        values ({})
        on conflict({})
        do update set
        {}
        """
        ).format(
            sql.Identifier(result["schema"]),
            sql.Identifier(result["table"]),
            sql.SQL(", ").join(map(sql.Identifier, columns)),
            sql.SQL(", ").join(sql.Placeholder() * len(columns)),
            sql.SQL(", ").join(map(sql.Identifier, result["id_cols"])),
            sql.SQL(", ").join(
                sql.SQL("{} = excluded.{}").format(
                    sql.Identifier(col), sql.Identifier(col)
                )
                for col in result["update_cols"]
            ),
        )
        with psycopg.connect(CONN_STRING) as conn:
            with conn.cursor() as cur:
                cur.executemany(
                    insert_query, [list(i.values()) for i in result["data"]]
                )
                logger.info(f"upsert affected {cur.rowcount} records")

    return wrapper

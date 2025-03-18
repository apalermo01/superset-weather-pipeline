import logging
from typing import TypedDict

import psycopg
from psycopg import sql

from src.util.env_util import get_env

logger = logging.getLogger(__name__)

CONN_STRING = get_env("STAGING_CONNECTION_STRING")
RAW_PATH = get_env("RAW_PATH")


class UpsertDataStruct(TypedDict):
    data: list
    schema: str
    table: str
    id_cols: list
    update_cols: list
    succ: bool


def upsert_records_from_list(func):
    """Assumes data is a list of dictionaries"""

    def wrapper(*args, **kwargs):

        result = func(*args, **kwargs)
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

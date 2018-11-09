# database_manager.py
#
# All methods here can be converted to handle query and
# an arbitrary amount of args to support any database system
# Note; asyncronous methods can not be interchanged with syncronous

import configparser
import sqlite3 as sql
from typing import List

import aiosqlite


config = configparser.ConfigParser()
config.read("./config.ini")
db_path = config["Database"]["sqlite"]


def sync_execute(query: str, *args) -> None:
    """Syncronous function to execute a statement"""
    db = sql.connect(db_path, detect_types=sql.PARSE_DECLTYPES)
    cursor = db.cursor()
    cursor.execute(query, *args)
    db.commit()
    db.close()


def sync_fetchall(query: str, *args) -> List[sql.Row]:
    """Syncronous function to fetch all results from query"""
    db = sql.connect(db_path, detect_types=sql.PARSE_DECLTYPES)
    cursor = db.cursor()
    cursor.execute(query, *args)
    all_rows = cursor.fetchall()
    return all_rows


async def execute(query: str, *args) -> None:
    """Asyncronous function to execute statement"""
    types = sql.PARSE_DECLTYPES
    async with aiosqlite.connect(db_path, detect_types=types) as db:
        await db.execute(query, *args)
        await db.commit()


async def fetchone(query: str, *args) -> sql.Row:
    """Asyncronous function to execute statement"""
    row = None
    types = sql.PARSE_DECLTYPES
    async with aiosqlite.connect(db_path, detect_types=types) as db:
        async with db.execute(query, *args) as cursor:
            row = await cursor.fetchone()
            await cursor.close()
    return row


async def fetchall(query: str, *args) -> List[sql.Row]:
    """Fetches all results in a list of tuples"""
    rows = None
    types = sql.PARSE_DECLTYPES
    async with aiosqlite.connect(db_path, detect_types=types) as db:
        async with db.execute(query, *args) as cursor:
            rows = await cursor.fetchall()
            await cursor.close()
    return rows


def make_sure_tables_exist():
    """
    Uses the utility methods in database_manager
    to make sure all tables exist on startup
    """
    sync_execute("""
        CREATE TABLE IF NOT EXISTS blacklistedchannels(
            channelid   BIGINT,
            guildid     BIGINT,
            date        timestamp,
            setbyid     BIGING,
            PRIMARY KEY (channelid, guildid));""")

    sync_execute("""
        CREATE TABLE IF NOT EXISTS prefixes(
            guildid BIGINT,
            prefix text,
            PRIMARY KEY (guildid, prefix));""")

    sync_execute("""
        CREATE TABLE IF NOT EXISTS warnings(
            id int PRIMARY KEY,
            guildid BIGINT,
            userid BIGINT);""")

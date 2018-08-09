import sqlite3 as sql
import asyncio
import aiosqlite
import configparser

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


def sync_fetchall(query: str, *args) -> list:
    """Syncronous function to fetch all results from query"""
    db = sql.connect(db_path, detect_types=sql.PARSE_DECLTYPES)
    cursor = db.cursor()
    cursor.execute(query, *args)
    all_rows = cursor.fetchall()
    return all_rows


async def execute(query: str, *args) -> None:
    """Asyncronous function to execute statement"""
    async with aiosqlite.connect(db_path, detect_types=sql.PARSE_DECLTYPES) as db:
        await db.execute(query, *args)
        await db.commit()


async def fetchone(query: str, *args) -> tuple:
    """Asyncronous function to execute statement"""
    row = None
    async with aiosqlite.connect(db_path, detect_types=sql.PARSE_DECLTYPES) as db:
        async with db.execute(query, *args) as cursor:
            row = await cursor.fetchone()
            await cursor.close()
    return row


async def fetchall(query: str, *args) -> list:
    rows = None
    async with aiosqlite.connect(db_path, detect_types=sql.PARSE_DECLTYPES) as db:
        async with db.execute(query, *args) as cursor:
            rows = await cursor.fetchall()
            await cursor.close()
    return rows 


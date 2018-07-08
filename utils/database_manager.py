import sqlite3 as sql
import asyncio
import aiosqlite
import configparser

config = configparser.ConfigParser()
config.read("./config.ini")
db_path = config["Database"]["sqlite"]

def sync_execute(query, *args) -> None:
    db = sql.connect(db_path, detect_types=sql.PARSE_DECLTYPES)
    cursor = db.cursor()
    cursor.execute(query, *args)
    db.commit()
    db.close()


def sync_fetchall(query, *args) -> list:
    db = sql.connect(db_path, detect_types=sql.PARSE_DECLTYPES)
    cursor = db.cursor()
    cursor.execute(query, *args)
    all_rows = cursor.fetchall()
    return all_rows

async def execute(query, *args) -> None:
    async with aiosqlite.connect(db_path, detect_types=sql.PARSE_DECLTYPES) as db:
        await db.execute(query, *args)
        await db.commit()

async def fetchcursor(query, *args) -> sql.Cursor:
    cursor = None
    async with aiosqlite.connect(db_path, detect_types=sql.PARSE_DECLTYPES) as db:
        async with db.execute(query, *args) as cur_cursor:
            cursor = cur_cursor        
    return cursor

async def fetchone(query, *args) -> tuple:
    row = None
    async with aiosqlite.connect(db_path, detect_types=sql.PARSE_DECLTYPES) as db:
        # cursor = await fetchcursor(query, *args)
        async with db.execute(query, *args) as cursor:
            row = await cursor.fetchone()
            await cursor.close()
    return row

async def fetchall(query, *args) -> list:
    rows = None
    async with aiosqlite.connect(db_path, detect_types=sql.PARSE_DECLTYPES) as db:
        async with db.execute(query, *args) as cursor:
            rows = await cursor.fetchall()
            await cursor.close()
    return rows 


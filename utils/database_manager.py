import asyncio
import aiosqlite
import configparser

config = configparser.ConfigParser()
config.read("./config.ini")
db_path = config["Database"]["sqlite"]


async def execute(query, *args):
    async with aiosqlite.connect(db_path) as db:
        await db.execute(query, *args)
        await db.commit()

async def fetchcursor(query, *args):
    cursor = None
    async with aiosqlite.connect(db_path) as db:
        async with db.execute(query, *args) as cur_cursor:
            cursor = cur_cursor        
    return cursor

async def fetchone(query, *args):
    row = None
    async with aiosqlite.connect(db_path) as db:
        # cursor = await fetchcursor(query, *args)
        async with db.execute(query, *args) as cursor:
            row = await cursor.fetchone()
            await cursor.close()
    return row

async def fetchall(query, *args):
    rows = None
    async with aiosqlite.connect(db_path) as db:
        async with db.execute(query, *args) as cursor:
            rows = await cursor.fetchall()
            await cursor.close()
    return rows 


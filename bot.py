import os
import sys
import logging
import asyncio
import traceback
import datetime
import configparser
from pathlib import Path

import discord
from discord.ext import commands

from utils import database_manager as sqlite

today_formatted = datetime.datetime.today().strftime("%B %d, &Y")

config = configparser.ConfigParser()
config.read("config.ini")
secrets = config["Secrets"]
botconfig = config["Bot"]

Path("./logs").mkdir(exist_ok=True)

logger = logging.getLogger("discord")
logger.setLevel(logging.INFO)
handler = logging.FileHandler(
    filename=f"logs/discord {today_formatted}.log",
    encoding="utf-8", mode="a"
)
handler.setFormatter(logging.Formatter(
    "%(asctime)s:%(levelname)s:%(name)s: %(message)s"))
logger.addHandler(handler)

class MyBot(commands.AutoShardedBot):
    def __init__(self, **kwargs):
        super().__init__(
            description=kwargs.pop("description", ""),
            case_insensitive=kwargs.pop("case", True),
            activity=kwargs.pop("activity", None),
            command_prefix=kwargs.pop("prefix", "!")
        )

        self.sqlite = sqlite
        self.db = kwargs.pop("db", None)
        self.start_time = None
        self.app_info = None
        self.config = config
        self.logger = logger
        self.loop.create_task(self.get_start_time())
        self.loop.create_task(self.load_extensions())


    async def get_start_time(self):
        await self.wait_until_ready()
        self.start_time = datetime.datetime.utcnow()

    async def load_extensions(self):
        await self.wait_until_ready()
        await asyncio.sleep(1)

        # Credits to Lucy (looselystyled#7626)
        # For most of the logic behind cog loading
        cogs = Path("./cogs")
        for cog in cogs.iterdir():
            if cog.is_dir():
                continue

            elif cog.stem == "database" and not self.db:
                continue

            if cog.suffix == ".py" and cog.stem != "__init__":
                path = ".".join(cog.with_suffix("").parts)
                try:
                    self.load_extension(path)
                    print(f"Loaded {path:>29}!")
                    logger.info(f"Loaded {path}")
                except Exception as e:
                    logger.exception(f"Failed to load {path}")
                    print(f"Failed to load {path:>22}!")
                    print(e, "\n")

    async def logout(self):
        await super().logout()


def run():
    desc = botconfig.get("description")
    prefix = botconfig.get("default_prefix")
    token = secrets["bot_token"]

    bot_kwargs = {
        "prefix": prefix,
        "description": desc
    }

    mybot = MyBot(**bot_kwargs)

    if not token or token == "none":
        logger.critical("No token given, add your token in config.ini!")
        sys.exit(1)

    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(mybot.start(token))
    except discord.LoginFailure:
        logger.critical("Invalid token used!")
        loop.run_until_complete(mybot.logout())
    except KeyboardInterrupt:
        logger.warning("Bot was forcefully closed!")
        loop.run_until_complete(mybot.logout())
    finally:
        sys.exit(1)

if __name__ == "__main__":
    os.system("CLS")
    run()

import os
import sys
import logging
import asyncio
import traceback
import datetime
import configparser
from pathlib import Path
from typing import List, Callable, Union, Any

import discord
from discord.ext import commands

from utils import database_manager as sqlite
 
# Read configs
config = configparser.ConfigParser()
config.read("config.ini")
secrets = config["Secrets"]
botconfig = config["Bot"]

# make sure the logs directory exists
Path("./logs").mkdir(exist_ok=True)

# Set up logging
today_formatted = datetime.datetime.today().strftime("%B %d, &Y")
logger = logging.getLogger("discord")
logger.setLevel(logging.INFO)
handler = logging.FileHandler(
    filename=f"logs/discord {today_formatted}.log",
    encoding="utf-8", mode="a"
)
handler.setFormatter(logging.Formatter(
    "%(asctime)s:%(levelname)s:%(name)s: %(message)s"))
logger.addHandler(handler)

SYNC = 0
ASYNC = 1

class Prefixer:
    """Class used to fetch guild-based prefixes"""
    def __init__(self):
        self.default = botconfig.get("default_prefix")
        self.prefix = self.startup()


    def startup(self) -> dict:
        """Loads all saved prefixes to memory, including given default prefix from config"""
        rows =  sqlite.sync_fetchall("SELECT * FROM prefixes")

        prefix_dict = dict()
        for row in rows:
            guild = row[0]
            prefix = row[1]
            
            if guild in prefix_dict:
                if prefix in prefix_dict[guild]:
                    continue
                else:
                    prefix_dict[guild].append(prefix)
            else:
                prefix_dict[guild] = [self.default, prefix]

        for prefixlist in prefix_dict.values():
            prefixlist.sort(reverse=True)

        return prefix_dict


    async def add_prefix(self, guild: int, prefix: str):
        """Async method to add a prefix to db, and memory"""
        await sqlite.execute("""
        INSERT OR IGNORE INTO prefixes(guild, prefix)
        VALUES (?, ?);""", [guild, prefix])

        if guild in self.prefix:
            self.prefix[guild].append(prefix)
        else:
            self.prefix[guild] = [prefix, self.default]

        # Sorts the prefixes to avoid conflic with sub-string based prefixes like ! and !!
        self.prefix[guild].sort(reverse=True)


    def get_prefix(self, bot: commands.Bot, message: discord.Message) -> List[str]:
        """Allows for bot mentions and default prefix in dms, else mentions and stored prefix to guild id"""
        if message.guild is None:
            return commands.when_mentioned_or(self.default)(bot, message)

        prefixes = self.fetch_prefix(message.guild.id)
        return commands.when_mentioned_or(*prefixes)(bot, message)


    def fetch_prefix(self, guild: int) -> List[str]:
        return self.prefix.get(guild, [self.default])


    async def remove_prefix(self, guild: int, prefix: str):
        """Removes prefix from db and memory"""
        if guild not in self.prefix:
            return

        if prefix not in self.prefix[guild]:
            return

        try:
            await sqlite.execute("""
            DELETE FROM prefixes
                WHERE guild = ? AND prefix = ?
            """, [guild, prefix])
        except Exception as e:
            logger.exception(e)

        if guild in self.prefix:
            try:
                self.prefix[guild].remove(prefix)
            except ValueError:
                logger.exception("Tried to remove non existing prefix")



class MyBot(commands.AutoShardedBot):
    def __init__(self, **kwargs: Union[str, Prefixer]):
        super().__init__(
            description=kwargs.pop("description", ""),
            case_insensitive=kwargs.pop("case", True),
            activity=kwargs.pop("activity", None),
            command_prefix=kwargs.get("prefix").get_prefix
        )

        self.sqlite = sqlite
        self.ENCRYPTKEY = kwargs.pop("enckey")
        self.db = kwargs.pop("db", None)
        self.start_time = None
        self.app_info = None
        self.config = config
        self.logger = logger
        self.blacklisted_channels = dict()
        self.prefixer = kwargs.pop("prefix")
        self.loop.create_task(self.get_start_time())
        self.loop.create_task(self.load_extensions())


    async def get_start_time(self):
        """Saves the current datetime object of when the bot is ready and online"""
        await self.wait_until_ready()
        self.start_time = datetime.datetime.utcnow()

    async def load_extensions(self):
        """ 
        Gets the cogs directory relative to the script, and loads all scripts within
        Iterates through the directroy, it does not recursively go through deeper levels of the dir

        Only adds the database cog if a database is present internally
        then loads the rest of the scripts, exceptions can be put into a directory or added as a continue condition
        """

        # Credits to Lucy (looselystyled#7626)
        # For most of the logic behind this cog loader
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
                    print(f"{'Loaded...':<19} {path:<1}!")
                    logger.info(f"Loaded {path}")
                except Exception as e:
                    logger.exception(f"Failed to load {path}")
                    print(f"{'Failed to load...':<19} {path:<1}!")
                    print(e, "\n")


    def update(self, minute :int, method: Callable, *args: Any, **kwargs: Any):
        """Runs a method every x minutes with passed args and kwargs"""

        async def _update(minute:int, method: Callable, *args, **kwargs):
            sec = minute * 60
            
            # Checks if the method given is a courotine or not.
            state = ASYNC if asyncio.iscoroutinefunction(method) else SYNC
            while True:
                await asyncio.sleep(sec)

                if state == SYNC:
                    try:
                        method(*args, **kwargs)
                    except Exception:
                        logger.exception("Update raised an exception with "
                                         f"method {method.__name__}\n"
                                         f"args {args}, kwargs {kwargs}")

                elif state == ASYNC:
                    try:
                        await method(*args, **kwargs)
                    except Exception:
                        logger.exception("Update raised an exception with "
                                        f"method {method.__name__}\n"
                                        f"args {args}, kwargs {kwargs}")

        self.loop.create_task(_update(minute, method, *args, **kwargs))
            


    async def logout(self):
        #Close other connections and tasks here like a database
        await super().logout()



def run():
    """Loads configs needed to run the bot"""

    desc = botconfig.get("description")
    token = secrets["bot_token"]
    enc_key = config["Database"].get("encrypt_key").encode('ASCII')
    bot_kwargs = {
        "description": desc,
        "prefix": Prefixer(),
        "enckey": enc_key
    }

    mybot = MyBot(**bot_kwargs)

    if not token or token == "none":
        logger.critical("No token given, add your token in config.ini!")
        print("No token given, add your token in config.ini!")
        sys.exit(1)

    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(mybot.start(token))
    except discord.LoginFailure:
        logger.critical("Invalid token used!")
        print("Invalid token used!")
        loop.run_until_complete(mybot.logout())
    except KeyboardInterrupt:
        logger.warning("Bot was forcefully closed!")
        loop.run_until_complete(mybot.logout())
    finally:
        sys.exit(1)



if __name__ == "__main__":
    os.system("CLS")
    sqlite.make_sure_tables_exist()
    run()

import discord
from discord.ext import commands

class Events:
    def __init__(self, bot):
        self.bot = bot

    async def on_connect(self):
        pass

    async def on_ready(self):
        self.bot.app_info = await self.bot.application_info()
        print("-" * 10)
        print(f"Logged in as: {self.bot.user.name}\n"
              f"Using discord.py version: {discord.__version__}\n"
              f"Owner: {self.bot.app_info.owner}\n")
        print("-" * 10)

    async def on_resumed(self):
        pass

    async def on_typing(self, channel, user, when):
        pass

    async def on_message(self, message):
        pass

    async def on_message_delete(self, message):
        pass

    async def on_message_edit(self, before, after):
        pass

    async def on_reaction_add(self, reaction, user):
        pass

    async def on_reaction_remove(self, reaction, user):
        pass

    async def on_guild_channel_delete(self, channel):
        pass

    async def on_guild_channel_create(self, channel):
        pass

    async def on_guild_channel_pins_update(self, channel, last_pin):
        pass

    async def on_member_join(self, member):
        pass

    async def on_member_remove(self, member):
        pass

    async def on_member_update(self, b, a):
        pass

    async def on_guild_join(self, guild):
        pass

    async def on_guild_update(self, before, after):
        pass

    async def on_guild_role_create(self, role):
        pass

    async def on_guild_role_delete(self, role):
        pass

    async def on_guild_role_update(self, before, after):
        pass

    async def on_guild_emojis_update(self, guild, before, after):
        pass

    async def on_member_ban(self, guild, user):
        pass

    async def on_member_unban(self, guild, user):
        pass


def setup(bot):
    bot.add_cog(Events(bot))

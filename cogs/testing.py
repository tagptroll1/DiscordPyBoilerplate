from pathlib import Path

import discord
from discord.ext import commands

class MyError(Exception):
    pass

class Test:
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.sqlite

    @commands.command()
    async def ping(self, ctx):
        await ctx.send("Pong!")
    
    @commands.command()
    async def table(self, ctx, *, query):
        await self.db.execute(query)
        await ctx.message.add_reaction("👌")

    @commands.command()
    async def insert(self, ctx, *, text):
        query = """INSERT INTO test(text) VALUES (?)"""
        await self.db.execute(query, [text])
        await ctx.message.add_reaction("👌")


    @commands.command()
    async def getall(self, ctx):
        query = """SELECT * FROM test"""
        rows = await self.db.fetchall(query)

        mylist = []
        for row in rows:
            mylist.append(" ".join([str(x) for x in row]))

        await ctx.send(embed=discord.Embed(
            title=f"Rows of test",
            description="\n".join(mylist)
        ))

    @commands.command()
    async def play(self, ctx):
        try:
            channel = ctx.author.voice.channel
        except AttributeError:
            return

        if channel:
            voice_client = await channel.connect()
        else:
            return

        if voice_client.is_playing():
            voice_client.stop()

        try:
            voice_client.play(discord.FFmpegPCMAudio("cogs/testsong.mp3"))
        except Exception as e:
            print(e)

        


    @commands.command(name="raise")
    async def raise_my_error(self, ctx):
        raise MyError("Whopsie")

    async def on_command_error(self, ctx, error):
        print(error, type(error))
        print(error.__cause__, type(error.__cause__))
        print(isinstance(error, MyError))
        print(isinstance(error.__cause__, MyError))




def setup(bot):
    bot.add_cog(Test(bot))

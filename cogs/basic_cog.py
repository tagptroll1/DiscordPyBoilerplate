from discord.ext import commands


class BasicCog:
    def __init__(self, bot):
        self.bot = bot
        self.bot.loop.create_task(self.api_tasks())

    async def api_tasks(self):
        """Any API related calls should be done here.
        This is to avoid errors related to not waiting for on_ready
        to trigger before loading cogs
        """
        await self.bot.wait_until_ready()
        # Api / async tasks go here

    async def __local_check(self, ctx):
        """I'm a local check that will be run on all commands in this cog!"""

    async def __before_invoke(self, ctx):
        """I will be called before any commands will be invoked in this cog!"""

    async def __after_invoke(self, ctx):
        """I will be called after a command was executed in this cog!"""

    def __unload(self):
        """I will clean up stuff!"""

    def __error(self, ctx, error):
        """I'm an error handler!"""

    @commands.command()
    async def command_template(self, ctx):
        await ctx.send("Test")


def setup(bot):
    bot.add_cog(BasicCog(bot))

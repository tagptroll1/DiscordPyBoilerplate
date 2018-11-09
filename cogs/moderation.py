import asyncio
from datetime import datetime
from textwrap import dedent

import discord
from discord.ext import commands

from utils import database_manager as db


class Moderator:
    """A cog for members with the administrator permission
    """

    def __init__(self, bot):
        self.bot = bot

    async def __local_check(self, ctx):
        return ctx.author.guild_permissions.administrator

    @commands.command(name="prefix")
    async def add_prefix(self, ctx, *, prefix: str):
        """Adds a custom prefix to the guild.
        The default prefix set in configs will always be availabel

        NOTE:   It's adviced to use "" around prefixes with
                leading or trailing whitespace!

        prefix -- string to be used as a new prefix for the guild
        """
        await self.bot.prefixer.add_prefix(ctx.guild.id, prefix)
        query = """
        INSERT OR IGNORE INTO prefixes(guild, prefix)
        VALUES (?, ?);"""
        await db.execute(query, [ctx.guild.id, prefix])
        await ctx.message.add_reaction("👌")
        self.bot.logger.info(
            f"{str(ctx.author)} added {prefix} to {ctx.guild.name}"
        )

    @commands.command(name="prefixes")
    async def fetch_prefixes(self, ctx):
        """Fetches all available prefixes for the guild.
        Also fetches the default prefix in configs
        """
        guild = ctx.guild.id
        prefixes = self.bot.prefixer.fetch_prefix(guild)
        prefixes = ", ".join(prefixes)
        await ctx.send(f"Prefixes available on this server are: `{prefixes}`")

    @commands.command(aliases=["deleteprefix"])
    async def removeprefix(self, ctx, prefix: str):
        if prefix == self.bot.prefixer.default:
            await ctx.send("Can't delete default prefix!")
            return

        if prefix in self.bot.prefixer.fetch_prefix(ctx.guild.id):
            await self.bot.prefixer.remove_prefix(ctx.guild.id, prefix)
            await ctx.message.add_reaction("👌")
            self.bot.logger.info(
                f"{str(ctx.author)} removed {prefix} from {ctx.guild.name}"
            )
            return

        await ctx.send("Prefix not in my list..")

    @commands.group(name="blacklist")
    async def blacklist_group(self, ctx):
        pass

    @blacklist_group.command(name="add", aliases=["append", "set"])
    async def add_blacklist(self, ctx, channel: discord.TextChannel = None):
        channel = channel or ctx.channel

        await db.execute("""
            INSERT OR IGNORE INTO blacklistedchannels(
                channelid,
                guildid,
                date,
                setbyid
            ) VALUES (?, ?, ?, ?);
        """, [channel.id, ctx.guild.id, datetime.utcnow(), ctx.author.id])

        self.bot.blacklisted_channels.add(channel.id)
        await ctx.message.add_reaction("🔨")
        self.bot.logger.info(
            f"{str(ctx.author)} added a blacklist to {channel.name} "
            f"in the guild {ctx.guild.name}"
        )

    @blacklist_group.command(name="remove", aliases=["delete", "pop"])
    async def remove_blacklist(self, ctx, channel: discord.TextChannel = None):
        channel = channel or ctx.channel

        try:
            self.bot.blacklisted_channels.remove(channel.id)
        except KeyError:
            await ctx.send("This channel is not blacklisted!")
            return

        await db.execute("""
            DELETE FROM blacklistedchannels
                WHERE channelid = ?
                AND guildid = ?;
        """, [channel.id, ctx.guild.id])

        await ctx.message.add_reaction("🔧")
        self.bot.logger.info(
            f"{str(ctx.author)} removed a blacklist from {channel.name} "
            f"in the guild {ctx.guild.name}"
        )

    @blacklist_group.command(name="get")
    async def get_blacklisted(self, ctx):

        rows = await db.fetchall("""
            SELECT channelid, date, setbyid
                FROM blacklistedchannels
                WHERE guildid = ?;
        """, [ctx.guild.id])

        embed = discord.Embed(title="Blacklisted channels")
        channels = []
        for row in rows:
            channel = ctx.guild.get_channel(row[0])
            date = row[1].strftime("%d.%m.%y")
            author = ctx.guild.get_member(row[2])
            channels.append(f"{date} - #{channel}; Set by{author.mention}")

        if channels:
            channels = "\n\t-".join(channels)
            embed.description = (
                "__List of TextChannels blacklisted on this server.__\n"
                f"\t-{channels}"
            )
        else:
            embed.description = "No TextChannels blacklisted on this server."

        await ctx.send(embed=embed)

    @commands.command()
    async def cleartable(self, ctx, table: str):
        await db.execute(
            f"DELETE FROM {table} where guildid = ?;", [ctx.guild.id]
        )
        await ctx.message.add_reaction("🔨")
        self.bot.logger.warning(
            f"{(ctx.author)} wiped data for the guild {ctx.guild.name}"
        )

    @commands.command()
    @commands.is_owner()
    async def droptable(self, ctx, table: str):
        await db.execute(f"DROP TABLE IF EXISTS {table}")
        await ctx.message.add_reaction("🔨")
        self.bot.logger.warning(
            f"Owner dropped the table {table}, if it existed"
        )

    @commands.command()
    async def warn(self, ctx, user: discord.Member, *, reason: str = None):
        await db.execute("""
            INSERT INTO warnings(guildid, userid)
                VALUES (?, ?);
        """, [ctx.guild.id, user.id])

        rows = await db.fetchall("""
            SELECT id FROM warnings
                WHERE userid = ? AND guildid = ?;
        """, [user.id, ctx.guild.id])
        if reason:
            warning = f"You have been warned in {ctx.guild.name}\n{reason}"
        else:
            warning = f"You have been warned in {ctx.guild.name}"
        await user.send(f"{warning}, you have been warned {len(rows)} times")

        embed = discord.Embed()
        if reason:
            warn = f"[{reason}]"
        else:
            warn = ""
        embed.set_author(
            name=f"🔨 Warned {str(user)} {warn}",
            icon_url=user.avatar_url
        )

        if len(rows) > 1:
            countstr = f"This is your {len(rows)}. warning"
        else:
            countstr = f"This is your first warning"
        embed.set_footer(text=countstr)
        embed.colour = 0xff0000
        await ctx.send(embed=embed)

    @commands.command()
    @commands.bot_has_permissions(kick_members=True)
    async def kick(self, ctx, to_kick: discord.Member, *, reason=None):
        reason = reason or f"Kicked by {ctx.author.name}"
        try:
            await to_kick.send(
                "You've been kicked from "
                f"{ctx.guild.name} by {str(ctx.author)}"
            )
            await asyncio.sleep(0.2)
        except discord.Forbidden:
            pass

        try:
            await to_kick.kick(reason=reason)
        except discord.HTTPException:
            self.bot.logger.exception(f"Kicking failed for {str(to_kick)}")
            return await ctx.send("Kicking has failed. Please try again!")

        await ctx.send(f"{ctx.author.mention} has kicked {to_kick.mention}")
        await ctx.message.add_reaction("🔨")
        self.bot.logger.info(
            f"{str(ctx.author)} has kicked {str(to_kick)}"
            f" from the guild {ctx.guild.name}")

    @commands.command()
    @commands.bot_has_permissions(ban_members=True)
    async def ban(self, ctx, to_ban: discord.Member, *, reason: str = None):
        try:
            member = await commands.MemberConverter().convert(ctx, to_ban)
            try:
                await member.send(
                    "You've been banned from "
                    f"{ctx.guild.name} by {str(ctx.author)}"
                )
                await asyncio.sleep(0.2)
            except discord.Forbidden:
                pass
        except Exception:
            try:
                ban_id = int(to_ban)
                member = discord.Object(id=ban_id)
            except TypeError:
                return ctx.send("Int not provided for hack ban to work")

        reason = reason or f"Banned by {str(ctx.author)}"
        try:
            await ctx.guild.ban(member, reason=reason)
        except discord.HTTPException:
            self.bot.logger.exception(f"Banning failed for {str(member)}")
            return await ctx.send("Banning has failed. Please try again!")

        if hasattr(member, "name"):
            await ctx.send(f"{ctx.author.mention} has banned {str(member)}")
        else:
            await ctx.send(
                f"{ctx.author.mention} has banned the id {member.id}"
            )
        await ctx.message.add_reaction("🔨")
        self.bot.logger.info(
            f"{str(ctx.author)} has banned {str(member)}"
            f" from the guild {ctx.guild.name}")

    @commands.command()
    @commands.bot_has_permissions(ban_members=True)
    async def unban(self, ctx, to_ban: int, *, reason: str = None):
        member = discord.Object(id=to_ban)

        reason = reason or f"Unbanned by {ctx.author.name}"
        try:
            await ctx.guild.unban(member, reason=reason)
        except discord.HTTPException:
            self.bot.logger.exception(
                f"Unbanning for the id {to_ban} has failed"
            )
            return await ctx.send("Unbanning has failed. Please try again!")

        await ctx.send(f"{ctx.author.mention} has unbanned the id {member.id}")
        await ctx.message.add_reaction("🔧")
        self.bot.logger.info(
            f"{str(ctx.author)} has unbanned {member.id}"
            f" from the guild {ctx.guild.name}")

    @commands.command()
    @commands.bot_has_permissions(ban_members=True)
    async def softban(
        self, ctx, to_ban: discord.Member, *, reason: str = None
    ):
        reason_msg = f"Reason: {reason}\n" if reason else ""
        msg = dedent(f"""
        You have been softbanned from {ctx.guild.name} by {str(ctx.author)}
        {reason_msg}
        What does this mean to you?
        \t>You have been kicked from the server
        \t>Your recent messages have been deleted
        \t>You *may* rejoin the server, but please behave""")

        try:
            await to_ban.send(embed=discord.Embed(description=msg))
            await asyncio.sleep(0.2)
        except discord.Forbidden:
            pass

        reason = reason or f"kicked by {str(ctx.author)} (Soft ban)"
        try:
            await to_ban.ban(reason=reason)
            await to_ban.unban(reason="Soft ban")
        except discord.HTTPException:
            self.bot.logger.exception(f"Soft ban failed for {str(to_ban)}")
            return await ctx.send("Kicking has failed. Please try again!")

        await ctx.send(f"{ctx.author.mention} has kicked {to_ban.mention}")
        await ctx.message.add_reaction("🔨")
        self.bot.logger.info(
            f"{str(ctx.author)} has softbanned "
            f"{str(to_ban)} from {ctx.guild.name}"
        )

    @commands.command()
    async def voicemute(self, ctx, member: discord.Member):
        await member.edit(mute=True)
        await ctx.message.add_reaction("🔨")
        self.bot.logger.info(
            f"{str(ctx.author)} has voice muted "
            f"{str(member)} in {ctx.guild.name}"
        )

    @commands.command()
    async def voiceunmute(self, ctx, member: discord.Member):
        await member.edit(mute=False)
        await ctx.message.add_reaction("🔧")
        self.bot.logger.info(
            f"{str(ctx.author)} has voice unmuted "
            f"{str(member)} in {ctx.guild.name}"
        )

    @commands.command()
    async def voicedeafen(self, ctx, member: discord.Member):
        await member.edit(deafen=True)
        await ctx.message.add_reaction("🔨")
        self.bot.logger.info(
            f"{str(ctx.author)} has voice deafened "
            f"{str(member)} in {ctx.guild.name}"
        )

    @commands.command()
    async def voiceundeafen(self, ctx, member: discord.Member):
        await member.edit(deafen=False)
        await ctx.message.add_reaction("🔧")
        self.bot.logger.info(
            f"{str(ctx.author)} has voice un-deafened "
            f"{str(member)} in {ctx.guild.name}"
        )

    @commands.command()
    @commands.bot_has_permissions(manage_roles=True)
    async def mute(self, ctx, member: discord.Member, *, reason: str = None):
        _reason = f"{member} has been permanently muted. "
        if reason:
            _reason += f"Reason: *{reason}*"

        _mute_role = discord.utils.get(ctx.guild.roles, name="Muted")

        if not _mute_role:
            param = {
                "name": "Muted",
                "permissions": discord.Permissions.none(),
                "reason": "To mute members"
            }
            try:
                await ctx.guild.create_role(**param)
            except discord.Forbidden:
                await ctx.send(
                    "I require manage roles permissions "
                    "to create required role"
                )
                return

        # TODO: come up with system to prevent messages being sent by muted
        # TODO: Controll all roles to make sure no other roles override mute

        await member.add_roles(_mute_role, reason=_reason)
        await ctx.send(_reason)
        self.bot.logger.info(
            f"{_reason}. Mute by: {str(ctx.author)}"
        )

    @commands.group()
    async def clear(self, ctx):
        pass


def setup(bot):
    bot.add_cog(Moderator(bot))

import asyncio

import discord
from discord.ext import commands

from utils.color_manager import random_hue_color
from utils.embeder import short_message

class RoleManager:
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    def __local_check(self, ctx) -> bool:
        if not ctx.guild:
            return False
        if not ctx.guild.me.guild_permissions.manage_roles:
            return False
        return True
    # Check end

    @commands.has_permissions(manage_roles=True)
    @commands.group(name="role")
    async def role_group(self, ctx):
        pass
    # Group end


    @commands.has_permissions(manage_roles=True)
    @role_group.command(name="add")
    async def role_add(self, ctx, *, name: str):
        role_get = discord.utils.get(ctx.guild.role_hierarchy, name=name)
        
        if role_get:
            msg = f"Role with name {name} already exists"
            return await ctx.send(embed=short_message(msg, colour=role_get.colour,
                                                      icon=self.bot.user.avatar_url))


        reason = f"{str(ctx.author)} has created the role {name}"
        fields = {
            "permissions": discord.Permissions().general(),
            "colour": random_hue_color(),
            "hoist": False,
            "mentionable": True,
            "reason": reason
        }
        try:
            await ctx.guild.create_role(name=name, **fields)
        except discord.HTTPException:
            self.bot.logger.exception(f"failed to create role {name}")
            msg = f"Something went wrong trying to create the role {name}!"
            return await ctx.send(embed=short_message(msg, icon=ctx.bot.user.avatar_url))

        await ctx.message.add_reaction("👌")
        self.bot.logger.info(reason)
    # Role add end

    @commands.has_permissions(manage_roles=True)
    @role_group.command(name="delete", aliases=["remove", "terminate", "del"])
    async def role_remove(self, ctx, role:discord.Role):
        if ctx.author.top_role < role:
            msg = f"The role {str(role)} is higher in the role hierachy than your top role!"
            return await ctx.send(embed=short_message(msg, colour=role.colour, 
                                                      icon=self.bot.user.avatar_url))

        reason = f"{str(ctx.author)} has removed the role {str(role)}"
        try:
            await role.delete(reason=reason)
        except discord.HTTPException:
            self.bot.logger.exception(f"failed to delete role {str(role)}")
            msg = f"Something went wrong trying to delete the role {str(role)}!"
            return await ctx.send(embed=short_message(msg, colour=role.colour, 
                                                      icon=ctx.bot.user.avatar_url))

        await ctx.message.add_reaction("👌")
        self.bot.logger.info(reason)
    # Role del end

    @commands.has_permissions(manage_roles=True)
    @role_group.command(name="give")
    async def role_give(self, ctx, member: discord.Member, role: discord.Role):
        if ctx.author.top_role < role:
            msg = f"The role {str(role)} is higher in the role hierachy than your top role!"
            return await ctx.send(embed=short_message(msg, colour=role.colour,
                                                      icon=self.bot.user.avatar_url))

        reason = f"{str(ctx.author)} has given the role {str(role)} to {str(member)}"
        try:
            await member.add_roles(role, reason=reason)
        except discord.HTTPException:
            self.bot.logger.exception(f"failed to give role {str(role)} to {str(member)}")
            msg = f"Something went wrong trying to give the role {str(role)} to {str(member)}!"
            return await ctx.send(embed=short_message(msg, colour=role.colour,
                                                      icon=ctx.bot.user.avatar_url))

        await ctx.message.add_reaction("👌")
        self.bot.logger.info(reason)
    # Role give end

    @commands.has_permissions(manage_roles=True)
    @role_group.command(name="take")
    async def role_take(self, ctx, member: discord.Member, role: discord.Role):
        if ctx.author.top_role < role:
            msg = f"The role {str(role)} is higher in the role hierachy than your top role!"
            return await ctx.send(embed=short_message(msg, colour=role.colour,
                                                      icon=self.bot.user.avatar_url))

        reason = f"{str(ctx.author)} has taken the role {str(role)} from {str(member)}"
        try:
            await member.remove_roles(role, reason=reason)
        except discord.HTTPException:
            self.bot.logger.exception(f"failed to take role {str(role)} from {str(member)}")
            msg = f"Something went wrong trying to take the role {str(role)} from {str(member)}!"
            return await ctx.send(embed=short_message(msg, colour=role.colour,
                                                      icon=ctx.bot.user.avatar_url))

        await ctx.message.add_reaction("👌")
        self.bot.logger.info(reason)
    # Role Take end

    @commands.command(name="iam")
    async def i_am_role(self, ctx, role: discord.Role):
        if ctx.author.top_role < role:
            msg = f"The role {str(role)} is higher in the role hierachy than your top role!"
            return await ctx.send(embed=short_message(msg, colour=role.colour,
                                                      icon=self.bot.user.avatar_url))

        if role.permissions > ctx.author.guild_permissions:
            msg = f"The role {str(role)} has more permissions than you have!"
            return await ctx.send(embed=short_message(msg, colour=role.colour,
                                                      icon=self.bot.user.avatar_url))

        reason = f"{str(ctx.author)} has given himself the role {str(role)}"
        try:
            await ctx.author.add_roles(role, reason=reason)

        except discord.Forbidden:
            error = f"Tried to give role to member higher in hierarchy"
            msg = "You're higher in the role hierarchy than me, I can't apply roles to you"
            self.bot.logger.exception(error)
            return await ctx.send(embed=short_message(msg, colour=role.colour,
                                                      icon=ctx.bot.user.avatar_url))

        except discord.HTTPException:
            self.bot.logger.exception(f"{str(ctx.author)} failed to give himself role {str(role)}")
            msg = f"Something went wrong trying to give you the role {str(role)}!"
            return await ctx.send(embed=short_message(msg, colour=role.colour,
                                                      icon=ctx.bot.user.avatar_url))

        await ctx.message.add_reaction("👌")
        self.bot.logger.info(reason)
    # I am role end

    @commands.command(name="iamnot")
    async def i_am_not_role(self, ctx, role: discord.Role):
        if ctx.author.top_role == role:
            msg = f"This is your top role, are you sure you wan't to remove {str(role)}"
            embed = await ctx.send(embed=short_message(msg, colour=role.colour,
                                                       icon=ctx.bot.user.avatar_url))
            await embed.add_reaction("👍")
            await embed.add_reaction("👎")

            def check(r, u):
                if r.emoji not in ("👎", "👍"):
                    return False
                if u is not ctx.author:
                    return False
                if r.message != embed:
                    return False
                return True

            try:
                r, _ = self.bot.wait_for("reaction_add", check=check, timeout=30)
            except asyncio.TimeoutError:
                await embed.delete()
                return
            
            if r.emoji == "👎":
                await embed.delete()
                return
            else:
                await embed.delete()

        reason = f"{str(ctx.author)} removed the role {str(role)} from himself"
        try:
            await ctx.author.remove_roles(role, reason=reason)

        except discord.Forbidden:
            error = f"Tried to take role from member higher in hierarchy"
            msg = "You're higher in the role hierarchy than me, I can't remove roles from you"
            self.bot.logger.exception(error)
            return await ctx.send(embed=short_message(msg, colour=role.colour,
                                                      icon=ctx.bot.user.avatar_url))

        except discord.HTTPException:
            self.bot.logger.exception(f"{str(ctx.author)} failed to remove role {str(role)}")
            msg = f"Something went wrong trying to remove the role {str(role)}"
            return await ctx.send(embed=short_message(msg, colour=role.colour,
                                                      icon=ctx.bot.user.avatar_url))

        await ctx.message.add_reaction("👌")
        self.bot.logger.info(reason)
    # I am not role end

    # Permissions
    @commands.group(name="permissions")
    async def role_permission(self, ctx):
        pass
    # permissions group end

    @commands.has_permissions(manage_roles=True)
    @role_permission.command(name="add")
    async def add_permission(self, ctx, role: discord.Role, *, argument: str):
        perm = role.permissions
        argsum = sum(1 for arg in argument.split("="))
        if argsum <= 1:
            await ctx.send(embed=short_message("Invalid use!"), icon=ctx.bot.user.avatar_url)
        elif argsum >= 3:
            await ctx.send(embed=short_message("Too many arguments!", icon=ctx.bot.user.avatar_url))
        pass
    # add permissions end

    @commands.has_permissions(manage_roles=True)
    @role_permission.command(name="remove")
    async def remove_permission(self, ctx, role: discord.Role, *, argument: str):
        perm = role.permissions
        pass
    # remove permissions end

    @commands.has_permissions(manage_roles=True)
    @role_permission.command(name="edit")
    async def edit_permission(self, ctx, role: discord.Role, *, argument: str):
        perm = role.permissions
        pass
    # edit permissions end

def setup(bot):
    bot.add_cog(RoleManager(bot))

import discord

from utils.color_manager import random_hue_color


def short_message(msg, colour=None, icon=None):
    colour = colour or random_hue_color()
    embed = discord.Embed(colour=colour)
    if icon:
        embed.set_author(name=msg, icon_url=icon)
        return embed

    embed.set_author(name=msg)
    return embed

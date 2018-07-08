import colorsys
import random

import discord


def random_hue_color():
    values = [int(x * 255) for x in colorsys.hsv_to_rgb(random.random(), 1, 1)]
    return discord.Color.from_rgb(*values)

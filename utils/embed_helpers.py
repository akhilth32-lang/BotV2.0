# utils/embed_helpers.py

import discord
from config.emoji import EMOJIS
from datetime import datetime

def create_embed(title: str = None, description: str = None, color: discord.Color = discord.Color.blue()):
    """Helper to create a standard discord embed with optional title, description, and color."""
    embed = discord.Embed(title=title, description=description, color=color)

    # Format: Today at hh:mm AM/PM
    now = datetime.now()
    formatted_time = now.strftime("Today at %I:%M %p")

    embed.set_footer(text=formatted_time)
    return embed

def add_field(embed: discord.Embed, name: str, value: str, inline: bool = True):
    embed.add_field(name=name, value=value, inline=inline)
    return embed

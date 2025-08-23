# utils/embed_helpers.py

import discord
from config.emoji import EMOJIS

def create_embed(title: str = None, description: str = None, color: discord.Color = discord.Color.blue()):
    """Helper to create a standard discord embed with optional title, description, and color."""
    embed = discord.Embed(title=title, description=description, color=color)
    embed.set_footer(text="Legend League Bot")
    return embed

def add_field(embed: discord.Embed, name: str, value: str, inline: bool = True):
    embed.add_field(name=name, value=value, inline=inline)
    return embed
    

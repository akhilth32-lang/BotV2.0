# utils/discord_helpers.py

import discord

def get_guild_by_name(client: discord.Client, guild_name: str) -> discord.Guild:
    """Return the guild object matching the given guild name."""
    return discord.utils.find(lambda g: g.name == guild_name, client.guilds)

def create_simple_embed(title: str, description: str, color=discord.Color.blue()) -> discord.Embed:
    """Create a basic Discord embed with title, description, and color."""
    embed = discord.Embed(title=title, description=description, color=color)
    embed.set_footer(text="Legend League Bot")
    return embed

async def send_dm(user: discord.User, content: str = None, embed: discord.Embed = None):
    """Send a direct message (DM) to a user."""
    if not user.dm_channel:
        await user.create_dm()
    await user.dm_channel.send(content=content, embed=embed)
  

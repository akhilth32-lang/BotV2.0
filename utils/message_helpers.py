# utils/message_helpers.py

import discord
from config.emoji import EMOJIS


async def send_typing_message(channel: discord.TextChannel, message: str):
    """Send typing indicator before sending a message to simulate natural typing."""
    async with channel.typing():
        await channel.send(message)


async def send_embed_message(channel: discord.TextChannel, title: str, description: str, color=discord.Color.blue()):
    """Send an embed with the given title, description, and color."""
    embed = discord.Embed(title=title, description=description, color=color)
    await channel.send(embed=embed)


async def send_success(interaction: discord.Interaction, message: str, ephemeral: bool = False):
    """Send a success message with tick emoji and green color."""
    embed = discord.Embed(description=f"{EMOJIS['tick']} {message}", color=discord.Color.green())
    await interaction.response.send_message(embed=embed, ephemeral=ephemeral)


async def send_failure(interaction: discord.Interaction, message: str, ephemeral: bool = True):
    """Send a failure message with failed emoji and red color."""
    embed = discord.Embed(description=f"{EMOJIS['failed']} {message}", color=discord.Color.red())
    await interaction.response.send_message(embed=embed, ephemeral=ephemeral)
                       

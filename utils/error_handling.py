# utils/error_handling.py

import discord
from config.emoji import EMOJIS
from utils.embed_helpers import create_embed

async def send_error_message(interaction: discord.Interaction, message: str):
    embed = create_embed(
        title=f"{EMOJIS['failed']} Error",
        description=message,
        color=discord.Color.red()
    )
    await interaction.followup.send(embed=embed, ephemeral=True)
    

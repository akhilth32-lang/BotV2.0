# extensions/link_profile.py

import discord
from discord import app_commands
from discord.ext import commands
from database import player_crud
from config.emoji import EMOJIS
from utils.embed_helpers import create_embed
import random

# Replace these URLs with your actual hosted profile photo URLs
PROFILE_PHOTOS = [
    "profile1.png",
    "profile2.png",
    "profile3.png",
]

class LinkProfile(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="link_profile",
        description="Show all linked Clash of Clans accounts for a Discord user"
    )
    @app_commands.describe(discord_user="Optional Discord user to view linked accounts (defaults to you)")
    async def link_profile(self, interaction: discord.Interaction, discord_user: discord.Member = None):
        await interaction.response.defer()

        user = discord_user or interaction.user
        linked_players = await player_crud.get_linked_players_by_discord(user.id)

        if not linked_players:
            embed = create_embed(
                title=f"{EMOJIS['warning']} No Linked Accounts",
                description=f"No Clash of Clans accounts linked to {user.mention}.({user.id})",
                color=discord.Color.dark_theme()
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
            return

        # Select a random profile photo URL for this user (or you may choose a deterministic one)
        random_photo_url = random.choice(PROFILE_PHOTOS)

        description_lines = []
        for player in linked_players:
            name = player.get("player_name", "Unknown")
            tag = player.get("player_tag", "N/A")
            discord_id = player.get("discord_id")

            th_level = player.get("townhall", "?")
            th_emoji = EMOJIS.get("townhall", "🏠")

            legend_league_emoji = EMOJIS.get("legend_league", "🏆")  # Your legend league emoji

            trophies = player.get("trophies", 0)

            # Format line like:
            # 1. <:th17:1409068038107697255> • **AKHIL**   |<:legend:1399752114653233322> 5321  (#8UQQL8VU8)
            line = f"{th_emoji} • **{name}**  | {legend_league_emoji} {trophies}  ({tag})"
            description_lines.append(line)

        embed = create_embed(
            title=f"Player Profile - {user.display_name}",
            description="\n".join(description_lines),
            color=discord.Color.dark_theme()
        )

        embed.set_thumbnail(url=random_photo_url)
        embed.set_footer(text="Clash on! 🔥")

        await interaction.followup.send(embed=embed, ephemeral=False)


async def setup(bot):
    await bot.add_cog(LinkProfile(bot))
    

# extensions/link_profile.py

import discord
from discord import app_commands
from discord.ext import commands
from database import player_crud
from config.emoji import EMOJIS
from utils.embed_helpers import create_embed


class LinkProfile(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="link_profile", description="Show all linked Clash of Clans accounts for a Discord user")
    @app_commands.describe(discord_user="Optional Discord user to view linked accounts (defaults to you)")
    async def link_profile(self, interaction: discord.Interaction, discord_user: discord.Member = None):
        await interaction.response.defer()

        user = discord_user or interaction.user
        linked_players = await player_crud.get_linked_players_by_discord(user.id)

        if not linked_players:
            embed = create_embed(
                title=f"{EMOJIS['warning']} No Linked Accounts",
                description=f"No Clash of Clans accounts linked to {user.mention}.",
                color=discord.Color.dark_theme()
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
            return

        description_lines = []
        for player in linked_players:
            name = player.get("player_name", "Unknown")
            tag = player.get("player_tag", "N/A")
            discord_id = player.get("discord_id")

            # Townhall emoji (fallback if missing)
            th_level = player.get("townHallLevel", "?")
            th_emoji = EMOJIS.get(f"th{th_level}", "🏠")

            line = (
                f"{th_emoji} **{name}** ({tag})\n"
                f"🔗 Linked to Discord ID: `{discord_id}`\n"
            )
            description_lines.append(line)

        embed = create_embed(
            title=f"Linked Accounts for {user.display_name}",
            description="\n".join(description_lines),
            color=discord.Color.dark_theme()
        )
        await interaction.followup.send(embed=embed, ephemeral=False)


async def setup(bot):
    await bot.add_cog(LinkProfile(bot))

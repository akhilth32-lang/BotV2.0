# extensions/link_profile.py

import discord
from discord import app_commands
from discord.ext import commands
from database import player_crud
from config.emoji import EMOJIS
from utils.embed_helpers import create_embed
from config.fonts import to_bold_gg_sans, to_regular_gg_sans

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
                color=discord.Color.orange()
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
            return

        description_lines = []
        for player in linked_players:
            name = to_bold_gg_sans(player.get("player_name", "Unknown"))
            tag = player.get("player_tag", "N/A")
            trophies = player.get("trophies", 0)
            offense = player.get("offense_trophies_change", 0)
            offense_attacks = player.get("offense_attacks", 0)
            defense = player.get("defense_trophies_change", 0)
            defense_defends = player.get("defense_defends", 0)

            offense_display = f"{EMOJIS['offense']} +{offense}/{offense_attacks if offense_attacks != 0 else 0}"
            defense_display = f"{EMOJIS['defense']} {defense}/{defense_defends if defense_defends != 0 else 0}"

            line = (
                f"{name} ({tag})\n"
                f"🏆 {trophies} | {offense_display} | {defense_display}\n"
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

# extensions/leaderboard.py

import discord
from discord import app_commands
from discord.ext import commands
from database import player_crud
from config.emoji import EMOJIS
from utils.embed_helpers import create_embed
from config.fonts import to_bold_gg_sans, to_regular_gg_sans

LEADERBOARD_PAGE_SIZE = 20

class Leaderboard(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="leaderboard", description="Show leaderboard of all linked Clash of Clans player accounts")
    @app_commands.describe(
        page="Page number to view (default 1)",
        color="Embed color in hex (e.g. #000000 for black, default black)",
        day="Legend league day snapshot to view (default current day)"
    )
    async def leaderboard(self, interaction: discord.Interaction, page: int = 1, color: str = "#000000", day: int = 0):
        await interaction.response.defer()

        # Fetch linked players sorted by trophies descending
        all_players = await player_crud.get_all_linked_players()
        # Sort by trophies descending
        sorted_players = sorted(all_players, key=lambda p: p.get('trophies', 0), reverse=True)

        total_pages = (len(sorted_players) + LEADERBOARD_PAGE_SIZE - 1) // LEADERBOARD_PAGE_SIZE
        if page < 1:
            page = 1
        if page > total_pages:
            page = total_pages

        # Paginate users
        start = (page - 1) * LEADERBOARD_PAGE_SIZE
        end = start + LEADERBOARD_PAGE_SIZE
        page_players = sorted_players[start:end]

        description_lines = []
        rank_offset = start
        for idx, player in enumerate(page_players, start=1):
            rank = rank_offset + idx
            name = to_bold_gg_sans(player.get("player_name", "Unknown"))
            tag = player.get("player_tag", "N/A")
            trophies = player.get("trophies", 0)

            offense_change = player.get("offense_trophies_change", 0)
            offense_attacks = player.get("offense_attacks", 0)
            defense_change = player.get("defense_trophies_change", 0)
            defense_defends = player.get("defense_defends", 0)

            offense_display = f"{EMOJIS['offense']} {offense_change:+}/{offense_attacks}"
            defense_display = f"{EMOJIS['defense']} {defense_change:+}/{defense_defends}"

            line = f"{rank}. {name} ({tag})\n   🏆 {trophies} | {offense_display} | {defense_display}"
            description_lines.append(line)

        embed = create_embed(
            title="Linked Players Leaderboard",
            description="\n".join(description_lines),
            color=discord.Color(int(color.replace('#', ''), 16))
        )
        embed.set_footer(text=f"Page {page}/{total_pages}")

        await interaction.followup.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Leaderboard(bot))
            

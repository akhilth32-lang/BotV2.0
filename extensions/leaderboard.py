# extensions/leaderboard.py

import discord
from discord import app_commands
from discord.ext import commands
from database import player_crud
from config import legend_season
from config.emoji import EMOJIS
from utils.embed_helpers import create_embed
from config.fonts import to_bold_gg_sans, to_regular_gg_sans
from utils.time_helpers import get_current_legend_season_and_day  # You need to implement this helper
import datetime

LEADERBOARD_PAGE_SIZE = 20

class Leaderboard(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="leaderboard",
        description="Show leaderboard of all linked Clash of Clans player accounts"
    )
    @app_commands.describe(
        leaderboard_name="Name of the leaderboard to show",
        color="Embed color in hex (e.g. #000000 for black, default black)",
        day="Legend league day snapshot to view (default current day)"
    )
    async def leaderboard(self, interaction: discord.Interaction, leaderboard_name: str, color: str = "#000000", day: int = 0):
        await interaction.response.defer()

        # Fetch linked players sorted by trophies descending
        all_players = await player_crud.get_all_linked_players()
        sorted_players = sorted(all_players, key=lambda p: p.get('trophies', 0), reverse=True)

        # Pagination removed: show only first LEADERBOARD_PAGE_SIZE players or all
        page_players = sorted_players[:LEADERBOARD_PAGE_SIZE]

        description_lines = []
        for idx, player in enumerate(page_players, start=1):
            name = to_bold_gg_sans(player.get("player_name", "Unknown"))
            tag = player.get("player_tag", "N/A")
            trophies = player.get("trophies", 0)
            offense_change = player.get("offense_trophies", 0)
            offense_attacks = player.get("offense_attacks", 0)
            defense_change = player.get("defense_trophies", 0)
            defense_defends = player.get("defense_defenses", 0)

            offense_display = f"{EMOJIS['offense']} {offense_change:+}/{offense_attacks}"
            defense_display = f"{EMOJIS['defense']} {defense_change:-}/{defense_defends}"

            line = f"{idx}. {name} ({tag})\n   🏆 {trophies} | {offense_display} | {defense_display}"
            description_lines.append(line)

        embed = create_embed(
            title=f"{leaderboard_name} Leaderboard",
            description="\n".join(description_lines),
            color=discord.Color(int(color.replace('#', ''), 16))
        )

        # Get current season and day for footer
        season_number, legend_day = get_current_legend_season_and_day(legend_season.LEGEND_SEASONS_2025)
        now_local = datetime.datetime.now().strftime("%I:%M %p")

        embed.set_footer(text=f"Day {legend_day}/{season_number} ({datetime.datetime.now():%Y-%m}) | Today at {now_local}")

        await interaction.followup.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Leaderboard(bot))
    

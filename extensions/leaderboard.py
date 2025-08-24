# extensions/leaderboard.py

import discord
from discord import app_commands
from discord.ext import commands
from database import player_crud
from database import leaderboard_snapshot_crud
from config import legend_season
from config.emoji import EMOJIS
from utils.embed_helpers import create_embed
from config.fonts import to_bold_gg_sans
from utils.time_helpers import get_current_legend_season_and_day
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

        # Determine the current Legend League season and day for footer and snapshot logic
        season_number, current_day = get_current_legend_season_and_day(legend_season.LEGEND_SEASONS_2025)

        if day == 0 or day == current_day:
            # Fetch live player data for current day or if day=0 (default)
            all_players = await player_crud.get_all_linked_players()
        else:
            # Fetch snapshot for the specified season and day
            snapshot = await leaderboard_snapshot_crud.get_snapshot(season_number, day)
            if snapshot is None or "leaderboard_data" not in snapshot:
                await interaction.followup.send(f"No snapshot data found for season {season_number} day {day}.")
                return
            all_players = snapshot["leaderboard_data"]

        # Sort players by trophies descending
        sorted_players = sorted(all_players, key=lambda p: p.get('trophies', 0), reverse=True)

        # Limit leaderboard size as per constant
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

        # Format footer: day/current_day, current season month-year, and local time
        total_days = 0
        for season in legend_season.LEGEND_SEASONS_2025:
            if season["season_number"] == season_number:
                total_days = season["duration_days"]
                break

        now = datetime.datetime.now()
        month_year = now.strftime("%Y-%m")
        local_time = now.strftime("%I:%M %p")

        embed.set_footer(text=f"Day {day}/{total_days} ({month_year}) | Today at {local_time}")

        await interaction.followup.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Leaderboard(bot))
    

# extensions/leaderboard.py

import discord
from discord import app_commands
from discord.ext import commands
from database import player_crud, leaderboard_snapshot_crud
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

        # Determine current season and day
        season_number, current_day = get_current_legend_season_and_day(legend_season.LEGEND_SEASONS_2025)

        # Fetch players data - live if day=0 else from snapshot for selected day
        if day == 0 or day == current_day:
            all_players = await player_crud.get_all_linked_players()
        else:
            snapshot = await leaderboard_snapshot_crud.get_snapshot(season_number, day)
            if not snapshot or "leaderboard_data" not in snapshot:
                await interaction.followup.send(f"No snapshot data found for season {season_number} day {day}.")
                return
            all_players = snapshot["leaderboard_data"]

        sorted_players = sorted(all_players, key=lambda p: p.get('trophies', 0), reverse=True)
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

        # Get total days in current season
        total_days = next((season["duration_days"] for season in legend_season.LEGEND_SEASONS_2025 if season["season_number"] == season_number), None)
        now_utc = datetime.datetime.now(datetime.timezone.utc)
        now_local = now_utc.astimezone()
        today_midnight = now_local.replace(hour=0, minute=0, second=0, microsecond=0)
        season_month = next((season["start"].strftime("%Y-%m") for season in legend_season.LEGEND_SEASONS_2025 if season["season_number"] == season_number), "")

        if day == 0:
            day_display = current_day
        else:
            day_display = day

        if day_display and total_days and season_month:
            if now_local > today_midnight:
                footer_str = f"Day {day_display}/{total_days} ({season_month}) | Today at {now_local.strftime('%I:%M %p')}"
            else:
                footer_str = f"Day {day_display}/{total_days} ({season_month}) | {now_local.strftime('%m/%d/%Y %I:%M %p')}"
        else:
            footer_str = f"Date unknown | {now_local.strftime('%m/%d/%Y %I:%M %p')}"

        embed.set_footer(text=footer_str)

        await interaction.followup.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Leaderboard(bot))
            

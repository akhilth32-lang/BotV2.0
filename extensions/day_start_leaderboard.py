# extensions/day_start_leaderboard.py

import discord
from discord import app_commands
from discord.ext import commands
from database.leaderboard_snapshot_crud import get_snapshot
from config import emoji, fonts
from utils.embed_helpers import create_embed
from config.fonts import to_bold_gg_sans, to_regular_gg_sans
from config.legend_season import LEGEND_SEASONS_2025
from utils.time_helpers import get_current_legend_season_and_day

PAGE_SIZE = 30

class DayStartLeaderboard(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="day_start_leaderboard", description="Show snapshot of leaderboard at end of Legend League day (10:30 AM IST snapshot)")
    @app_commands.describe(page="Leaderboard page number (default 1)")
    async def day_start_leaderboard(self, interaction: discord.Interaction, page: int = 1):
        await interaction.response.defer()

        # Determine current season and day using helper from config.legend_season and utils.time_helpers
        season, day = get_current_legend_season_and_day(LEGEND_SEASONS_2025)

        snapshot = await get_snapshot(season, day)
        if not snapshot:
            await interaction.followup.send("No snapshot found for the current Legend League day.", ephemeral=True)
            return

        leaderboard_data = snapshot.get("leaderboard_data", [])

        total_pages = (len(leaderboard_data) + PAGE_SIZE - 1) // PAGE_SIZE
        page = max(1, min(page, total_pages))

        start_idx = (page - 1) * PAGE_SIZE
        end_idx = start_idx + PAGE_SIZE
        page_data = leaderboard_data[start_idx:end_idx]

        description_lines = []
        rank_offset = start_idx
        for idx, player in enumerate(page_data, start=rank_offset + 1):
            name = to_bold_gg_sans(player.get("player_name", "Unknown"))
            tag = player.get("player_tag", "")
            trophies = player.get("trophies", 0)
            offense_change = player.get("offense_trophies_change", 0)
            offense_attacks = player.get("offense_attacks", 0)
            defense_change = player.get("defense_trophies_change", 0)
            defense_defends = player.get("defense_defends", 0)

            offense_display = f"{emoji.EMOJIS['offense']} {offense_change:+}/{offense_attacks}"
            defense_display = f"{emoji.EMOJIS['defense']} {defense_change:+}/{defense_defends}"

            line = f"{idx}. {name} 🏆{trophies} {offense_display} {defense_display} ({tag})"
            description_lines.append(line)

        embed = create_embed(
            title=f"Legend League Day {day} Snapshot Leaderboard (Season {season})",
            description="\n".join(description_lines),
            color=discord.Color.dark_theme()
        )
        embed.set_footer(text=f"Page {page} / {total_pages}")

        await interaction.followup.send(embed=embed)

async def setup(bot):
    await bot.add_cog(DayStartLeaderboard(bot))
        

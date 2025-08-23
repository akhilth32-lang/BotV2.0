# tasks/daily_snapshot_reset.py

import asyncio
import datetime
from discord.ext import commands, tasks
from database.leaderboard_snapshot_crud import save_daily_snapshot
from database import player_crud
from config.legend_season import LEGEND_SEASONS_2025
from utils.time_helpers import get_current_legend_season_and_day
import pytz

class DailySnapshotReset(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.snapshot_task.start()

    def cog_unload(self):
        self.snapshot_task.cancel()

    @tasks.loop(minutes=1.0)
    async def snapshot_task(self):
        now_utc = datetime.datetime.utcnow().replace(tzinfo=pytz.UTC)
        
        # Target reset time 10:30 AM IST (5:00 AM UTC)
        reset_time_utc = now_utc.replace(hour=5, minute=0, second=0, microsecond=0)

        # Because task runs every 1 minute, check if we are within reset timeframe (e.g., exactly 5:00 AM UTC)
        if abs((now_utc - reset_time_utc).total_seconds()) < 70:  # within 70 seconds window

            # Get current season and day for snapshot metadata
            season, day = get_current_legend_season_and_day(LEGEND_SEASONS_2025)

            # Fetch all linked players data for snapshot
            linked_players = await player_crud.get_all_linked_players(limit=2000)

            # Save snapshot in DB before reset at 10:25 AM IST (4:55 AM UTC)
            # We save snapshot at this time so this runs a little early before reset
            await save_daily_snapshot(season, day, linked_players)

            # Now reset offense and defense stats (to 0/0) for all linked players for new day
            for player in linked_players:
                await player_crud.update_player_stats(
                    player["player_tag"],
                    player["trophies"],
                    offense_change=0,
                    offense_count=0,
                    defense_change=0,
                    defense_count=0,
                )
            print(f"Daily leaderboard snapshot saved and offense/defense reset for season {season} day {day}.")

    @snapshot_task.before_loop
    async def before_snapshot(self):
        await self.bot.wait_until_ready()

async def setup(bot):
    await bot.add_cog(DailySnapshotReset(bot))

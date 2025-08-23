import asyncio
from datetime import datetime, time, timezone, timedelta
import logging

import discord
from discord.ext import tasks
from pymongo import MongoClient

from apis.coc_api import CocClient
from config.settings import MONGO_URI

logger = logging.getLogger(__name__)

# MongoDB setup
mongo_client = MongoClient(MONGO_URI)
db = mongo_client["clash_bot"]
backup_collection = db["daily_backups"]

class BackgroundUpdater:
    def __init__(self, bot: discord.Bot):
        self.bot = bot
        self.coc_client = CocClient()
        self.backup_time = time(4, 55)  # 10:25 AM IST = 4:55 UTC
        self.backup_task.start()

    async def fetch_all_players(self):
        # This should fetch all player tags from your database or cache
        # Placeholder: fetch player tags from DB or from a stored list
        player_tags = []
        # Implement actual fetch here
        return player_tags

    @tasks.loop(minutes=1)
    async def backup_task(self):
        now = datetime.now(timezone.utc)
        if now.time().hour == self.backup_time.hour and now.time().minute == self.backup_time.minute:
            await self.perform_backup()

    async def perform_backup(self):
        logger.info("Starting daily backup task...")
        try:
            player_tags = await self.fetch_all_players()
            backups = []
            for tag in player_tags:
                player_data = await self.coc_client.get_player(tag)
                backups.append(player_data.raw)

            backup_record = {
                "timestamp": datetime.now(timezone.utc),
                "players": backups,
            }
            backup_collection.insert_one(backup_record)
            logger.info("Daily backup saved successfully.")
        except Exception as e:
            logger.error(f"Error during backup: {e}")

    def cog_unload(self):
        self.backup_task.cancel()
      

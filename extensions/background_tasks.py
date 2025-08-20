# extensions/background_tasks.py
import asyncio
from discord.ext import commands, tasks
from database.player_crud import get_all_players, add_or_update_player, backup_all_players
from apis.coc_api import fetch_player_data
from datetime import datetime, timedelta

class BackgroundTasks(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.last_reset_date = None
        self.last_backup_date = None
        self.update_players_data.start()
        self.reset_offense_defense.start()
        self.backup_leaderboard.start()

    def cog_unload(self):
        self.update_players_data.cancel()
        self.reset_offense_defense.cancel()
        self.backup_leaderboard.cancel()

    async def async_fetch_player_data(self, tag):
        import aiohttp
        async with aiohttp.ClientSession() as session:
            return await fetch_player_data(session, tag)

    @tasks.loop(minutes=5)
    async def update_players_data(self):
        players = get_all_players()
        print(f"\n⏳ Background update: {len(players)} players")
        for player in players:
            try:
                discord_id = player["discord_id"]
                tag = player["player_tag"]

                trophies = player.get("trophies", 0)
                rank = player.get("rank", 0)
                off_t = player.get("offense_trophies", 0)
                off_a = player.get("offense_attacks", 0)
                def_t = player.get("defense_trophies", 0)
                def_d = player.get("defense_defenses", 0)

                data = await self.async_fetch_player_data(tag)
                if data:
                    delta = data.get("trophies", 0) - trophies
                    if delta > 0:
                        off_t += delta
                        off_a += 1
                    elif delta < 0:
                        def_t += abs(delta)
                        def_d += 1

                    data.update({
                        "prev_trophies": trophies,
                        "prev_rank": rank,
                        "offense_trophies": off_t,
                        "offense_attacks": off_a,
                        "defense_trophies": def_t,
                        "defense_defenses": def_d,
                        "last_reset": datetime.now().strftime("%Y-%m-%d")
                    })
                    add_or_update_player(discord_id, tag, data)
                else:
                    print(f"❌ Failed: {tag}")
            except Exception as e:
                print(f"❌ Error updating {player['player_tag']}: {e}")
        print("✅ Update finished!")

    @tasks.loop(minutes=1)
    async def reset_offense_defense(self):
        now = datetime.utcnow() + timedelta(hours=5, minutes=30)  # IST
        if now.hour == 10 and now.minute == 30 and self.last_reset_date != now.date():
            from database.database import players_col
            players_col.update_many({}, {
                "$set": {
                    "offense_trophies": 0,
                    "offense_attacks": 0,
                    "defense_trophies": 0,
                    "defense_defenses": 0
                }
            })
            self.last_reset_date = now.date()
            print("🔁 Daily offense/defense reset done (10:30 AM IST)")

    @tasks.loop(minutes=1)
    async def backup_leaderboard(self):
        now = datetime.utcnow() + timedelta(hours=5, minutes=30)  # IST
        if now.hour == 10 and now.minute == 25 and self.last_backup_date != now.date():
            backup_all_players()
            self.last_backup_date = now.date()

async def setup(bot):
    await bot.add_cog(BackgroundTasks(bot))
              

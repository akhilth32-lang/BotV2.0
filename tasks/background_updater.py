# tasks/background_updater.py

import asyncio
from discord.ext import commands, tasks
from database import player_crud
from apis.coc_api import ClashOfClansAPI
import datetime

class BackgroundUpdater(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.api = ClashOfClansAPI()
        self.update_players.start()

    def cog_unload(self):
        self.update_players.cancel()

    @tasks.loop(minutes=5.0)
    async def update_players(self):
        # Runs every 5 minutes
        print(f"[{datetime.datetime.utcnow()}] Starting background update of linked players...")

        try:
            players = await player_crud.get_all_linked_players()
            print(f"Updating {len(players)} linked players.")

            for player in players:
                player_tag = player["player_tag"]
                try:
                    # Fetch player data from official API
                    player_data = await self.api.get_player(player_tag)

                    # Calculate offense, defense, trophies info here
                    trophies = player_data.get("trophies", 0)
                    attack_wins = player_data.get("attackWins", 0)
                    defense_wins = player_data.get("defenseWins", 0)

                    # You may implement logic here to calculate offense/defense changes comparing with DB values

                    # For now, we just update trophies with 0 changes placeholders
                    await player_crud.update_player_stats(
                        player_tag,
                        trophies,
                        offense_change=0,
                        offense_count=0,
                        defense_change=0,
                        defense_count=0,
                    )
                    print(f"Updated {player_tag} - Trophies: {trophies}")
                except Exception as e:
                    print(f"Failed to update player {player_tag}: {str(e)}")

        except Exception as e:
            print(f"Background update error: {str(e)}")

    @update_players.before_loop
    async def before_update(self):
        await self.bot.wait_until_ready()

async def setup(bot):
    await bot.add_cog(BackgroundUpdater(bot))
    

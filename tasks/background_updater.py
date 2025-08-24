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
        print(f"[{datetime.datetime.utcnow()}] Starting background update of linked players...")

        try:
            players = await player_crud.get_all_linked_players()
            print(f"Updating {len(players)} linked players.")

            for player in players:
                player_tag = player["player_tag"]
                try:
                    player_data = await self.api.get_player(player_tag)

                    # Extract current stats from API
                    trophies = player_data.get("trophies", 0)
                    townhall = player_data.get("townHallLevel", 0)
                    attacks = player_data.get("attackWins", 0)
                    defenses = player_data.get("defenseWins", 0)
                    rank = player_data.get("rank", 0)  # If available

                    # Previous stats from DB for delta calculation
                    prev_trophies = player.get("trophies", 0)
                    prev_offense_attacks = player.get("offense_attacks", 0)
                    prev_defense_defenses = player.get("defense_defenses", 0)
                    prev_offense_trophies = player.get("offense_trophies", 0)
                    prev_defense_trophies = player.get("defense_trophies", 0)
                    prev_rank = player.get("rank", 0)

                    # Calculate deltas
                    offense_change = trophies - prev_trophies
                    offense_count = attacks - prev_offense_attacks
                    defense_change = 0  # Adjust if you track defense trophies differently
                    defense_count = defenses - prev_defense_defenses

                    await player_crud.update_player_stats(
                        player_tag=player_tag,
                        trophies=trophies,
                        offense_change=offense_change,
                        offense_count=offense_count,
                        defense_change=defense_change,
                        defense_count=defense_count,
                        townhall=townhall,
                        attacks=attacks,
                        defenses=defenses,
                        prev_trophies=prev_trophies,
                        prev_rank=prev_rank,
                        rank=rank
                    )

                    print(f"Updated {player_tag} - Trophies: {trophies}, Attacks: {attacks}, Defenses: {defenses}")

                except Exception as e:
                    print(f"Failed to update player {player_tag}: {str(e)}")

        except Exception as e:
            print(f"Background update error: {str(e)}")

    @update_players.before_loop
    async def before_update(self):
        await self.bot.wait_until_ready()


async def setup(bot):
    await bot.add_cog(BackgroundUpdater(bot))
    

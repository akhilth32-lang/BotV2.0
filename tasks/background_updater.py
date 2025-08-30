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
        self.last_reset_date = None
        self.update_players.start()
        self.reset_offense_defense.start()

    def cog_unload(self):
        self.update_players.cancel()
        self.reset_offense_defense.cancel()

    @tasks.loop(minutes=5.0)
    async def update_players(self):
        print(f"[{datetime.datetime.utcnow()}] Starting background update of linked players...")

        try:
            players = await player_crud.get_all_linked_players()
            print(f"Found {len(players)} linked players.")

            for player in players:
                player_tag = player["player_tag"]
                print(f"Updating player {player_tag}...")

                try:
                    # Fetch latest player data from API
                    player_data = await self.api.get_player(player_tag)
                    print(f"API data for {player_tag}: {player_data}")

                    # Extract API career total wins and trophies
                    total_attacks = player_data.get("attackWins", 0)  # Total career attack wins
                    total_defenses = player_data.get("defenseWins", 0)  # Total career defense wins
                    current_trophies = player_data.get("trophies", 0)
                    townhall = player_data.get("townHallLevel", 0)
                    rank = player_data.get("rank", 0)  # Optional per API

                    # Read previous stored values
                    prev_trophies = player.get("trophies", 0)
                    prev_offense_attacks = player.get("offense_attacks", 0)
                    prev_offense_attacks_field = player.get("prev_offense_attacks", 0)

                    # Daily Legend League stats (reset daily)
                    offense_trophies = player.get("offense_trophies", 0)
                    offense_attacks = player.get("offense_attacks", 0)
                    defense_trophies = player.get("defense_trophies", 0)
                    defense_defenses = player.get("defense_defenses", 0)

                    # Calculate offense attacks difference based on total career attack wins from API
                    attack_win_diff = total_attacks - prev_offense_attacks_field
                    if attack_win_diff < 0:
                        # Possible reset or anomaly in API counter, fallback to total_attacks
                        attack_win_diff = total_attacks

                    offense_attacks += attack_win_diff

                    # Calculate daily offense/defense trophies
                    if current_trophies > prev_trophies:
                        offense_trophies += current_trophies - prev_trophies
                    elif current_trophies < prev_trophies:
                        defense_trophies += prev_trophies - current_trophies
                        defense_defenses += 1  # Defense count unchanged for this update, defensive difference not implemented

                    # Update database with new aggregated stats including previous offense attacks count
                    updated = await player_crud.update_player_stats(
                        player_tag=player_tag,
                        trophies=current_trophies,
                        offense_change=offense_trophies,
                        offense_count=offense_attacks,
                        defense_change=defense_trophies,
                        defense_count=defense_defenses,
                        townhall=townhall,
                        attacks=total_attacks,
                        defenses=total_defenses,
                        prev_trophies=prev_trophies,
                        prev_rank=player.get("rank", 0),
                        rank=rank,
                        prev_offense_attacks=total_attacks  # <-- Store current career attacks as previous for next cycle
                    )

                    print(
                        f"DB update for {player_tag}: {'Success' if updated else 'No change'} "
                        f"| Total Attacks: {total_attacks}, Total Defenses: {total_defenses} "
                        f"| Daily Offense: +{offense_trophies}/{offense_attacks}, "
                        f"Daily Defense: +{defense_trophies}/{defense_defenses}"
                    )

                except Exception as e:
                    print(f"Failed to update player {player_tag}: {str(e)}")

        except Exception as e:
            print(f"Background update error: {str(e)}")

    @tasks.loop(minutes=1.0)
    async def reset_offense_defense(self):
        now = datetime.datetime.utcnow() + datetime.timedelta(hours=5, minutes=30)  # IST timezone
        if now.hour == 10 and now.minute == 30:
            if self.last_reset_date != now.date():
                print(f"Performing daily reset of offense/defense stats at {now.isoformat()}")
                from database.database import players_collection
                await players_collection.update_many({}, {
                    "$set": {
                        "offense_trophies": 0,
                        "offense_attacks": 0,
                        "defense_trophies": 0,
                        "defense_defenses": 0
                    }
                })
                self.last_reset_date = now.date()
                print("Daily offense/defense reset complete.")

    @update_players.before_loop
    async def before_update(self):
        await self.bot.wait_until_ready()

    @reset_offense_defense.before_loop
    async def before_reset(self):
        await self.bot.wait_until_ready()


async def setup(bot):
    await bot.add_cog(BackgroundUpdater(bot))
    

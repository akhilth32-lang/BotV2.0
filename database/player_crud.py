# database/player_crud.py

from .database import players_collection
from bson.objectid import ObjectId
from typing import List, Optional
import datetime


async def add_linked_player(discord_id: int, player_tag: str, api_token: str, player_name: str):
    """Add a new linked player for a discord user."""
    player_doc = {
        "discord_id": discord_id,
        "player_tag": player_tag.upper(),
        "api_token": api_token,
        "player_name": player_name,
        "offense_trophies_change": 0,
        "offense_attacks": 0,
        "defense_trophies_change": 0,
        "defense_defends": 0,
        "trophies": 0,
        "last_updated": datetime.datetime.utcnow(),
        "linked_date": datetime.datetime.utcnow(),
        "unlinked": False  # flag to keep track if unlinked
    }
    await players_collection.insert_one(player_doc)
    return player_doc


async def get_linked_players_by_discord(discord_id: int) -> List[dict]:
    """Get all linked players for a Discord user."""
    cursor = players_collection.find({"discord_id": discord_id, "unlinked": False})
    return await cursor.to_list(length=None)


async def unlink_player(player_tag: str, discord_id: Optional[int] = None):
    """Mark player as unlinked for given discord and player_tag."""
    player_tag = player_tag.upper()
    query = {"player_tag": player_tag}
    if discord_id:
        query["discord_id"] = discord_id
    update = {"$set": {"unlinked": True}}
    result = await players_collection.update_one(query, update)
    return result.modified_count > 0


async def update_player_stats(player_tag: str, trophies: int, offense_change: int, offense_count: int,
                              defense_change: int, defense_count: int):
    """Update player stats."""
    player_tag = player_tag.upper()
    update = {
        "$set": {
            "trophies": trophies,
            "offense_trophies_change": offense_change,
            "offense_attacks": offense_count,
            "defense_trophies_change": defense_change,
            "defense_defends": defense_count,
            "last_updated": datetime.datetime.utcnow(),
        }
    }
    result = await players_collection.update_one({"player_tag": player_tag}, update)
    return result.modified_count > 0


async def get_all_linked_players(limit: int = 2000):
    """Get all linked players for updating stats."""
    cursor = players_collection.find({"unlinked": False}).limit(limit)
    return await cursor.to_list(length=limit)
    

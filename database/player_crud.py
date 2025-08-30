# database/player_crud.py

from .database import players_collection
from bson.objectid import ObjectId
from typing import List, Optional
import datetime


async def add_linked_player(discord_id: int, player_tag: str, player_name: str, townhall: int = 0, trophies: int = 0):
    """Add a new linked player for a Discord user.
    Prevents duplicate linking of the same player_tag.
    """
    player_tag = player_tag.upper()

    # Check if already linked (globally, not unlinked)
    existing = await players_collection.find_one({"player_tag": player_tag, "unlinked": False})
    if existing:
        return None  # Already linked

    player_doc = {
        "discord_id": discord_id,
        "player_tag": player_tag,
        "player_name": player_name,
        "townhall": townhall,
        "trophies": trophies,
        "offense_trophies": 0,
        "offense_attacks": 0,
        "prev_offense_attacks": 0,  # <-- Added field
        "defense_trophies": 0,
        "defense_defenses": 0,
        "attackWins": 0,
        "defenseWins": 0,
        "prev_trophies": trophies,
        "prev_rank": 0,
        "rank": 0,
        "last_reset": datetime.datetime.utcnow().date().isoformat(),
        "last_updated": datetime.datetime.utcnow(),
        "linked_date": datetime.datetime.utcnow(),
        "unlinked": False
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


async def get_prev_offense_attacks(player_tag: str):
    player = await players_collection.find_one({"player_tag": player_tag})
    return player.get("offense_attacks", 0) if player else 0


async def update_player_stats(player_tag: str, trophies: int, offense_change: int, offense_count: int,
                              defense_change: int, defense_count: int, townhall: Optional[int] = None,
                              attacks: Optional[int] = None, defenses: Optional[int] = None,
                              prev_trophies: Optional[int] = None, prev_rank: Optional[int] = None,
                              rank: Optional[int] = None, prev_offense_attacks: Optional[int] = None):
    """Update player stats and additional info."""
    player_tag = player_tag.upper()
    update_fields = {
        "trophies": trophies,
        "offense_trophies": offense_change,
        "offense_attacks": offense_count,
        "defense_trophies": defense_change,
        "defense_defenses": defense_count,
        "last_updated": datetime.datetime.utcnow(),
    }

    if townhall is not None:
        update_fields["townhall"] = townhall
    if attacks is not None:
        update_fields["attackWins"] = attacks
    if defenses is not None:
        update_fields["defenseWins"] = defenses
    if prev_trophies is not None:
        update_fields["prev_trophies"] = prev_trophies
    if prev_rank is not None:
        update_fields["prev_rank"] = prev_rank
    if rank is not None:
        update_fields["rank"] = rank
    if prev_offense_attacks is not None:
        update_fields["prev_offense_attacks"] = prev_offense_attacks  # <-- Track previous offense attacks

    update = {"$set": update_fields}
    result = await players_collection.update_one({"player_tag": player_tag}, update)
    return result.modified_count > 0


async def get_all_linked_players(limit: int = 2000):
    """Get all linked players for updating stats."""
    cursor = players_collection.find({"unlinked": False}).limit(limit)
    return await cursor.to_list(length=limit)


# ✅ Fetch player from API and save full info (fixed small details)
async def fetch_and_save_player(api, discord_id: int, player_tag: str):
    """Fetch player from CoC API and save full info in DB."""
    data = await api.get_player(player_tag)
    if not data:
        return None  # Fail-safe if API call fails

    player_doc = {
        "discord_id": discord_id,
        "player_tag": player_tag.upper(),
        "player_name": data.get("name", "Unknown"),
        "townhall": data.get("townHallLevel", 0),
        "trophies": data.get("trophies", 0),
        "attackWins": 0,
        "defenseWins": 0,
        "offense_attacks": 0,
        "prev_offense_attacks": 0,  # <-- Added field
        "offense_trophies": 0,
        "defense_defenses": 0,
        "defense_trophies": 0,
        "prev_trophies": data.get("trophies", 0),
        "prev_rank": 0,
        "rank": 0,
        "last_reset": datetime.datetime.utcnow().date().isoformat(),
        "last_updated": datetime.datetime.utcnow(),
        "linked_date": datetime.datetime.utcnow(),
        "unlinked": False
    }

    await players_collection.update_one(
        {"player_tag": player_tag.upper()},
        {"$set": player_doc},
        upsert=True
    )

    return player_doc
        

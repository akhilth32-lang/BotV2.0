# database/player_crud.py
from database.database import players_col
from typing import Optional, List, Dict


def add_or_update_player(discord_id: int, player_tag: str, data: dict):
    """
    Add a new player or update existing player info in the DB.
    """
    players_col.update_one(
        {"discord_id": discord_id},
        {
            "$set": {
                "player_tag": player_tag,
                "name": data.get("name"),
                "trophies": data.get("trophies"),
                "townhall": data.get("townhall", 0),
                "last_updated": data.get("last_updated"),
                # Add other fields as needed
                "offense_trophies": data.get("offense_trophies", 0),
                "offense_attacks": data.get("offense_attacks", 0),
                "defense_trophies": data.get("defense_trophies", 0),
                "defense_defenses": data.get("defense_defenses", 0),
            }
        },
        upsert=True
    )


def get_player_by_tag(player_tag: str) -> Optional[dict]:
    """
    Find a player in the DB by player_tag.
    Returns None if not found.
    """
    player = players_col.find_one({"player_tag": player_tag})
    return player


def get_linked_players_for_user(discord_id: int) -> List[dict]:
    """
    Get all players linked to a given Discord user.
    """
    players = list(players_col.find({"discord_id": discord_id}))
    return players


def remove_player(discord_id: int, player_tag: str = None):
    """
    Remove player(s) linked to a Discord user.
    If player_tag is specified, remove only that player.
    Otherwise, remove all players linked to the Discord user.
    """
    if player_tag:
        players_col.delete_one({"discord_id": discord_id, "player_tag": player_tag})
    else:
        players_col.delete_many({"discord_id": discord_id})


def get_all_players() -> List[dict]:
    """
    Get all player records from DB.
    """
    return list(players_col.find())


def backup_all_players():
    """
    Make a backup copy of all players data in DB with timestamp.
    You should implement actual backup logic here, like exporting to a file or another collection.
    """
    import datetime
    backup_collection = players_col.database["players_backup"]
    all_data = list(players_col.find())
    timestamp = datetime.datetime.utcnow()
    if all_data:
        backup_collection.insert_one({
            "timestamp": timestamp,
            "players": all_data
        })
    print(f"Backup done at {timestamp}")
    

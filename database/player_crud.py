# database/player_crud.py
from database.database import players_col
from typing import Optional, List, Dict

def add_or_update_player(discord_id: int, player_tag: str, data: dict):
    players_col.update_one(
        {"discord_id": discord_id, "player_tag": player_tag.upper()},
        {
            "$set": {
                "name": data.get("name"),
                "trophies": data.get("trophies"),
                "townhall": data.get("townhall", 0),
                "last_updated": data.get("last_updated"),
                "offense_trophies": data.get("offense_trophies", 0),
                "offense_attacks": data.get("offense_attacks", 0),
                "defense_trophies": data.get("defense_trophies", 0),
                "defense_defenses": data.get("defense_defenses", 0),
            }
        },
        upsert=True
    )

def get_player_by_tag(player_tag: str) -> Optional[dict]:
    player = players_col.find_one({"player_tag": player_tag.upper()})
    return player

def get_linked_players_for_user(discord_id: int) -> List[dict]:
    return list(players_col.find({"discord_id": discord_id}))

def remove_player(discord_id: int, player_tag: str = None):
    if player_tag:
        players_col.delete_one({"discord_id": discord_id, "player_tag": player_tag.upper()})
    else:
        players_col.delete_many({"discord_id": discord_id})

def get_all_players() -> List[dict]:
    return list(players_col.find())

def backup_all_players():
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
    

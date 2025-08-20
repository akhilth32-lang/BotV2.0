# database/player_crud.py
from .database import players_col, backup_col
from datetime import datetime


def add_or_update_player(discord_id, tag, data):
    update = {
        "discord_id": discord_id,
        "player_tag": tag,
        "name": data["name"],
        "trophies": data["trophies"],
        "rank": data.get("rank", 0),
        "prev_trophies": data.get("prev_trophies", data["trophies"]),
        "prev_rank": data.get("prev_rank", data.get("rank", 0)),
        "attacks": data.get("attacks", 0),
        "defenses": data.get("defenses", 0),
        "offense_trophies": data.get("offense_trophies", 0),
        "offense_attacks": data.get("offense_attacks", 0),
        "defense_trophies": data.get("defense_trophies", 0),
        "defense_defenses": data.get("defense_defenses", 0),
        "last_reset": data.get("last_reset", datetime.now().strftime("%Y-%m-%d"))
    }
    players_col.update_one({"player_tag": tag}, {"$set": update}, upsert=True)
    print(f"✅ Player updated/added: {data['name']} ({tag})")


def get_all_players():
    return list(players_col.find().sort("trophies", -1))


def get_linked_players_for_user(discord_id):
    return list(players_col.find({"discord_id": discord_id}))


def remove_player(discord_id, tag=None):
    if tag:
        result = players_col.delete_one({"discord_id": discord_id, "player_tag": tag.replace("#", "")})
        print(f"🔁 Removed one: matched={result.deleted_count}")
    else:
        result = players_col.delete_many({"discord_id": discord_id})
        print(f"🔁 Removed all: matched={result.deleted_count}")


def backup_all_players():
    players = list(players_col.find({}))
    if players:
        backup_col.delete_many({})
        backup_col.insert_many(players)
        print(f"💾 Backup complete with {len(players)} players")
      

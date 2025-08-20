# utils/embed_helpers.py
import discord
from utils.time_helpers import format_ist

def create_leaderboard_embed(title, color, players, page, page_size):
    embed = discord.Embed(title=title, color=color)
    start = page * page_size
    end = start + page_size
    embed.set_footer(text=f"Last refreshed: {format_ist()}")

    for i, p in enumerate(players[start:end], start=start + 1):
        embed.add_field(
            name=f"{i}. {p['name']} (#{p['player_tag']})",
            value=f"🏆 {p['trophies']} | ⚔️ +{p.get('offense_trophies', 0)}/{p.get('offense_attacks', 0)} | 🛡️ -{p.get('defense_trophies', 0)}/{p.get('defense_defenses', 0)}\n\u200b",
            inline=False
        )
    return embed

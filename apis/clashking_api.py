# apis/clashking_api.py
import aiohttp
import os
from dotenv import load_dotenv

load_dotenv()

CLASH_KING_API_BASE = "https://api.clashk.ing"
CLASH_KING_API_KEY = os.getenv("CLASH_KING_API_KEY")


async def fetch_live_legends(session):
    url = f"{CLASH_KING_API_BASE}/ranking/live/legends"
    headers = {"Authorization": f"Bearer {CLASH_KING_API_KEY}"} if CLASH_KING_API_KEY else {}
    async with session.get(url, headers=headers) as resp:
        if resp.status == 200:
            return await resp.json()
        else:
            print(f"Clash King API error: {resp.status} fetching live legends")
            return None


async def fetch_legend_player(session, player_tag):
    url = f"{CLASH_KING_API_BASE}/ranking/legends/{player_tag.replace('#', '')}"
    headers = {"Authorization": f"Bearer {CLASH_KING_API_KEY}"} if CLASH_KING_API_KEY else {}
    async with session.get(url, headers=headers) as resp:
        if resp.status == 200:
            return await resp.json()
        else:
            print(f"Clash King API error: {resp.status} fetching legend player {player_tag}")
            return None
          

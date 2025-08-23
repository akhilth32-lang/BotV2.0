# apis/coc_api.py

import aiohttp
import asyncio
from config.settings import COC_API_TOKEN

BASE_URL = "https://api.clashofclans.com/v1"

HEADERS = {
    "Authorization": f"Bearer {COC_API_TOKEN}",
    "Accept": "application/json"
}

class ClashOfClansAPI:

    def __init__(self):
        self.session = aiohttp.ClientSession(headers=HEADERS)

    async def close(self):
        await self.session.close()

    async def get_player(self, player_tag: str):
        """Get player info by tag."""
        player_tag = player_tag.strip('#').upper()
        url = f"{BASE_URL}/players/%23{player_tag}"
        async with self.session.get(url) as resp:
            if resp.status == 200:
                return await resp.json()
            else:
                data = await resp.text()
                raise Exception(f"Failed to get player {player_tag}: {resp.status} - {data}")

    async def verify_player_api_token(self, player_tag: str, player_token: str):
        """
        Verify player token for player tag by making POST request
        to the official verifytoken endpoint with the developer API token.
        """
        player_tag = player_tag.strip('#').upper()
        url = f"{BASE_URL}/players/%23{player_tag}/verifytoken"
        json_data = {"token": player_token}

        async with aiohttp.ClientSession(headers=HEADERS) as session:
            async with session.post(url, json=json_data) as resp:
                if resp.status != 200:
                    return False
                data = await resp.json()
                return data.get("status") == "ok"

    async def get_location_leaderboard(self, location_id: str, limit=200, after=None):
        """Get leaderboard for a given location id."""
        url = f"{BASE_URL}/locations/{location_id}/rankings/players?limit={limit}"
        if after:
            url += f"&after={after}"
        async with self.session.get(url) as resp:
            if resp.status == 200:
                return await resp.json()
            else:
                data = await resp.text()
                raise Exception(f"Failed to get leaderboard for {location_id}: {resp.status} - {data}")
                

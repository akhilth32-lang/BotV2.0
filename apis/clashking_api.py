# apis/clashking_api.py
import aiohttp

async def fetch_live_legends(session: aiohttp.ClientSession):
    """
    Fetch the live Legend League leaderboard from Clash King API.
    Returns a list of player dicts or None on failure.
    """
    url = "https://api.clashk.ing/ranking/live/legends?top_ranking=1&lower_ranking=200"
    try:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                # Data is a list of dicts representing players
                return data
            else:
                print(f"Clash King API returned status {response.status}")
                return None
    except Exception as e:
        print(f"Error fetching Clash King live legends: {e}")
        return None
        

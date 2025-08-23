# apis/leaderboard_fetcher.py

from apis.coc_api import ClashOfClansAPI

class LeaderboardFetcher:
    def __init__(self):
        self.api = ClashOfClansAPI()
        self._cache = None
        self._cache_expiry = 0

    async def fetch_full_leaderboard(self, location_id: str):
        import time
        now = time.time()
        # Cache for 5 minutes
        if self._cache and self._cache_expiry > now:
            return self._cache

        # Bulk fetch with limit 200 per API spec
        result = await self.api.get_location_leaderboard(location_id, limit=200)
        players = result.get("items", [])

        self._cache = players
        self._cache_expiry = now + 300
        return players

    async def close(self):
        await self.api.close()
        

# config/settings.py

import os
from dotenv import load_dotenv

load_dotenv()

# Discord Bot Token
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

# Clash of Clans API Token for official API access
COC_API_TOKEN = os.getenv("COC_API_TOKEN")

# MongoDB connection string
MONGODB_URI = os.getenv("MONGODB_URI")

# Render app port (for keep_alive.py)
RENDER_PORT = int(os.getenv("PORT", 8080))

# Legend League season reset time (10:30 AM IST converted to UTC)
# IST (UTC+5:30), 10:30 AM IST = 5:00 AM UTC
LEGEND_LEAGUE_RESET_HOUR_UTC = 5
LEGEND_LEAGUE_RESET_MINUTE_UTC = 0

# Leaderboard page size
LEADERBOARD_PAGE_SIZE = 20

# Current Leaderboard page size (from API spec)
CURRENT_LEADERBOARD_PAGE_SIZE = 30

# Other global bot settings (customize as needed)
MAX_LINKS_PER_USER = None  # None = unlimited

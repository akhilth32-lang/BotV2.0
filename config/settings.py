import os
from dotenv import load_dotenv

load_dotenv()

# MongoDB connection string from environment variable
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")

# Discord Bot Token
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN", "")

# Clash of Clans API token
COC_API_TOKEN = os.getenv("COC_API_TOKEN", "")

# Other settings
BOT_PREFIX = "!"

# bot.py
import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("DISCORD_BOT_TOKEN")

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

# Load all command extensions
extensions = [
    "extensions.leaderboard",
    "extensions.link",
    "extensions.day_leaderboard",
    "extensions.current_leaderboard",
    "extensions.background_tasks"
]

async def main():
    async with bot:
        for ext in extensions:
            await bot.load_extension(ext)
        await bot.start(TOKEN)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())

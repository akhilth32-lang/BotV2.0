import os
import discord
from discord.ext import commands
from keep_alive import keep_alive

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="/", intents=intents)

initial_extensions = [
    "extensions.link",
    "extensions.unlink",
    "extensions.link_profile",
    "extensions.leaderboard",
    "extensions.current_leaderboard",
    "extensions.day_start_leaderboard",
    "tasks.background_updater",
    "tasks.daily_snapshot_reset",
]

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    await bot.tree.sync()
    print("Slash commands synced")

async def load_extensions():
    for ext in initial_extensions:
        await bot.load_extension(ext)

if __name__ == "__main__":
    keep_alive()
    import asyncio
    asyncio.run(load_extensions())
    bot.run(os.environ["BOT_TOKEN"])
    

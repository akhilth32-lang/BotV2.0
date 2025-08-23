import os
import discord
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv
import keep_alive

load_dotenv()
TOKEN = os.getenv("DISCORD_BOT_TOKEN")

intents = discord.Intents.default()
intents.message_content = True  # Required for message content access if needed

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} commands")
    except Exception as e:
        print(f"Command sync failed: {e}")
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")

initial_extensions = [
    "extensions.link",
    "extensions.unlink_profile",
    "extensions.leaderboard",
    "extensions.current_leaderboard",
    "extensions.day_start_leaderboard",
    "tasks.background_updater",
]

if __name__ == "__main__":
    for ext in initial_extensions:
        try:
            bot.load_extension(ext)
            print(f"Loaded extension: {ext}")
        except Exception as e:
            print(f"Failed to load extension {ext}: {e}")

    keep_alive.keep_alive()
    bot.run(TOKEN)
    

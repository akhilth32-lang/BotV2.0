import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import asyncio

from keep_alive import keep_alive

# Load token from .env
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# Intents
intents = discord.Intents.default()
intents.message_content = True  # Enable if you process message content commands

# Create bot
bot = commands.Bot(command_prefix='!', intents=intents)

# Extensions to load
initial_extensions = [
    'extensions.link',
    'extensions.unlink',
    'extensions.link_profile',
    'extensions.leaderboard',
    'extensions.current_leaderboard',
    'extensions.day_start_leaderboard',
    'tasks.background_updater',   # background updater cog
    'extensions.fetch_ids',       # ✅ new fetch_ids extension
]

async def load_extensions():
    for ext in initial_extensions:
        try:
            await bot.load_extension(ext)
            print(f'✅ Loaded extension {ext}')
        except Exception as e:
            print(f'❌ Failed to load extension {ext}: {e}')

@bot.event
async def on_ready():
    print(f'🤖 Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')
    # Sync slash commands
    try:
        await bot.tree.sync()
        print('✅ Slash commands synced globally.')
    except Exception as e:
        print(f'❌ Failed to sync commands: {e}')

async def main():
    # Start keepalive server
    keep_alive()
    # Load extensions
    await load_extensions()
    # Start bot
    await bot.start(TOKEN)

if __name__ == '__main__':
    asyncio.run(main())

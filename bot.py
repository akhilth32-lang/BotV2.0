import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import asyncio

from keep_alive import keep_alive

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.message_content = True  # Enable if you process message content commands

bot = commands.Bot(command_prefix='!', intents=intents)

initial_extensions = [
    'extensions.link',
    'extensions.unlink',
    'extensions.link_profile',
    'extensions.leaderboard',
    'extensions.current_leaderboard',
    'extensions.day_start_leaderboard',
    'tasks.background_updater',   # Added this line to load background updater cog
]

async def load_extensions():
    for ext in initial_extensions:
        try:
            await bot.load_extension(ext)
            print(f'Loaded extension {ext}')
        except Exception as e:
            print(f'Failed to load extension {ext}: {e}')

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')
    await bot.tree.sync()  # Sync slash commands globally
    print('Slash commands synced.')

async def main():
    keep_alive()  # Start keepalive server
    await load_extensions()
    await bot.start(TOKEN)

if __name__ == '__main__':
    asyncio.run(main())
    

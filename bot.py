# bot.py

import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

from keep_alive import keep_alive
from extensions import link, unlink, link_profile, leaderboard, current_leaderboard, day_start_leaderboard

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
bot = commands.Bot(command_prefix='!', intents=intents)

# Load extensions (cogs)
initial_extensions = [
    'extensions.link',
    'extensions.unlink',
    'extensions.link_profile',
    'extensions.leaderboard',
    'extensions.current_leaderboard',
    'extensions.day_start_leaderboard',
]

if __name__ == '__main__':
    for ext in initial_extensions:
        bot.load_extension(ext)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')

keep_alive()  # Start the keep alive web server for Render + uptimerobot
bot.run(TOKEN)

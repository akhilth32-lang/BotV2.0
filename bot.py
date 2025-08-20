# bot.py
import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
from keep_alive import keep_alive

load_dotenv()

TOKEN = os.getenv("DISCORD_BOT_TOKEN")

intents = discord.Intents.default()
# Enable intents as your bot requires. Enable message_content if your bot needs to read messages
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Example slash command - add your extensions similarly
@bot.tree.command(name="ping", description="Check bot latency")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message(f"Pong! Latency is {round(bot.latency * 1000)}ms")

@bot.event
async def on_ready():
    # Sync slash commands globally
    await bot.tree.sync()
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    print("------")

# Load all your other cogs/extensions here, example:
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
    keep_alive()  # start the Flask keep-alive server
    import asyncio
    asyncio.run(main())
    

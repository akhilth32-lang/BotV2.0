# extensions/link_profile.py

import discord
from discord import app_commands
from discord.ext import commands
from database import player_crud
from config.emoji import EMOJIS
from utils.embed_helpers import create_embed
import random
from datetime import datetime

# Replace these URLs with your actual hosted profile photo URLs
PROFILE_PHOTOS = [
    "https://cdn.discordapp.com/attachments/1383022223043858472/1409490443481251850/barbarian_baby_default_emote.png?ex=68ad91c4&is=68ac4044&hm=1afbf174a675200d818cb98ceb7c0ce1ab78a4ea2069c6ec2a245fad20636752&",
    "https://cdn.discordapp.com/attachments/1383022223043858472/1409490443905007718/Wizard_skin_StreetMagic_icon.png?ex=68ad91c4&is=68ac4044&hm=04fd616d473d8dbbd09a952fcec4cd99abb3a7ec4bffc8893bb9aa6d8413b3e5&",
    "https://cdn.discordapp.com/attachments/1383022223043858472/1409490444198477864/miner_classic_icon.png?ex=68ad91c4&is=68ac4044&hm=5933c01cf58571689c0bc22cd22cc609d61b34ac35dd859143ca9b766e286d8c&",
]

class LinkProfile(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="link_profile",
        description="Show all linked Clash of Clans accounts for a Discord user"
    )
    @app_commands.describe(discord_user="Optional Discord user to view linked accounts (defaults to you)")
    async def link_profile(self, interaction: discord.Interaction, discord_user: discord.Member = None):
        await interaction.response.defer()

        user = discord_user or interaction.user
        linked_players = await player_crud.get_linked_players_by_discord(user.id)

        if not linked_players:
            embed = create_embed(
                title=f"{EMOJIS['warning']} No Linked Accounts",
                description=f"No Clash of Clans accounts linked to {user.mention}.",
                color=discord.Color.dark_theme()
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
            return

        # Select a random profile photo URL for this user
        random_photo_url = random.choice(PROFILE_PHOTOS)

        description_lines = []
        for player in linked_players:
            name = player.get("player_name", "Unknown")
            tag = player.get("player_tag", "N/A")

            th_level = player.get("townhall", "?")
            th_emoji = EMOJIS.get("townhall", "🏠")  # Always use custom townhall emoji

            # Format: :th: • **NAME** (#TAG)
            line = f"{th_emoji} • **{name}** ({tag})"
            description_lines.append(line)

        # Add one empty line between accounts
        formatted_description = "\n\n".join(description_lines)

        # Format timestamp footer (Today at HH:MM AM/PM)
        now = datetime.now().strftime("Today at %I:%M %p")

        embed = create_embed(
            title=f"Player Profile - {user.display_name}",
            description=formatted_description,
            color=discord.Color(0x2c2f33)
        )

        embed.set_thumbnail(url=random_photo_url)
        embed.set_footer(text=now)

        await interaction.followup.send(embed=embed, ephemeral=False)


async def setup(bot):
    await bot.add_cog(LinkProfile(bot))

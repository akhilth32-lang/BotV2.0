# extensions/link.py
from discord.ext import commands
from discord import app_commands, Interaction
from database.player_crud import add_or_update_player, remove_player, get_linked_players_for_user
from apis.coc_api import fetch_player_data
import asyncio

class LinkCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def async_fetch_player_data(self, tag):
        # Helper to run async API fetch_player_data with aiohttp session
        import aiohttp
        async with aiohttp.ClientSession() as session:
            return await fetch_player_data(session, tag)

    @app_commands.command(name="link", description="Link your Clash of Clans player tag to your Discord account")
    @app_commands.describe(player_tag="Your Clash of Clans player tag (e.g., #8YJ98LV2C)")
    async def link(self, interaction: Interaction, player_tag: str):
        await interaction.response.defer()
        tag = player_tag.replace("#", "").upper()
        data = await self.async_fetch_player_data(tag)
        if data:
            add_or_update_player(interaction.user.id, tag, data)
            await interaction.followup.send(f"✅ Linked {data['name']} ({player_tag}) to your account.")
        else:
            await interaction.followup.send("❌ Failed to fetch player data. Please check the tag and try again.")

    @app_commands.command(name="unlink", description="Unlink a Clash of Clans tag or all linked with you")
    @app_commands.describe(player_tag="Optional: tag to unlink (remove all if empty)")
    async def unlink(self, interaction: Interaction, player_tag: str = None):
        await interaction.response.defer()
        if player_tag:
            tag = player_tag.replace("#", "").upper()
        else:
            tag = None
        remove_player(interaction.user.id, tag)
        await interaction.followup.send("✅ Account unlinked.", ephemeral=True)

    @app_commands.command(name="linkprofile", description="Show all linked Clash of Clans accounts for your Discord user")
    async def link_profile(self, interaction: Interaction):
        await interaction.response.defer()
        linked_players = get_linked_players_for_user(interaction.user.id)
        if not linked_players:
            await interaction.followup.send("You have no linked Clash of Clans accounts.", ephemeral=True)
            return

        description = ""
        for p in linked_players:
            description += f"{p['name']} (#{p['player_tag']}) — Trophies: {p['trophies']}\n"
        await interaction.followup.send(content=f"**Your linked Clash of Clans accounts:**\n{description}", ephemeral=True)


async def setup(bot):
    await bot.add_cog(LinkCog(bot))
      

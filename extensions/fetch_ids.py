# extensions/fetch_ids.py

import discord
from discord import app_commands
from discord.ext import commands

class FetchIDs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="fetch_ids", description="Fetch all slash command IDs in this server")
    async def fetch_ids(self, interaction: discord.Interaction):
        guild = interaction.guild
        if guild is None:
            await interaction.response.send_message("❌ This can only be used in a server.", ephemeral=True)
            return

        commands_list = await self.bot.tree.fetch_commands(guild=guild)
        if not commands_list:
            await interaction.response.send_message("⚠️ No slash commands found in this server.", ephemeral=True)
            return

        lines = []
        for cmd in commands_list:
            lines.append(f"</{cmd.name}:{cmd.id}> (`{cmd.id}`)")

        message = "📋 **Slash Commands in this server:**\n" + "\n".join(lines)
        await interaction.response.send_message(message, ephemeral=True)

async def setup(bot):
    await bot.add_cog(FetchIDs(bot))

# extensions/fetch_ids.py

import discord
from discord import app_commands
from discord.ext import commands

class FetchIDs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="fetch_ids", description="Fetch all slash command IDs (global & this server)")
    async def fetch_ids(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        lines = []

        # Fetch global commands
        global_cmds = await self.bot.tree.fetch_commands()
        if global_cmds:
            lines.append("🌍 **Global Slash Commands:**")
            for cmd in global_cmds:
                lines.append(f"</{cmd.name}:{cmd.id}> (`{cmd.id}`)")
        else:
            lines.append("⚠️ No global commands found.")

        # Fetch guild commands (server-specific)
        if interaction.guild:
            guild_cmds = await self.bot.tree.fetch_commands(guild=interaction.guild)
            if guild_cmds:
                lines.append(f"\n🏠 **Server Slash Commands ({interaction.guild.name}):**")
                for cmd in guild_cmds:
                    lines.append(f"</{cmd.name}:{cmd.id}> (`{cmd.id}`)")
            else:
                lines.append("\n⚠️ No server commands found.")
        else:
            lines.append("\n❌ Must be used inside a server to fetch guild commands.")

        message = "\n".join(lines)
        await interaction.followup.send(message, ephemeral=True)


async def setup(bot):
    await bot.add_cog(FetchIDs(bot))

# extensions/link.py
from discord.ext import commands
from discord import app_commands, Interaction, Embed
from database.player_crud import add_or_update_player, remove_player, get_linked_players_for_user, get_player_by_tag
from apis.coc_api import fetch_player_data
from emoji_map import TOWNHALL_EMOJIS

class LinkCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="link", description="Link your Clash of Clans account")
    @app_commands.describe(player_tag="Your Clash of Clans player tag (e.g., #ABC123)")
    async def link(self, interaction: Interaction, player_tag: str):
        await interaction.response.defer(ephemeral=True)
        tag = player_tag.upper().replace("#", "")
        existing = get_player_by_tag(tag)
        if existing:
            await interaction.followup.send(f"**{existing['name']} (#{existing['player_tag']})** is already linked.", ephemeral=True)
            return

        import aiohttp
        async with aiohttp.ClientSession() as session:
            data = await fetch_player_data(session, '#' + tag)
            if data:
                add_or_update_player(interaction.user.id, tag, data)
                await interaction.followup.send(f"✅ Linked {data['name']} (#{tag}) to your account.", ephemeral=True)
            else:
                await interaction.followup.send("❌ Failed to fetch player data. Please check the tag and try again.", ephemeral=True)

    @app_commands.command(name="unlink", description="Unlink a Clash account")
    @app_commands.describe(player_tag="Optional, specify tag to unlink, or unlinks all if empty")
    async def unlink(self, interaction: Interaction, player_tag: str = None):
        await interaction.response.defer(ephemeral=True)
        if player_tag:
            remove_player(interaction.user.id, player_tag.upper().replace("#", ""))
            await interaction.followup.send(f"Unlinked {player_tag}.", ephemeral=True)
        else:
            remove_player(interaction.user.id)
            await interaction.followup.send("All linked accounts removed.", ephemeral=True)

    @app_commands.command(name="linkprofile", description="Show linked Clash accounts")
    @app_commands.describe(user="Optional Discord user to check")
    async def linkprofile(self, interaction: Interaction, user: commands.MemberConverter = None):
        target = user or interaction.user
        linked = get_linked_players_for_user(target.id)
        if not linked:
            await interaction.response.send_message(f"No linked accounts found for {target.display_name}.", ephemeral=True)
            return

        embed = Embed(title=f"{target.display_name}'s Linked Clash Accounts", color=0x118EF5)
        for p in linked:
            emoji = TOWNHALL_EMOJIS.get(p.get("townhall", 0), "")
            embed.add_field(
                name=f"{p['name']} {emoji}",
                value=f"Trophies: {p['trophies']} | Tag: #{p['player_tag']}",
                inline=False
            )
        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(LinkCog(bot))
            

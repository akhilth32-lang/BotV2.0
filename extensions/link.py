# extensions/link.py

import discord
from discord import app_commands
from discord.ext import commands
from apis.coc_api import ClashOfClansAPI
from database import player_crud
from config.emoji import EMOJIS
from utils.embed_helpers import create_embed
from utils.error_handling import send_error_message

class Link(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.coc_api = ClashOfClansAPI()

    @app_commands.command(name="link", description="Link a Clash of Clans account with your Discord by player tag and API token")
    @app_commands.describe(player_tag="Clash of Clans player tag starting with #", api_token="Player's API token from game settings", discord_user="Optionally link for another Discord user")
    async def link(self, interaction: discord.Interaction, player_tag: str, api_token: str, discord_user: discord.Member = None):
        await interaction.response.defer(ephemeral=True)

        target_user = discord_user or interaction.user
        player_tag = player_tag.upper().replace("O", "0")  # Common OCR error, optional fix

        # Verify player token via official API
        verified = await self.coc_api.verify_player_api_token(player_tag, api_token)
        if not verified:
            embed = create_embed(
                title=f"{EMOJIS['failed']} Link Failed",
                description="The player API token is not valid for the given player tag.",
                color=discord.Color.red(),
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
            return

        # Fetch player info for name etc.
        try:
            player_info = await self.coc_api.get_player(player_tag)
        except Exception as e:
            await send_error_message(interaction, str(e))
            return

        player_name = player_info.get("name", "Unknown")

        # Save linked player info to DB
        await player_crud.add_linked_player(
            discord_id=target_user.id,
            player_tag=player_tag,
            api_token=api_token,
            player_name=player_name
        )

        embed = create_embed(
            title=f"{EMOJIS['tick']} Link Successful",
            description=f"Player **{player_name}** ({player_tag}) has been linked to Discord user {target_user.mention}.",
            color=discord.Color.green(),
        )
        await interaction.followup.send(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(Link(bot))
        

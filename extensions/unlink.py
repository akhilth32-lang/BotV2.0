# extensions/unlink.py

import discord
from discord import app_commands
from discord.ext import commands
from database import player_crud
from config.emoji import EMOJIS
from utils.embed_helpers import create_embed
from utils.error_handling import send_error_message

class Unlink(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="unlink", description="Unlink a Clash of Clans account from your Discord account")
    @app_commands.describe(player_tag="Clash of Clans player tag to unlink, e.g. #92VJVRYV0")
    async def unlink(self, interaction: discord.Interaction, player_tag: str):
        await interaction.response.defer(ephemeral=True)

        player_tag = player_tag.upper().replace("O", "0")  # Normalize
        discord_id = interaction.user.id

        # Try to unlink player for this discord user
        try:
            success = await player_crud.unlink_player(player_tag, discord_id)
            if success:
                embed = create_embed(
                    title=f"{EMOJIS['tick']} Unlink Successful",
                    description=f"Player tag {player_tag} has been unlinked from your Discord account.",
                    color=discord.Color.green(),
                )
            else:
                embed = create_embed(
                    title=f"{EMOJIS['failed']} Unlink Failed",
                    description="The player tag was not linked to your Discord account or does not exist.",
                    color=discord.Color.red(),
                )
            await interaction.followup.send(embed=embed, ephemeral=True)

        except Exception as e:
            await send_error_message(interaction, str(e))

async def setup(bot):
    await bot.add_cog(Unlink(bot))
        

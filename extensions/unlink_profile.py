from discord.ext import commands
from database.player_crud import delete_player_by_tag, get_player_by_tag

class UnlinkProfile(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="unlink")
    async def unlink_command(self, ctx, player_tag: str):
        """Unlink a Clash of Clans player tag from Discord user."""
        player = get_player_by_tag(player_tag)
        if player is None or player.get("discord_id") != str(ctx.author.id):
            await ctx.send("Player tag not linked to your Discord account.")
            return
        deleted_count = delete_player_by_tag(player_tag)
        if deleted_count:
            await ctx.send(f"Successfully unlinked player {player_tag} from your Discord account.")
        else:
            await ctx.send("Failed to unlink player. Please try again later.")

async def setup(bot):
    await bot.add_cog(UnlinkProfile(bot))
  

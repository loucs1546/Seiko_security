# cogs/security/content_filter.py
import discord
from discord.ext import commands
import core_config as config
from config.filters import est_contenu_suspect
from utils.logging import send_log_to  # ← send_log_to

class ContentFilterCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or not message.guild or message.guild.id != config.GUILD_ID:
            return

        if est_contenu_suspect(message.content):
            try:
                await message.delete()
            except:
                pass

            embed = discord.Embed(
                title="⚠️ Contenu supprimé (illicite)",
                description=f"**Auteur** : {message.author.mention}\n**Salon** : {message.channel.mention}",
                color=0xff0000,
                timestamp=discord.utils.utcnow()
            )
            embed.add_field(name="Contenu", value=message.content[:1020], inline=False)
            await send_log_to(self.bot, "securite", embed)  # ← send_log_to, pas send_log

            await message.channel.send(
                f"{message.author.mention}, votre message a été supprimé pour contenu illicite.",
                delete_after=5
            )

async def setup(bot):
    await bot.add_cog(ContentFilterCog(bot))
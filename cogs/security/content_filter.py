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
            embed = discord.Embed(
                title="⚠️ Contenu signalé",
                description=f"Par {message.author.mention} dans {message.channel.mention}",
                color=0xff6600,
                timestamp=discord.utils.utcnow()
            )
            embed.add_field(name="Raison", value="Contenu suspect détecté", inline=False)
            embed.add_field(name="Extrait", value=message.content[:100], inline=False)
            await send_log_to(self.bot, "content", embed)  # ← send_log_to

async def setup(bot):
    await bot.add_cog(ContentFilterCog(bot))
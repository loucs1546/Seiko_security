# cogs/security/link_filter.py
import discord
from discord.ext import commands
import core_config as config
import re
from utils.logging import send_log_to
from config.filters import est_url_suspecte

URL_REGEX = re.compile(r"https?://[^\s]+")

class LinkFilterCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or not message.guild or message.guild.id != config.GUILD_ID:
            return

        urls = URL_REGEX.findall(message.content)
        if not urls:
            return

        for url in urls:
            # ✅ 1. Loguer D'ABORD dans "🔍・contenu"
            embed = discord.Embed(
                title="🔗 Lien détecté",
                description=f"Par {message.author.mention} dans {message.channel.mention}",
                color=0x0099ff,
                timestamp=discord.utils.utcnow()
            )
            embed.add_field(name="URL", value=url[:1020])

            if est_url_suspecte(url):
                embed.color = 0xff6600
                embed.title = "⚠️ Lien suspect"

            await send_log_to(self.bot, "content", embed)

        # ✅ 2. Supprimer le message APRÈS le log
        try:
            await message.delete()
        except Exception:
            pass

        # ✅ 3. Avertir l'utilisateur
        try:
            await message.channel.send(
                f"{message.author.mention}, votre message contient un lien et a été supprimé.",
                delete_after=5
            )
        except Exception:
            pass

async def setup(bot):
    await bot.add_cog(LinkFilterCog(bot))
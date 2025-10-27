# cogs/security/link_filter.py
import discord
from discord.ext import commands
import core_config as config
import re
from utils.logging import send_log
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

        try:
            await message.delete()
            # ✅ Loguer ICI
            embed = discord.Embed(
                title="🗑️ Message supprimé (lien suspect)",
                description=f"**Auteur** : {message.author.mention}\n"
                            f"**Salon** : {message.channel.mention}\n"
                            f"**Supprimé par** : {self.bot.user.mention} (bot)",
                color=0xff6600,
                timestamp=discord.utils.utcnow()
            )
            if message.content:
                embed.add_field(name="Contenu", value=message.content[:1020], inline=False)
            await send_log(self.bot, "messages", embed)

            await message.channel.send(
                f"{message.author.mention}, votre message contient un lien suspect et a été supprimé.",
                delete_after=5
            )
        except Exception:
            pass

        for url in urls:
            embed = discord.Embed(
                title="⚠️ Lien suspect détecté",
                description=f"Par {message.author.mention} dans {message.channel.mention}",
                color=0xff6600,
                timestamp=discord.utils.utcnow()
            )
            embed.add_field(name="URL", value=url[:1020])
            await send_log(self.bot, "content", embed)

async def setup(bot):
    await bot.add_cog(LinkFilterCog(bot))
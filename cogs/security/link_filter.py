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
        for url in urls:
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

            await send_log(self.bot, "content", embed)

async def setup(bot):
    await bot.add_cog(LinkFilterCog(bot))
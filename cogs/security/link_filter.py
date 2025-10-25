import discord
from discord.ext import commands
import config
import re
from utils.logging import send_log

NSFW_KEYWORDS = {
    "porn", "sex", "xxx", "nude", "nsfw", "adult", "cam", "onlyfans",
    "pedo", "child", "lolita", "jailbait", "cp", "hentai", "furry", "rule34",
    "gay", "lesbian", "trans", " Shemale", "cock", "pussy", "ass", "boobs"
}

URL_REGEX = re.compile(r"https?://[^\s]+")

def is_suspicious_url(url: str) -> bool:
    url_lower = url.lower()
    for word in NSFW_KEYWORDS:
        if word in url_lower:
            return True
    if "discord.gg/" in url_lower or "discord.com/invite/" in url_lower:
        return True
    return False

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
                title="🔗 URL détectée",
                description=f"Par {message.author.mention} dans {message.channel.mention}",
                color=0xff6600,
                timestamp=discord.utils.utcnow()
            )
            embed.add_field(name="URL", value=url[:1020])

            if is_suspicious_url(url):
                embed.color = 0xff0000
                embed.title = "⚠️ URL SUSPECTE – POSSIBLEMENT NSFW/PEGI18"
                # Optionnel : supprimer le message
                # await message.delete()
                # await message.channel.send(f"{message.author.mention}, lien interdit.", delete_after=5)

            await send_log(self.bot, "links", embed)

async def setup(bot):
    await bot.add_cog(LinkFilterCog(bot))

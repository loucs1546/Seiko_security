# cogs/security/content_filter.py
import discord
from discord.ext import commands
from config.filters import est_url_suspecte, est_contenu_suspect
from utils.logging import send_log
import core_config as config

class ContentFilterCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or not message.guild or message.guild.id != config.GUILD_ID:
            return

        if est_contenu_suspect(message.content):
            # Optionnel : supprimer le message
            # await message.delete()
            # await message.channel.send(f"{message.author.mention}, message non autorisé.", delete_after=5)

            embed = discord.Embed(
                title="⚠️ Contenu signalé",
                description=f"Par {message.author.mention} dans {message.channel.mention}",
                color=0xff6600,
                timestamp=discord.utils.utcnow()
            )
            embed.add_field(name="Raison", value="Contenu suspect détecté", inline=False)
            embed.add_field(name="Extrait", value=message.content[:100], inline=False)
            await send_log(self.bot, "content", embed)
async def setup(bot):
    print("✅ Filtre de contenu activé")
    await bot.add_cog(ContentFilterCog(bot))

async def setup(bot):
    await bot.add_cog(ContentFilterCog(bot))
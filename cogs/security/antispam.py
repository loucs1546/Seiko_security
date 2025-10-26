# cogs/security/antispam.py
import discord
from discord.ext import commands
import core_config as config
from utils.logging import send_log
from collections import defaultdict
import time
from config.filters import WHITELISTED_PHRASES

class AntiSpamCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.user_messages = defaultdict(list)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or not message.guild or message.guild.id != config.GUILD_ID:
            return

        # Nettoyer le contenu pour comparaison
        clean_content = message.content.strip().lower()

        # Ignorer les messages dans la liste blanche
        if clean_content in WHITELISTED_PHRASES:
            return

        uid = message.author.id
        now = time.time()

        # Nettoyer l'historique (messages des 5 dernières secondes uniquement)
        self.user_messages[uid] = [t for t in self.user_messages[uid] if now - t[0] < 5]
        self.user_messages[uid].append((now, clean_content))

        # Vérifier si spam : ≥5 messages en 5s
        if len(self.user_messages[uid]) >= 5:
            contents = [msg[1] for msg in self.user_messages[uid]]
            is_repetitive = len(set(contents)) == 1  # Tous les messages identiques
            is_short = all(len(c) <= 5 for c in contents)  # Tous très courts

            if is_repetitive or is_short:
                try:
                    await message.delete()
                    await message.channel.send(
                        f"{message.author.mention}, veuillez ne pas spammer.",
                        delete_after=5
                    )
                    embed = discord.Embed(
                        title="🚫 SPAM BLOQUÉ",
                        description=f"Par {message.author.mention}",
                        color=0xff0000,
                        timestamp=discord.utils.utcnow()
                    )
                    embed.add_field(name="Contenu", value=message.content[:1020])
                    await send_log(self.bot, "threats", embed)
                except Exception:
                    pass  # Échec silencieux si pas la permission

async def setup(bot):
    await bot.add_cog(AntiSpamCog(bot))
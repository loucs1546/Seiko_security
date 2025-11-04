import discord
from discord.ext import commands
import core_config as config
from utils.logging import send_log_to
import time

class AntiRaidCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.join_log = []  # [(timestamp, member, invite_code)]
        self.invite_tracker = {}  # invite_code → [member_ids]

    @commands.Cog.listener()
    async def on_member_join(self, member):
        if member.guild.id != config.GUILD_ID:
            return

        now = time.time()
        # Nettoyer les entrées > 60s
        self.join_log = [entry for entry in self.join_log if now - entry[0] < 60]
        
        # Récupérer l'invitation (si possible)
        invite_code = None
        try:
            invites = await member.guild.invites()
            for invite in invites:
                if invite.uses > 0 and invite.inviter:
                    if invite.code not in self.invite_tracker:
                        self.invite_tracker[invite.code] = []
                    self.invite_tracker[invite.code].append(member.id)
                    invite_code = invite.code
                    break
        except:
            pass

        self.join_log.append((now, member, invite_code))

        # Si ≥5 membres en 60s ET même invitation → alerte raid
        if len(self.join_log) >= 5:
            # Vérifier si au moins 3 ont rejoint via la même invitation
            if invite_code:
                same_invite_count = len(self.invite_tracker.get(invite_code, []))
                if same_invite_count >= 3:
                    log_channel = self.bot.get_channel(config.LOG_CHANNEL_ID)
                    if log_channel:
                        await log_channel.send("🚨 **ALERTE RAID SUSPECT** détecté !")
                    
                    embed = discord.Embed(
                        title="🚨 RAID SUSPECT DÉTECTÉ",
                        description=f"{len(self.join_log)} membres en 60 secondes.\n"
                                    f"Invitation commune : `{invite_code}`\n"
                                    f"Créateur : {invite.inviter.mention if 'invite' in locals() else 'Inconnu'}",
                        color=0xff0000,
                        timestamp=discord.utils.utcnow()
                    )
                    await send_log(self.bot, "alerts", embed)

async def setup(bot):
    await bot.add_cog(AntiRaidCog(bot))
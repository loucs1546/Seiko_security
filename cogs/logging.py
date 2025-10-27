# cogs/logging.py
import discord
from discord.ext import commands
import core_config as config
from utils.logging import send_log
import asyncio

class LoggingCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # === MESSAGES ===
    @commands.Cog.listener()
    async def on_message(self, message):
        if not message.guild or message.guild.id != config.GUILD_ID or message.author.id == self.bot.user.id:
            return
        embed = discord.Embed(
            title="📥 Message reçu",
            description=f"**Auteur** : {message.author.mention}\n**Salon** : {message.channel.mention}\n**Contenu** :\n>>> {message.content or '[Aucun texte]'}",
            color=0x2ecc71,
            timestamp=message.created_at
        )
        if message.attachments:
            urls = "\n".join(a.url for a in message.attachments[:3])
            embed.add_field(name="📎 Pièces jointes", value=urls, inline=False)
        await send_log(self.bot, "messages", embed)

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if not message.guild or message.guild.id != config.GUILD_ID or message.author.bot:
            return

        deleter = "Inconnu"
        # Attendre un peu pour que l'audit log soit disponible
        await asyncio.sleep(0.5)
        try:
            async for entry in message.guild.audit_logs(action=discord.AuditLogAction.message_delete, limit=1):
                if entry.target.id == message.author.id and (discord.utils.utcnow() - entry.created_at).total_seconds() < 10:
                    deleter = entry.user
                    break
        except:
            pass

        embed = discord.Embed(
            title="🗑️ Message supprimé",
            description=f"**Auteur** : {message.author.mention}\n"
                        f"**Salon** : {message.channel.mention}\n"
                        f"**Supprimé par** : {deleter}",
            color=0xff8800,
            timestamp=discord.utils.utcnow()
        )
        if message.content:
            embed.add_field(name="Contenu", value=message.content[:1020], inline=False)
        await send_log(self.bot, "messages", embed)

    # === PROFIL (pseudo) ===
    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        if before.guild.id != config.GUILD_ID:
            return

        # Pseudo
        if before.nick != after.nick:
            moderator = "Inconnu"
            await asyncio.sleep(0.5)
            try:
                async for entry in after.guild.audit_logs(action=discord.AuditLogAction.member_update, limit=1):
                    if (
                        entry.target.id == after.id and
                        hasattr(entry.changes, 'nick') and
                        entry.changes.nick[0] == before.nick and
                        entry.changes.nick[1] == after.nick and
                        (discord.utils.utcnow() - entry.created_at).total_seconds() < 10
                    ):
                        moderator = entry.user
                        break
            except:
                pass

            old_nick = before.nick or before.global_name or before.name
            new_nick = after.nick or after.global_name or after.name
            embed = discord.Embed(
                title="📛 Pseudo modifié",
                description=f"{after.mention}\n**Modérateur** : {moderator}",
                color=0x00ccff,
                timestamp=discord.utils.utcnow()
            )
            embed.add_field(name="Avant", value=old_nick, inline=True)
            embed.add_field(name="Après", value=new_nick, inline=True)
            await send_log(self.bot, "profile", embed)

        # Rôles (déjà bon, mais on le garde)
        before_roles = set(before.roles)
        after_roles = set(after.roles)
        if before_roles != after_roles:
            moderator = "Inconnu"
            await asyncio.sleep(0.5)
            try:
                async for entry in after.guild.audit_logs(action=discord.AuditLogAction.member_role_update, limit=1):
                    if entry.target.id == after.id and (discord.utils.utcnow() - entry.created_at).total_seconds() < 10:
                        moderator = entry.user
                        break
            except:
                pass

            added = after_roles - before_roles
            removed = before_roles - after_roles
            desc = ""
            if added: desc += "➕ Ajoutés : " + ", ".join(r.mention for r in added) + "\n"
            if removed: desc += "➖ Retirés : " + ", ".join(r.mention for r in removed)
            if desc:
                embed = discord.Embed(
                    title="👑 Rôles modifiés",
                    description=f"{after.mention}\n**Modérateur** : {moderator}\n{desc}",
                    color=0xffaa00,
                    timestamp=discord.utils.utcnow()
                )
                await send_log(self.bot, "roles", embed)

    # === VOCAL ===
    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if member.guild.id != config.GUILD_ID:
            return

        # Déplacement forcé (par un modérateur)
        if before.channel and after.channel and before.channel != after.channel:
            moderator = "Inconnu"
            await asyncio.sleep(0.5)  # ← Critique : attendre que l'audit log soit prêt
            try:
                async for entry in member.guild.audit_logs(action=discord.AuditLogAction.member_move, limit=1):
                    if entry.target.id == member.id and (discord.utils.utcnow() - entry.created_at).total_seconds() < 10:
                        moderator = entry.user
                        break
            except:
                pass

            embed = discord.Embed(
                title="🎤 Déplacement vocal",
                description=f"{member.mention} : {before.channel.mention} → {after.channel.mention}\n**Modérateur** : {moderator}",
                color=0xffff00,
                timestamp=discord.utils.utcnow()
            )
            await send_log(self.bot, "vocal", embed)

        # Mute / Deafen par un modérateur
        elif before.mute != after.mute or before.deaf != after.deaf:
            moderator = "Inconnu"
            await asyncio.sleep(0.5)
            try:
                async for entry in member.guild.audit_logs(action=discord.AuditLogAction.member_update, limit=1):
                    if entry.target.id == member.id and (discord.utils.utcnow() - entry.created_at).total_seconds() < 10:
                        if (before.mute != after.mute and getattr(entry.changes, 'mute', None)) or \
                           (before.deaf != after.deaf and getattr(entry.changes, 'deaf', None)):
                            moderator = entry.user
                            break
            except:
                pass

            actions = []
            if before.mute != after.mute:
                actions.append("mute vocal" if after.mute else "unmute vocal")
            if before.deaf != after.deaf:
                actions.append("sourdine" if after.deaf else "fin de sourdine")

            embed = discord.Embed(
                title="🎤 État vocal modifié",
                description=f"{member.mention} — {', '.join(actions)}\n**Modérateur** : {moderator}",
                color=0x1abc9c,
                timestamp=discord.utils.utcnow()
            )
            await send_log(self.bot, "vocal", embed)

        # Connexion/déconnexion normale (pas de modérateur)
        elif before.channel is None and after.channel:
            embed = discord.Embed(
                title="🎤 Connexion vocale",
                description=f"{member.mention} a rejoint {after.channel.mention}",
                color=0x00ff00,
                timestamp=discord.utils.utcnow()
            )
            await send_log(self.bot, "vocal", embed)

        elif before.channel and after.channel is None:
            embed = discord.Embed(
                title="🎤 Déconnexion vocale",
                description=f"{member.mention} a quitté {before.channel.mention}",
                color=0xff0000,
                timestamp=discord.utils.utcnow()
            )
            await send_log(self.bot, "vocal", embed)

    # === COMMANDES ===
    @commands.Cog.listener()
    async def on_interaction(self, interaction: discord.Interaction):
        if not interaction.guild or interaction.guild.id != config.GUILD_ID or interaction.type != discord.InteractionType.application_command:
            return

        args = []
        if interaction.data.get("options"):
            for opt in interaction.data["options"]:
                if opt["type"] in (6, 7, 8):  # User, Channel, Role
                    args.append(f"{opt['name']}: <@{opt['value']}>")
                else:
                    args.append(f"{opt['name']}: {opt['value']}")

        full_command = f"/{interaction.command.name}"
        if args:
            full_command += " " + " ".join(args)

        embed = discord.Embed(
            title="🛠️ Commande slash détectée",
            description=f"**Utilisateur** : {interaction.user.mention}\n"
                        f"**Commande complète** :\n```\n{full_command}\n```",
            color=0x2ecc71,
            timestamp=discord.utils.utcnow()
        )
        await send_log(self.bot, "commands", embed)

async def setup(bot):
    await bot.add_cog(LoggingCog(bot))
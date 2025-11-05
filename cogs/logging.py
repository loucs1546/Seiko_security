# cogs/logging.py
import discord
from discord.ext import commands
import core_config as config
from utils.logging import send_log_to

class LoggingCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def get_voice_action_author(self, guild, target_id, max_age_seconds=15):
        """Récupère l'auteur d'une action vocale (déplacement, déconnexion) depuis les logs d'audit."""
        try:
            async for entry in guild.audit_logs(limit=10):
                if entry.target.id != target_id:
                    continue
                if (discord.utils.utcnow() - entry.created_at).total_seconds() > max_age_seconds:
                    continue
                if entry.action in (
                    discord.AuditLogAction.member_disconnect,
                    discord.AuditLogAction.member_move
                ):
                    return entry.user
                if entry.action == discord.AuditLogAction.member_update:
                    if hasattr(entry.changes, 'channel_id'):
                        return entry.user
        except Exception:
            pass
        return None

    async def get_audit_author(self, guild, target_id, action_type, max_age_seconds=15):
        """Récupère l'auteur d'une action spécifique depuis les logs d'audit."""
        try:
            async for entry in guild.audit_logs(action=action_type, limit=10):
                if entry.target.id == target_id and (discord.utils.utcnow() - entry.created_at).total_seconds() < max_age_seconds:
                    return entry.user
        except Exception:
            pass
        return None

    @commands.Cog.listener()
    async def on_message(self, message):
        if not message.guild or message.guild.id != config.GUILD_ID or message.author.id == self.bot.user.id:
            return
        embed = discord.Embed(
            title="📥 Message reçu",
            description=f"**Auteur** : {message.author.mention}\n**Salon** : {message.channel.mention}",
            color=0x2ecc71,
            timestamp=message.created_at
        )
        if message.content:
            embed.add_field(name="Contenu", value=message.content[:1020], inline=False)
        await send_log_to(self.bot, "messages", embed)

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if not after.guild or after.guild.id != config.GUILD_ID or after.author.bot or before.content == after.content:
            return
        embed = discord.Embed(
            title="✏️ Message édité",
            description=f"Par {after.author.mention} dans {after.channel.mention}",
            color=0xffff00,
            timestamp=discord.utils.utcnow()
        )
        embed.add_field(name="Avant", value=before.content[:1020] or "*(vide)*", inline=False)
        embed.add_field(name="Après", value=after.content[:1020] or "*(vide)*", inline=False)
        await send_log_to(self.bot, "messages", embed)

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if not message.guild or message.guild.id != config.GUILD_ID:
            return

        # Récupérer l'auteur de la suppression
        deleter = None
        try:
            async for entry in message.guild.audit_logs(limit=5, action=discord.AuditLogAction.message_delete):
                if entry.target.id == message.author.id and (discord.utils.utcnow() - entry.created_at).total_seconds() < 10:
                    deleter = entry.user
                    break
        except:
            pass

        # Si le bot a supprimé le message, on le sait déjà (anti-spam, etc.)
        # Sinon, par défaut, c'est l'auteur lui-même
        if deleter is None:
            deleter = message.author

        # Créer l'embed
        embed = discord.Embed(
            title="🗑️ Message supprimé",
            description=f"**Auteur** : {message.author.mention}\n"
                        f"**Salon** : {message.channel.mention}\n"
                        f"**Fait par** : {deleter.mention}",
            color=0xff8800,
            timestamp=message.created_at
        )
        if message.content:
            embed.add_field(name="Contenu", value=message.content, inline=False)
        if message.attachments:
            urls = "\n".join(a.url for a in message.attachments)
            embed.add_field(name="Pièces jointes", value=urls, inline=False)

        # Envoyer dans le salon "messages"
        await send_log_to(self.bot, "messages", embed)

        # Si c'est le bot qui a supprimé le message, loguer aussi dans "securite"
        if deleter.id == self.bot.user.id:
            await send_log_to(self.bot, "securite", embed)

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        if before.guild.id != config.GUILD_ID:
            return

        # --- Rôles ---
        before_roles = set(before.roles)
        after_roles = set(after.roles)
        if before_roles != after_roles:
            moderator = None
            try:
                async for entry in after.guild.audit_logs(limit=5, action=discord.AuditLogAction.member_role_update):
                    if entry.target.id == after.id and (discord.utils.utcnow() - entry.created_at).total_seconds() < 10:
                        moderator = entry.user
                        break
            except:
                pass

            added = after_roles - before_roles
            removed = before_roles - after_roles
            if added or removed:
                desc = ""
                if added:
                    desc += "➕ Ajoutés : " + ", ".join(r.mention for r in added) + "\n"
                if removed:
                    desc += "➖ Retirés : " + ", ".join(r.mention for r in removed)

                embed = discord.Embed(
                    title="👑 Rôles modifiés",
                    description=f"{after.mention}\n{desc}**Fait par** : {moderator.mention if moderator else 'Inconnu'}",
                    color=0xffaa00,
                    timestamp=discord.utils.utcnow()
                )
                await send_log_to(self.bot, "roles", embed)

        # --- Pseudo ---
        if before.nick != after.nick:
            moderator = None
            try:
                async for entry in after.guild.audit_logs(limit=5, action=discord.AuditLogAction.member_update):
                    if entry.target.id == after.id and hasattr(entry.changes, 'nick') and (discord.utils.utcnow() - entry.created_at).total_seconds() < 10:
                        moderator = entry.user
                        break
            except:
                pass

            old_nick = before.nick or before.global_name or before.name
            new_nick = after.nick or after.global_name or after.name

            embed = discord.Embed(
                title="📛 Pseudo modifié",
                description=f"{after.mention}\n**Avant** : {old_nick}\n**Après** : {new_nick}\n**Fait par** : {moderator.mention if moderator else 'Inconnu'}",
                color=0x00ccff,
                timestamp=discord.utils.utcnow()
            )
            await send_log_to(self.bot, "profile", embed)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if member.guild.id != config.GUILD_ID:
            return

        now = discord.utils.utcnow()

        # Connexion
        if before.channel is None and after.channel is not None:
            embed = discord.Embed(
                title="🎤 Connexion vocale",
                description=f"{member.mention} a rejoint {after.channel.mention}\n**Fait par** : {member.mention}",
                color=0x00ff00,
                timestamp=now
            )
            await send_log_to(self.bot, "vocal", embed)

        # Déconnexion
        elif before.channel is not None and after.channel is None:
            moderator = await self.get_voice_action_author(member.guild, member.id)
            fait_par = moderator.mention if moderator else member.mention
            embed = discord.Embed(
                title="🎤 Déconnexion vocale",
                description=f"{member.mention} a quitté {before.channel.mention}\n**Fait par** : {fait_par}",
                color=0xff0000,
                timestamp=now
            )
            await send_log_to(self.bot, "vocal", embed)

        # Déplacement
        elif before.channel and after.channel and before.channel != after.channel:
            moderator = await self.get_voice_action_author(member.guild, member.id)
            fait_par = moderator.mention if moderator else member.mention
            embed = discord.Embed(
                title="🎤 Déplacement vocal",
                description=f"{member.mention} : {before.channel.mention} → {after.channel.mention}\n**Fait par** : {fait_par}",
                color=0xffff00,
                timestamp=now
            )
            await send_log_to(self.bot, "vocal", embed)

        # Mute / Deafen
        elif before.mute != after.mute or before.deaf != after.deaf:
            moderator = await self.get_audit_author(
                member.guild,
                member.id,
                discord.AuditLogAction.member_update,
                max_age_seconds=15
            )
            actions = []
            if before.mute != after.mute:
                actions.append("mute vocal" if after.mute else "unmute vocal")
            if before.deaf != after.deaf:
                actions.append("sourdine" if after.deaf else "fin de sourdine")
            fait_par = moderator.mention if moderator else "Inconnu"
            embed = discord.Embed(
                title="🎤 État vocal modifié",
                description=f"{member.mention} — {', '.join(actions)}\n**Fait par** : {fait_par}",
                color=0x1abc9c,
                timestamp=now
            )
            await send_log_to(self.bot, "vocal", embed)

    @commands.Cog.listener()
    async def on_interaction(self, interaction: discord.Interaction):
        if not interaction.guild or interaction.guild.id != config.GUILD_ID or interaction.type != discord.InteractionType.application_command:
            return

        args = []
        if interaction.data.get("options"):
            for opt in interaction.data["options"]:
                if opt["type"] in (6, 7, 8):
                    args.append(f"{opt['name']}: <@{opt['value']}>")
                else:
                    args.append(f"{opt['name']}: {opt['value']}")

        full_command = f"/{interaction.command.name}"
        if args:
            full_command += " " + " ".join(args)

        embed = discord.Embed(
            title="🛠️ Commande slash détectée",
            description=f"**Utilisateur** : {interaction.user.mention}\n**Commande complète** :\n```\n{full_command}\n```",
            color=0x2ecc71,
            timestamp=discord.utils.utcnow()
        )
        await send_log_to(self.bot, "commands", embed)

async def setup(bot):
    await bot.add_cog(LoggingCog(bot))
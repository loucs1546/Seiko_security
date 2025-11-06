# cogs/logging.py
import discord
from discord.ext import commands
import core_config as config
from utils.logging import send_log_to
import re  # ← Ajoute cette ligne

class LoggingCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if not message.guild or message.guild.id != config.GUILD_ID or message.author.id == self.bot.user.id:
            return

        # === DÉTECTION DES BAVURES ===
        contenu = message.content.strip()
        if contenu:
            # Nettoyer le contenu
            contenu_nettoye = re.sub(r'[^\w\s]', '', contenu.lower())
            mots = [m for m in contenu_nettoye.split() if len(m) >= 2]

            # Moins de 2 mots → bavure
            if len(mots) < 2:
                await self._log_bavure(message, "Moins de 2 mots")
                return

            # Trop de caractères aléatoires
            lettres_frequentes = "aeioulnrst"
            total_car = sum(len(mot) for mot in mots)
            if total_car > 0:
                lettres_freq_count = sum(sum(1 for c in mot if c in lettres_frequentes) for mot in mots)
                ratio = lettres_freq_count / total_car
                if ratio < 0.25:
                    await self._log_bavure(message, "Contenu aléatoire")
                    return

        # === LOG NORMAL ===
        embed = discord.Embed(
            title="📥 Message reçu",
            description=f"**Auteur** : {message.author.mention}\n**Salon** : {message.channel.mention}",
            color=0x2ecc71,
            timestamp=message.created_at
        )
        if message.content:
            embed.add_field(name="Contenu", value=message.content, inline=False)
        if message.attachments:
            urls = "\n".join(a.url for a in message.attachments)
            embed.add_field(name="Pièces jointes", value=urls, inline=False)
        await send_log_to(self.bot, "messages", embed)

    async def _log_bavure(self, message, raison: str):
        """Log une bavure dans le salon dédié."""
        try:
            await message.delete()
        except:
            pass

        embed = discord.Embed(
            title="⚠️ Bavure détectée",
            description=f"**Auteur** : {message.author.mention}\n"
                        f"**Salon** : {message.channel.mention}\n"
                        f"**Raison** : {raison}",
            color=0xff6600,
            timestamp=message.created_at
        )
        if message.content:
            embed.add_field(name="Contenu", value=message.content[:1020], inline=False)
        await send_log_to(self.bot, "bavures", embed)

        try:
            await message.channel.send(
                f"{message.author.mention}, veuillez écrire des messages compréhensibles.",
                delete_after=5
            )
        except:
            pass

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if not after.guild or after.guild.id != config.GUILD_ID or after.author.bot or before.content == after.content:
            return
        embed = discord.Embed(
            title="✏️ Message édité",
            description=f"**Auteur** : {after.author.mention}\n**Salon** : {after.channel.mention}",
            color=0xffff00,
            timestamp=discord.utils.utcnow()
        )
        embed.add_field(name="Avant", value=before.content or "*(vide)*", inline=False)
        embed.add_field(name="Après", value=after.content or "*(vide)*", inline=False)
        await send_log_to(self.bot, "messages", embed)

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if not message.guild or message.guild.id != config.GUILD_ID:
            return

        deleter = None
        try:
            async for entry in message.guild.audit_logs(limit=5, action=discord.AuditLogAction.message_delete):
                if entry.target.id == message.author.id and (discord.utils.utcnow() - entry.created_at).total_seconds() < 10:
                    deleter = entry.user
                    break
        except:
            pass

        if deleter is None:
            deleter = message.author

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

        await send_log_to(self.bot, "messages", embed)

        if deleter.id == self.bot.user.id:
            await send_log_to(self.bot, "securite", embed)

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        if before.guild.id != config.GUILD_ID:
            return

        # === PSEUDO MODIFIÉ (CORRIGÉ) ===
        if before.nick != after.nick:
            moderator = None
            try:
                async for entry in after.guild.audit_logs(limit=5, action=discord.AuditLogAction.member_update):
                    if (
                        entry.target.id == after.id and
                        hasattr(entry.changes, 'nick') and
                        entry.changes.nick[0] == before.nick and
                        entry.changes.nick[1] == after.nick and
                        (discord.utils.utcnow() - entry.created_at).total_seconds() < 10
                    ):
                        moderator = entry.user
                        break
            except Exception:
                pass

            # ✅ Récupère le vrai nom (pas "Aucun")
            old_nick = before.nick or before.global_name or before.name
            new_nick = after.nick or after.global_name or after.name

            embed = discord.Embed(
                title="📛 Pseudo modifié",
                description=f"{after.mention}\n**Avant** : {old_nick}\n**Après** : {new_nick}\n**Fait par** : {moderator.mention if moderator else 'Inconnu'}",
                color=0x00ccff,
                timestamp=discord.utils.utcnow()
            )
            await send_log_to(self.bot, "profile", embed)

        # === RÔLES ===
        before_roles = set(before.roles)
        after_roles = set(after.roles)
        if before_roles != after_roles:
            moderator = None
            try:
                async for entry in after.guild.audit_logs(limit=5, action=discord.AuditLogAction.member_role_update):
                    if entry.target.id == after.id and (discord.utils.utcnow() - entry.created_at).total_seconds() < 10:
                        moderator = entry.user
                        break
            except Exception:
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
                await send_log_to(self.bot, "moderation", embed)

        # === AVATAR ===
        if before.avatar != after.avatar:
            embed = discord.Embed(
                title="🖼️ Avatar modifié",
                description=f"{after.mention}",
                color=0x00ccff,
                timestamp=discord.utils.utcnow()
            )
            embed.set_thumbnail(url=after.display_avatar.url)
            await send_log_to(self.bot, "profile", embed)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if member.guild.id != config.GUILD_ID:
            return

        now = discord.utils.utcnow()

        if before.channel is None and after.channel is not None:
            embed = discord.Embed(
                title="🎤 Connexion vocale",
                description=f"{member.mention} a rejoint {after.channel.mention}\n**Fait par** : {member.mention}",
                color=0x00ff00,
                timestamp=now
            )
            await send_log_to(self.bot, "vocal", embed)

        elif before.channel is not None and after.channel is None:
            moderator = None
            try:
                async for entry in member.guild.audit_logs(limit=5, action=discord.AuditLogAction.member_disconnect):
                    if entry.target.id == member.id and (discord.utils.utcnow() - entry.created_at).total_seconds() < 10:
                        moderator = entry.user
                        break
            except Exception:
                pass

            fait_par = moderator.mention if moderator else member.mention
            embed = discord.Embed(
                title="🎤 Déconnexion vocale",
                description=f"{member.mention} a quitté {before.channel.mention}\n**Fait par** : {fait_par}",
                color=0xff0000,
                timestamp=now
            )
            await send_log_to(self.bot, "vocal", embed)

        elif before.channel and after.channel and before.channel != after.channel:
            moderator = None
            try:
                async for entry in member.guild.audit_logs(limit=5, action=discord.AuditLogAction.member_move):
                    if entry.target.id == member.id and (discord.utils.utcnow() - entry.created_at).total_seconds() < 10:
                        moderator = entry.user
                        break
            except Exception:
                pass

            fait_par = moderator.mention if moderator else member.mention
            embed = discord.Embed(
                title="🎤 Déplacement vocal",
                description=f"{member.mention} : {before.channel.mention} → {after.channel.mention}\n**Fait par** : {fait_par}",
                color=0xffff00,
                timestamp=now
            )
            await send_log_to(self.bot, "vocal", embed)

        elif before.mute != after.mute or before.deaf != after.deaf:
            moderator = None
            try:
                async for entry in member.guild.audit_logs(limit=5, action=discord.AuditLogAction.member_update):
                    if entry.target.id == member.id and (discord.utils.utcnow() - entry.created_at).total_seconds() < 10:
                        moderator = entry.user
                        break
            except Exception:
                pass

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

        args = {}
        if interaction.data.get("options"):
            for opt in interaction.data["options"]:
                args[opt["name"]] = opt.get("value")

        full_command = f"/{interaction.command.name}"
        reason = args.get("raison", "")

        # === LOG DES SANCTIONS SANS RAISON (dans 'bavures') ===
        if interaction.command.name in ("kick", "ban", "warn") and (not reason or reason == "Aucune raison"):
            embed = discord.Embed(
                title="⚠️ Bavure détectée",
                description=f"**Commande** : {full_command}\n**Auteur** : {interaction.user.mention}\n**Cible** : {args.get('pseudo', 'Inconnu')}\n**Raison** : *Aucune*",
                color=0xff6600,
                timestamp=discord.utils.utcnow()
            )
            await send_log_to(self.bot, "bavures", embed)

        # === LOG NORMAL DANS 'commands' ===
        desc = f"**Utilisateur** : {interaction.user.mention}\n**Commande complète** :\n```\n{full_command}"
        for name, value in args.items():
            desc += f" --{name} {value}"
        desc += "\n```"

        embed = discord.Embed(
            title="🛠️ Commande slash détectée",
            description=desc,
            color=0x2ecc71,
            timestamp=discord.utils.utcnow()
        )
        await send_log_to(self.bot, "commands", embed)

async def setup(bot):
    await bot.add_cog(LoggingCog(bot))
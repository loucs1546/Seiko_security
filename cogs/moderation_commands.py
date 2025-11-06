# cogs/moderation_commands.py
import discord
from discord.ext import commands
from datetime import datetime
import core_config as config
from utils.logging import send_log_to
import re

def get_sanction_channel(bot):
    return bot.get_channel(config.CONFIG["logs"].get("sanctions"))

def est_bavure_raison(raison: str) -> bool:
    """Détecte une raison invalide : besoin de 2 vrais mots (avec voyelle)."""
    if not raison or raison.strip().lower() in ("", "aucune raison"):
        return True
    mots = re.findall(r'\b[a-zA-Z]{2,}\b', raison)
    if len(mots) < 2:
        return True
    voyelles = "aeiouy"
    valid_count = 0
    for mot in mots:
        if any(c.lower() in voyelles for c in mot):
            valid_count += 1
            if valid_count >= 2:
                return False
    return True

class BavureReviewView(View):
    def __init__(self, mod_author: discord.Member, target: discord.Member, command_name: str, reason: str, interaction: discord.Interaction):
        super().__init__(timeout=600)
        self.mod_author = mod_author
        self.target = target
        self.command_name = command_name
        self.reason = reason
        self.original_interaction = interaction

    @discord.ui.button(label="✅ Accepter", style=discord.ButtonStyle.green)
    async def accept(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Exécuter la commande
        if self.command_name == "warn":
            embed = discord.Embed(
                title="⚠️ Avertissement",
                description=f"**Membre** : {self.target.mention}\n**Modérateur** : {self.mod_author.mention}\n**Raison** : {self.reason}",
                color=0xffff00,
                timestamp=discord.utils.utcnow()
            )
            ch = get_sanction_channel(self.original_interaction.client)
            if ch: await ch.send(embed=embed)
            await self.original_interaction.followup.send(f"✅ Avertissement envoyé à {self.target.mention}.", ephemeral=True)

        elif self.command_name in ("kick", "ban"):
            await self.target.send(f"⚠️ Vous avez été {'expulsé' if self.command_name == 'kick' else 'banni'} pour : **{self.reason}**.")
            if self.command_name == "kick":
                await self.target.kick(reason=self.reason)
                action = "expulsé"
            else:
                await self.target.ban(reason=self.reason)
                action = "banni"
            embed = discord.Embed(
                title=f"{'👢 Kick' if self.command_name == 'kick' else '🔨 Ban'}",
                description=f"**Membre** : {self.target.mention}\n**Modérateur** : {self.mod_author.mention}\n**Raison** : {self.reason}",
                color=0xff0000 if self.command_name == "ban" else 0xff9900,
                timestamp=discord.utils.utcnow()
            )
            ch = get_sanction_channel(self.original_interaction.client)
            if ch: await ch.send(embed=embed)
            await self.original_interaction.followup.send(f"✅ {self.target.mention} {action}.", ephemeral=True)

        # Log dans bavures-sanctions
        log_embed = discord.Embed(
            title="✅ Bavure acceptée",
            description=f"**Modérateur** : {self.mod_author.mention}\n**Cible** : {self.target.mention}\n**Commande** : /{self.command_name}\n**Raison** : {self.reason}",
            color=0x2ecc71,
            timestamp=discord.utils.utcnow()
        )
        await send_log_to(self.original_interaction.client, "bavures-sanctions", log_embed)
        await interaction.response.edit_message(content="✅ Sanction appliquée.", view=None)

    @discord.ui.button(label="❌ Refuser", style=discord.ButtonStyle.red)
    async def reject(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Log dans bavures-sanctions
        log_embed = discord.Embed(
            title="❌ Bavure refusée",
            description=f"**Modérateur** : {self.mod_author.mention}\n**Cible** : {self.target.mention}\n**Commande** : /{self.command_name}\n**Raison** : {self.reason}",
            color=0xff6600,
            timestamp=discord.utils.utcnow()
        )
        await send_log_to(self.original_interaction.client, "bavures-sanctions", log_embed)
        await interaction.response.edit_message(content="❌ Sanction annulée.", view=None)

class ModerationCommandsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # === COMMANDES DE SÉCURITÉ ===
    @discord.app_commands.command(name="anti-spam", description="Active/désactive l'anti-spam")
    @discord.app_commands.checks.has_permissions(administrator=True)
    async def anti_spam(self, interaction: discord.Interaction, actif: bool):
        config.CONFIG["security"]["anti_spam"] = actif
        await interaction.response.send_message(f"✅ Anti-spam {'activé' if actif else 'désactivé'}.", ephemeral=True)

    @discord.app_commands.command(name="anti-raid", description="Active/désactive l'anti-raid")
    @discord.app_commands.checks.has_permissions(administrator=True)
    async def anti_raid(self, interaction: discord.Interaction, actif: bool):
        config.CONFIG["security"]["anti_raid"] = actif
        await interaction.response.send_message(f"✅ Anti-raid {'activé' if actif else 'désactivé'}.", ephemeral=True)

    @discord.app_commands.command(name="anti-hack", description="Active/désactive l'anti-hack")
    @discord.app_commands.checks.has_permissions(administrator=True)
    async def anti_hack(self, interaction: discord.Interaction, actif: bool):
        config.CONFIG["security"]["anti_hack"] = actif
        await interaction.response.send_message(f"✅ Anti-hack {'activé' if actif else 'désactivé'}.", ephemeral=True)

    # === MODÉRATION ===
    @discord.app_commands.command(name="ping", description="Affiche la latence du bot")
    async def ping(self, interaction: discord.Interaction):
        latency = round(self.bot.latency * 1000)
        await interaction.response.send_message(f"🏓 Pong ! Latence : **{latency} ms**", ephemeral=True)

    @discord.app_commands.command(name="clear-salon", description="Supprime tous les messages du salon")
    @discord.app_commands.checks.has_permissions(manage_messages=True)
    async def clear_salon(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        deleted = await interaction.channel.purge(limit=1000)
        await interaction.followup.send(f"🧹 **{len(deleted)}** messages supprimés.", ephemeral=True)

    @discord.app_commands.command(name="delete-salon", description="Supprime un salon")
    @discord.app_commands.describe(salon="Salon à supprimer")
    @discord.app_commands.checks.has_permissions(manage_channels=True)
    async def delete_salon(self, interaction: discord.Interaction, salon: discord.TextChannel):
        await salon.delete(reason=f"Supprimé par {interaction.user}")
        await interaction.response.send_message(f"✅ Salon **{salon.name}** supprimé.", ephemeral=True)

    @discord.app_commands.command(name="delete-categorie", description="Supprime une catégorie et ses salons")
    @discord.app_commands.describe(categorie="Catégorie à supprimer")
    @discord.app_commands.checks.has_permissions(manage_channels=True)
    async def delete_categorie(self, interaction: discord.Interaction, categorie: discord.CategoryChannel):
        await interaction.response.send_message("✅ Suppression en cours...", ephemeral=True)
        for channel in categorie.channels:
            try:
                await channel.delete(reason=f"Supprimé avec la catégorie par {interaction.user}")
            except:
                pass
        try:
            await categorie.delete(reason=f"Supprimé par {interaction.user}")
        except:
            pass

    @discord.app_commands.command(name="say", description="Envoie un message dans un salon")
    @discord.app_commands.describe(salon="Salon cible", contenu="Message à envoyer")
    @discord.app_commands.checks.has_permissions(manage_messages=True)
    async def say(self, interaction: discord.Interaction, salon: discord.TextChannel, contenu: str):
        contenu_nettoye = contenu.replace("\\n", "\n")
        await salon.send(contenu_nettoye)
        await interaction.response.send_message(f"✅ Message envoyé dans {salon.mention}.", ephemeral=True)

    @discord.app_commands.command(name="warn", description="Avertit un membre")
    @discord.app_commands.describe(pseudo="Membre à avertir", raison="Raison de l'avertissement")
    @discord.app_commands.checks.has_permissions(manage_messages=True)
    async def warn(self, interaction: discord.Interaction, pseudo: discord.Member, raison: str = "Aucune raison"):
        if self._est_bavure_raison(raison):
            embed = discord.Embed(
                title="⚠️ Bavure détectée",
                description=f"**Modérateur** : {interaction.user.mention}\n**Cible** : {pseudo.mention}\n**Commande** : `/warn`\n**Raison** : *{raison}*",
                color=0xff6600,
                timestamp=discord.utils.utcnow()
            )
            await send_log_to(self.bot, "bavures", embed)
            view = BavureReviewView(interaction.user, pseudo, "warn", raison, interaction)
            await interaction.response.send_message(
                "⚠️ Cette sanction semble être une bavure. Voulez-vous la valider ?",
                view=view,
                ephemeral=True
            )
            return

        # Exécution normale
        embed = discord.Embed(
            title="⚠️ Avertissement",
            description=f"**Membre** : {pseudo.mention}\n**Modérateur** : {interaction.user.mention}\n**Raison** : {raison}",
            color=0xffff00,
            timestamp=discord.utils.utcnow()
        )
        ch = get_sanction_channel(self.bot)
        if ch: await ch.send(embed=embed)
        await interaction.response.send_message(f"✅ Avertissement envoyé.", ephemeral=True)

    @discord.app_commands.command(name="kick", description="Expulse un membre")
    @discord.app_commands.describe(pseudo="Membre à expulser", raison="Raison du kick")
    @discord.app_commands.checks.has_permissions(kick_members=True)
    async def kick(self, interaction: discord.Interaction, pseudo: discord.Member, raison: str = "Aucune raison"):
        if self._est_bavure_raison(raison):
            embed = discord.Embed(
                title="⚠️ Bavure détectée",
                description=f"**Modérateur** : {interaction.user.mention}\n**Cible** : {pseudo.mention}\n**Commande** : `/kick`\n**Raison** : *{raison}*",
                color=0xff6600,
                timestamp=discord.utils.utcnow()
            )
            await send_log_to(self.bot, "bavures", embed)
            view = BavureReviewView(interaction.user, pseudo, "kick", raison, interaction)
            await interaction.response.send_message(
                "⚠️ Cette sanction semble être une bavure. Voulez-vous la valider ?",
                view=view,
                ephemeral=True
            )
            return

        # Exécution normale
        try:
            await pseudo.send(f"⚠️ Vous avez été expulsé de **{interaction.guild.name}** pour : **{raison}**.")
        except:
            pass
        await pseudo.kick(reason=raison)
        embed = discord.Embed(
            title="👢 Kick",
            description=f"**Membre** : {pseudo.mention}\n**Modérateur** : {interaction.user.mention}\n**Raison** : {raison}",
            color=0xff9900,
            timestamp=discord.utils.utcnow()
        )
        ch = get_sanction_channel(self.bot)
        if ch: await ch.send(embed=embed)
        await interaction.response.send_message(f"✅ {pseudo.mention} expulsé.", ephemeral=True)

    @discord.app_commands.command(name="ban", description="Bannit un membre")
    @discord.app_commands.describe(pseudo="Membre à bannir", temps="Jours de suppression des messages (0 = aucun)", raison="Raison du ban")
    @discord.app_commands.checks.has_permissions(ban_members=True)
    async def ban(self, interaction: discord.Interaction, pseudo: discord.Member, temps: int = 0, raison: str = "Aucune raison"):
        if self._est_bavure_raison(raison):
            embed = discord.Embed(
                title="⚠️ Bavure détectée",
                description=f"**Modérateur** : {interaction.user.mention}\n**Cible** : {pseudo.mention}\n**Commande** : `/ban`\n**Raison** : *{raison}*",
                color=0xff6600,
                timestamp=discord.utils.utcnow()
            )
            await send_log_to(self.bot, "bavures", embed)
            view = BavureReviewView(interaction.user, pseudo, "ban", raison, interaction)
            await interaction.response.send_message(
                "⚠️ Cette sanction semble être une bavure. Voulez-vous la valider ?",
                view=view,
                ephemeral=True
            )
            return

        # Exécution normale
        try:
            await pseudo.send(f"⚠️ Vous avez été banni de **{interaction.guild.name}** pour : **{raison}**.")
        except:
            pass
        await pseudo.ban(reason=raison, delete_message_days=temps)
        embed = discord.Embed(
            title="🔨 Ban",
            description=f"**Membre** : {pseudo.mention}\n**Modérateur** : {interaction.user.mention}\n**Raison** : {raison}",
            color=0xff0000,
            timestamp=discord.utils.utcnow()
        )
        ch = get_sanction_channel(self.bot)
        if ch: await ch.send(embed=embed)
        await interaction.response.send_message(f"✅ {pseudo.mention} banni.", ephemeral=True)

    @discord.app_commands.command(name="reachlog", description="Affiche le dernier log d'audit")
    @discord.app_commands.checks.has_permissions(administrator=True)
    async def reachlog(self, interaction: discord.Interaction):
        try:
            async for entry in interaction.guild.audit_logs(limit=1):
                log_msg = f"**{entry.action.name}**\n"
                log_msg += f"**Cible** : {getattr(entry, 'target', 'Inconnue')}\n"
                log_msg += f"**Auteur** : {entry.user}\n"
                log_msg += f"**Date** : <t:{int(entry.created_at.timestamp())}:R>"
                await interaction.response.send_message(log_msg, ephemeral=True)
                return
            await interaction.response.send_message("📭 Aucun log trouvé.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Erreur : {e}", ephemeral=True)

    @discord.app_commands.command(name="reach-id", description="Résout un ID Discord (utilisateur, salon, rôle)")
    @discord.app_commands.describe(id="ID à résoudre")
    @discord.app_commands.checks.has_permissions(administrator=True)
    async def reach_id(self, interaction: discord.Interaction, id: str):
        try:
            obj_id = int(id)
        except ValueError:
            await interaction.response.send_message("❌ ID invalide. Doit être un nombre.", ephemeral=True)
            return

        guild = interaction.guild
        results = []

        member = guild.get_member(obj_id)
        if member:
            results.append(f"👤 **Membre** : {member.mention} (`{member}`)")

        channel = guild.get_channel(obj_id)
        if channel:
            results.append(f"💬 **Salon** : {channel.mention} (`{channel.name}`)")

        role = guild.get_role(obj_id)
        if role:
            results.append(f"👑 **Rôle** : {role.mention} (`{role.name}`)")

        if results:
            await interaction.response.send_message(
                f"🔍 Résultats pour l'ID `{id}` :\n" + "\n".join(results),
                ephemeral=True
            )
        else:
            await interaction.response.send_message(
                f"❌ Aucun utilisateur, salon ou rôle trouvé avec l'ID `{id}`.",
                ephemeral=True
            )

async def setup(bot):
    await bot.add_cog(ModerationCommandsCog(bot))
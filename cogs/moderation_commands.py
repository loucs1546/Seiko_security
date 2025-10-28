# cogs/moderation_commands.py
import discord
from discord.ext import commands
import core_config as config
from utils.logging import send_log

def get_sanction_channel(bot):
    return bot.get_channel(config.CONFIG["logs"].get("sanctions"))

class ModerationCommandsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # === SÉCURITÉ (inchangé) ===
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

    # === COMMANDES DE MODÉRATION (toutes restaurées) ===
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
        await interaction.response.send_message(
            f"✅ Suppression de la catégorie **{categorie.name}** en cours...",
            ephemeral=True
        )
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
        await salon.send(contenu)
        await interaction.response.send_message(f"✅ Message envoyé dans {salon.mention}.", ephemeral=True)

    @discord.app_commands.command(name="kick", description="Expulse un membre")
    @discord.app_commands.describe(pseudo="Membre à expulser", raison="Raison du kick")
    @discord.app_commands.checks.has_permissions(kick_members=True)
    async def kick(self, interaction: discord.Interaction, pseudo: discord.Member, raison: str = "Aucune raison"):
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
        sanction_ch = get_sanction_channel(self.bot)
        if sanction_ch:
            await sanction_ch.send(embed=embed)
        await interaction.response.send_message(f"✅ {pseudo.mention} expulsé.", ephemeral=True)

    @discord.app_commands.command(name="ban", description="Bannit un membre")
    @discord.app_commands.describe(pseudo="Membre à bannir", temps="Jours de suppression des messages (0 = aucun)", raison="Raison du ban")
    @discord.app_commands.checks.has_permissions(ban_members=True)
    async def ban(self, interaction: discord.Interaction, pseudo: discord.Member, temps: int = 0, raison: str = "Aucune raison"):
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
        sanction_ch = get_sanction_channel(self.bot)
        if sanction_ch:
            await sanction_ch.send(embed=embed)
        await interaction.response.send_message(f"✅ {pseudo.mention} banni.", ephemeral=True)

    @discord.app_commands.command(name="warn", description="Avertit un membre")
    @discord.app_commands.describe(pseudo="Membre à avertir", raison="Raison de l'avertissement")
    @discord.app_commands.checks.has_permissions(manage_messages=True)
    async def warn(self, interaction: discord.Interaction, pseudo: discord.Member, raison: str = "Aucune raison"):
        embed = discord.Embed(
            title="⚠️ Avertissement",
            description=f"**Membre** : {pseudo.mention}\n**Modérateur** : {interaction.user.mention}\n**Raison** : {raison}",
            color=0xffff00,
            timestamp=discord.utils.utcnow()
        )
        sanction_ch = get_sanction_channel(self.bot)
        if sanction_ch:
            await sanction_ch.send(embed=embed)
        await interaction.response.send_message(f"✅ Avertissement envoyé pour {pseudo.mention}.", ephemeral=True)

    # === NOUVELLE COMMANDE : /reachlog ===
    @discord.app_commands.command(name="reachlog", description="Affiche le dernier log d'audit du serveur")
    @discord.app_commands.checks.has_permissions(administrator=True)
    async def reachlog(self, interaction: discord.Interaction):
        try:
            async for entry in interaction.guild.audit_logs(limit=1):
                log_msg = f"**{entry.action.name}**\n"
                log_msg += f"**Cible** : {entry.target}\n"
                log_msg += f"**Auteur** : {entry.user}\n"
                log_msg += f"**Raison** : {entry.reason or 'Aucune'}\n"
                log_msg += f"**Date** : <t:{int(entry.created_at.timestamp())}:R>"
                await interaction.response.send_message(log_msg, ephemeral=True)
                return
            await interaction.response.send_message("📭 Aucun log d'audit trouvé.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Erreur : {str(e)}", ephemeral=True)
    @discord.app_commands.command(name="logs", description="Définit le salon pour un type de log")
    @discord.app_commands.describe(
        type="Type de log",
        salon="Salon de destination"
    )
    @discord.app_commands.choices(type=[
        discord.app_commands.Choice(name="messages", value="messages"),
        discord.app_commands.Choice(name="moderation", value="moderation"),
        discord.app_commands.Choice(name="ticket", value="ticket"),
        discord.app_commands.Choice(name="vocal", value="vocal"),
        discord.app_commands.Choice(name="securite", value="securite")
    ])
    @discord.app_commands.checks.has_permissions(administrator=True)
    async def logs(self, interaction: discord.Interaction, type: str, salon: discord.TextChannel):
        import core_config as config
        config.CONFIG["logs"][type] = salon.id
        await interaction.response.send_message(f"✅ Salon de logs **{type}** défini sur {salon.mention}.", ephemeral=True)

    @discord.app_commands.command(name="scan-deleted", description="Récupère les suppressions de messages récentes manquées")
    @discord.app_commands.checks.has_permissions(administrator=True)
    async def scan_deleted(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        count = 0
        async for entry in interaction.guild.audit_logs(action=discord.AuditLogAction.message_delete, limit=50):
            if (discord.utils.utcnow() - entry.created_at).total_seconds() > 300:
                break
            embed = discord.Embed(
                title="🗑️ Message supprimé (récupéré)",
                description=f"**Auteur** : {entry.target}\n**Supprimé par** : {entry.user}",
                color=0xff8800,
                timestamp=entry.created_at
            )
            from utils.logging import send_log_to
            await send_log_to(self.bot, "messages", embed)
            count += 1
        await interaction.followup.send(f"✅ {count} suppressions récupérées.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(ModerationCommandsCog(bot))
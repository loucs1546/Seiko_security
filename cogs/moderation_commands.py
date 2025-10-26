# cogs/moderation_commands.py
import discord
from discord.ext import commands
import core_config as config
from utils.logging import send_log

def get_sanction_channel(bot):
    channel_id = config.LOG_CHANNELS.get("sanctions")
    return bot.get_channel(channel_id)

class ModerationCommandsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.app_commands.command(name="ping", description="Affiche le statut et la latence du bot")
    async def ping(self, interaction: discord.Interaction):
        latency = round(self.bot.latency * 1000)
        embed = discord.Embed(
            title="🏓 Pong !",
            color=0x2ecc71,
            timestamp=discord.utils.utcnow()
        )
        embed.add_field(name="Latence", value=f"`{latency} ms`", inline=True)
        embed.add_field(name="Serveur", value=f"`{interaction.guild.name if interaction.guild else 'DM'}`", inline=True)
        embed.set_footer(text=f"Bot : {self.bot.user}", icon_url=self.bot.user.display_avatar.url)
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @discord.app_commands.command(name="clear-salon", description="Supprime tous les messages du salon")
    @discord.app_commands.checks.has_permissions(manage_messages=True)
    async def clear_salon(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        deleted = await interaction.channel.purge(limit=1000)
        await interaction.followup.send(f"🧹 **{len(deleted)}** messages supprimés.", ephemeral=True)

    @discord.app_commands.command(name="delete-salon", description="Supprime le salon spécifié")
    @discord.app_commands.describe(salon="Salon à supprimer")
    @discord.app_commands.checks.has_permissions(manage_channels=True)
    async def delete_salon(self, interaction: discord.Interaction, salon: discord.TextChannel):
        await salon.delete(reason=f"Supprimé par {interaction.user}")
        await interaction.response.send_message(f"✅ Salon **{salon.name}** supprimé.", ephemeral=True)

    @discord.app_commands.command(name="delete-categorie", description="Supprime une catégorie et ses salons")
    @discord.app_commands.describe(categorie="Catégorie à supprimer")
    @discord.app_commands.checks.has_permissions(manage_channels=True)
    async def delete_categorie(self, interaction: discord.Interaction, categorie: discord.CategoryChannel):
        await interaction.response.defer(ephemeral=True)
        count = len(categorie.channels)
        await categorie.delete(reason=f"Supprimé par {interaction.user}")
        await interaction.followup.send(f"✅ Catégorie **{categorie.name}** et ses **{count}** salons supprimés.", ephemeral=True)

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
    @discord.app_commands.describe(pseudo="Membre à bannir", temps="Durée (en jours, 0 = permanent)", raison="Raison du ban")
    @discord.app_commands.checks.has_permissions(ban_members=True)
    async def ban(self, interaction: discord.Interaction, pseudo: discord.Member, temps: int = 0, raison: str = "Aucune raison"):
        try:
            await pseudo.send(f"⚠️ Vous avez été banni de **{interaction.guild.name}** pour : **{raison}**.")
        except:
            pass
        await pseudo.ban(reason=raison, delete_message_days=temps)
        embed = discord.Embed(
            title="🔨 Ban",
            description=f"**Membre** : {pseudo.mention}\n**Modérateur** : {interaction.user.mention}\n**Durée** : {'Permanent' if temps == 0 else f'{temps} jours'}\n**Raison** : {raison}",
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

# ⚠️ PAS DE cog_load ICI !
async def setup(bot):
    await bot.add_cog(ModerationCommandsCog(bot))
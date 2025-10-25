# cogs/log_setup.py
import discord
from discord.ext import commands
import core_config as config

class LogSetupCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.app_commands.command(
        name="create-categorie-log",
        description="Crée une catégorie complète de salons de surveillance"
    )
    @discord.app_commands.checks.has_permissions(administrator=True)
    async def create_log_category(self, interaction: discord.Interaction):
        guild = interaction.guild

        # Vérifie si une catégorie de logs existe déjà
        for category in guild.categories:
            if "log" in category.name.lower() or "surveillance" in category.name.lower():
                await interaction.response.send_message(
                    f"❌ Une catégorie de surveillance existe déjà : **{category.name}**",
                    ephemeral=True
                )
                return

        # Crée la catégorie
        category = await guild.create_category(
            name="🔐・Surveillance",
            overwrites={
                guild.default_role: discord.PermissionOverwrite(read_messages=False),
                guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
            }
        )

        # Liste des salons à créer
        salon_configs = [
            ("📜・messages", "messages"),
            ("🎤・vocal", "vocal"),
            ("🎫・tickets", "tickets"),
            ("🛠️・commandes", "commands"),
            ("👑・rôles", "roles"),
            ("📛・profil", "profile"),
            ("🔍・contenu", "content"),
            ("🚨・alertes", "alerts")
        ]

        # Créer les salons et enregistrer les ID
        channel_ids = {}
        for name, key in salon_configs:
            channel = await guild.create_text_channel(name=name, category=category)
            channel_ids[key] = channel.id

        config.LOG_CHANNELS = channel_ids
        await interaction.response.send_message(
            f"✅ Catégorie **{category.name}** créée avec {len(salon_configs)} salons de surveillance !",
            ephemeral=True
        )

async def setup(bot):
    await bot.add_cog(LogSetupCog(bot))
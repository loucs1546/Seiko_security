# cogs/log_setup.py
import discord
from discord.ext import commands
import core_config as config

class LogSetupCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def create_log_category_callback(self, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ Réservé aux administrateurs.", ephemeral=True)
            return

        await interaction.response.defer(ephemeral=True)
        guild = interaction.guild

        for category in guild.categories:
            if "log" in category.name.lower() or "surveillance" in category.name.lower():
                await interaction.followup.send(
                    f"❌ Une catégorie de logs existe déjà : **{category.name}**",
                    ephemeral=True
                )
                return

        try:
            category = await guild.create_category(
                name="🔐・Surveillance",
                overwrites={
                    guild.default_role: discord.PermissionOverwrite(read_messages=False),
                    guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
                }
            )

            salon_configs = [
                ("📜・messages", "messages"),
                ("🎤・vocal", "vocal"),
                ("🎫・tickets", "tickets"),
                ("🛠️・commandes", "commands"),
                ("👑・rôles", "roles"),
                ("📛・profil", "profile"),
                ("🔍・contenu", "content"),
                ("🚨・alertes", "alerts"),
                ("⚖️・sanctions", "sanctions")
            ]

            channel_ids = {}
            for name, key in salon_configs:
                channel = await guild.create_text_channel(name=name, category=category)
                channel_ids[key] = channel.id

            config.LOG_CHANNELS = channel_ids

            await interaction.followup.send(
                f"✅ Catégorie **{category.name}** créée avec {len(salon_configs)} salons !",
                ephemeral=True
            )

        except Exception as e:
            await interaction.followup.send(f"❌ Erreur : {str(e)}", ephemeral=True)

    async def cog_load(self):
        guild = discord.Object(id=config.GUILD_ID)
        command = discord.app_commands.Command(
            name="create-categorie-log",
            description="Crée une catégorie complète de salons de surveillance",
            callback=self.create_log_category_callback
        )
        self.bot.tree.add_command(command, guild=guild)

async def setup(bot):
    await bot.add_cog(LogSetupCog(bot))
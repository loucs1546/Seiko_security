# cogs/log_setup.py
import discord
from discord.ext import commands
import core_config as config

class LogSetupCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.app_commands.command(name="add-cat-log", description="Crée une catégorie complète de salons de surveillance")
    @discord.app_commands.checks.has_permissions(administrator=True)
    async def add_cat_log(self, interaction: discord.Interaction):
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
            # Meilleure gestion des overwrites : s'assurer que guild.me existe, sinon utiliser bot.user
            bot_member = guild.me or guild.get_member(self.bot.user.id)
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(read_messages=False),
            }
            if bot_member:
                overwrites[bot_member] = discord.PermissionOverwrite(read_messages=True, send_messages=True)

            category = await guild.create_category(
                name="🔐・Surveillance",
                overwrites=overwrites
            )

            salon_configs = [
                ("📜・messages", "messages"),
                ("🎤・vocal", "vocal"),
                ("🎫・tickets", "ticket"),
                ("🛠️・commandes", "commands"),
                ("👑・rôles", "moderation"),
                ("📛・profil", "profile"),
                ("🔍・contenu", "content"),
                ("🚨・alertes", "alerts"),
                ("⚖️・sanctions", "sanctions"),
                ("🎉・giveaway", "giveaway")
            ]

            channel_ids = {}
            for name, key in salon_configs:
                channel = await guild.create_text_channel(name=name, category=category)
                channel_ids[key] = channel.id

            # Stockage cohérent : utiliser config.CONFIG["logs"] pour être retrouvé par le reste du bot
            if not isinstance(config.CONFIG, dict):
                config.CONFIG = {}
            config.CONFIG.setdefault("logs", {})
            config.CONFIG["logs"].update(channel_ids)

            await interaction.followup.send(
                f"✅ Catégorie **{category.name}** créée avec {len(salon_configs)} salons !\n"
                "Les salons ont été enregistrés dans la configuration.",
                ephemeral=True
            )

        except Exception as e:
            await interaction.followup.send(f"❌ Erreur : {str(e)}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(LogSetupCog(bot))
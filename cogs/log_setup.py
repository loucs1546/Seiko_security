# cogs/log_setup.py
import discord
from discord.ext import commands
import core_config as config

class LogSetupCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def _create_category(self, interaction: discord.Interaction):
        # Méthode réutilisable pour créer la catégorie + salons
        # interaction peut être un discord.Interaction provenant d'une commande ou d'un bouton
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

            # Stockage cohérent pour le reste du bot
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

    @discord.app_commands.command(name="add-cat-log", description="Crée une catégorie complète de salons de surveillance")
    @discord.app_commands.checks.has_permissions(administrator=True)
    async def add_cat_log(self, interaction: discord.Interaction):
        # Utilise la méthode réutilisable
        await self._create_category(interaction)

# View avec bouton "Créer" qui appelle la même méthode
class LogSetupView(discord.ui.View):
    def __init__(self, cog: LogSetupCog):
        super().__init__(timeout=None)  # persistante
        self.cog = cog

    @discord.ui.button(label="Créer", style=discord.ButtonStyle.green, custom_id="add-cat-log:create")
    async def create_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Vérifie les permissions administrateur avant d'exécuter
        if not interaction.user.guild_permissions.administrator:
            try:
                await interaction.response.send_message("❌ Permissions insuffisantes.", ephemeral=True)
            except Exception:
                await interaction.followup.send("❌ Permissions insuffisantes.", ephemeral=True)
            return

        await self.cog._create_category(interaction)

async def setup(bot):
    await bot.add_cog(LogSetupCog(bot))
    # Enregistrer la view persistante (utile si l'interface existante envoie un bouton avec ce custom_id)
    cog = bot.get_cog("LogSetupCog")
    if cog:
        try:
            bot.add_view(LogSetupView(cog))
        except Exception:
            # si déjà ajouté ou erreur, on ignore pour éviter crash
            pass
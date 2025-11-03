import discord
from discord.ext import commands
from discord import app_commands
import core_config as config

class ToggleButton(discord.ui.Button):
    def __init__(self, label, style, config_key, bot):
        super().__init__(label=label, style=style)
        self.config_key = config_key
        self.bot = bot
        self.update_label()

    def update_label(self):
        state = config.CONFIG.get("security", {}).get(self.config_key, False)
        self.label = f"{self.label.split(' ')[0]} {'✅' if state else '❌'}"

    async def callback(self, interaction: discord.Interaction):
        # Toggle la config
        current = config.CONFIG.setdefault("security", {}).get(self.config_key, False)
        config.CONFIG["security"][self.config_key] = not current
        self.update_label()
        await interaction.response.edit_message(view=self.view)

class SecurityView(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=180)
        self.add_item(ToggleButton("Anti-spam", discord.ButtonStyle.danger, "anti_spam", bot))
        self.add_item(ToggleButton("Anti-hack", discord.ButtonStyle.danger, "anti_hack", bot))
        self.add_item(ToggleButton("Anti-raid", discord.ButtonStyle.danger, "anti_raid", bot))
        self.add_item(CloseButton())

class CloseButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Fermer", style=discord.ButtonStyle.secondary)

    async def callback(self, interaction: discord.Interaction):
        await interaction.message.delete()

class LogsSetupView(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=180)
        self.bot = bot
        self.add_item(CreateLogsButton(bot))
        self.add_item(ManualLogsButton(bot))
        self.add_item(CloseButton())

class CreateLogsButton(discord.ui.Button):
    def __init__(self, bot):
        super().__init__(label="Créer", style=discord.ButtonStyle.success)
        self.bot = bot

    async def callback(self, interaction: discord.Interaction):
        # Import log_setup et créer les salons/catégories
        try:
            from log_setup import LOG_CATEGORIES
            guild = interaction.guild
            created = []
            for cat_name, channels in LOG_CATEGORIES.items():
                category = await guild.create_category(cat_name)
                for ch_name in channels:
                    ch = await guild.create_text_channel(ch_name, category=category)
                    created.append(f"{cat_name}/{ch_name}")
            await interaction.response.send_message(
                f"✅ Catégories et salons créés :\n" + "\n".join(created),
                ephemeral=True
            )
        except Exception as e:
            await interaction.response.send_message(f"❌ Erreur création logs : {e}", ephemeral=True)

class ManualLogsButton(discord.ui.Button):
    def __init__(self, bot):
        super().__init__(label="Manuellement", style=discord.ButtonStyle.primary)
        self.bot = bot

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            "Indiquez le type de log à configurer (messages, moderation, ticket, vocal, giveaway, securite) puis le salon cible.",
            ephemeral=True
        )
        # Ici, tu peux ajouter un flow étape par étape avec discord.ui.Modal ou une suite de messages

class ConfigView(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=180)
        self.bot = bot
        self.add_item(SecurityButton(bot))
        self.add_item(LogsButton(bot))
        self.add_item(CloseButton())

class SecurityButton(discord.ui.Button):
    def __init__(self, bot):
        super().__init__(label="Cyber-sécurité", style=discord.ButtonStyle.primary)
        self.bot = bot

    async def callback(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="🛡️ Configuration de la Sécurité",
            description="Activez/désactivez les protections",
            color=discord.Color.red()
        )
        await interaction.response.edit_message(embed=embed, view=SecurityView(self.bot))

class LogsButton(discord.ui.Button):
    def __init__(self, bot):
        super().__init__(label="Logs", style=discord.ButtonStyle.secondary)
        self.bot = bot

    async def callback(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="📋 Configuration des Logs",
            description="Choisissez la méthode de configuration des logs.",
            color=discord.Color.blue()
        )
        await interaction.response.edit_message(embed=embed, view=LogsSetupView(self.bot))

class ConfigCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="config", description="Configure le bot")
    @app_commands.checks.has_permissions(administrator=True)
    async def config(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="⚙️ Configuration de Seiko",
            description="Choisissez une catégorie à configurer",
            color=discord.Color.blurple()
        )
        await interaction.response.send_message(
            embed=embed,
            view=ConfigView(self.bot),
            ephemeral=True
        )

async def setup(bot):
    await bot.add_cog(ConfigCog(bot))

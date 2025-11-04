import discord
from discord.ext import commands
from discord import app_commands
import core_config as config

class DraftBotView(discord.ui.View):
    """Vue de base avec style DraftBot"""
    def __init__(self):
        super().__init__(timeout=None)
    
    async def on_timeout(self):
        for item in self.children:
            item.disabled = True

class ConfigMainView(DraftBotView):
    def __init__(self, bot):
        super().__init__()
        self.bot = bot
        # Ajout des boutons principaux
        self.add_item(SecurityButton(bot))
        self.add_item(LogsButton(bot))

class SecurityView(DraftBotView):
    def __init__(self, bot):
        super().__init__()
        # Ajout des toggles de sécurité
        self.add_item(SecurityToggle("Anti-spam", "anti_spam", bot))
        self.add_item(SecurityToggle("Anti-hack", "anti_hack", bot))
        self.add_item(SecurityToggle("Anti-raid", "anti_raid", bot))
        self.add_item(BackButton("Menu principal"))

class SecurityToggle(discord.ui.Button):
    def __init__(self, label, key, bot):
        super().__init__(style=discord.ButtonStyle.secondary, label=label)
        self.key = key
        self.bot = bot
        self.update_style()
    
    def update_style(self):
        enabled = config.CONFIG.get("security", {}).get(self.key, False)
        self.style = discord.ButtonStyle.success if enabled else discord.ButtonStyle.danger
        self.label = f"{self.label.split(' ')[0]} {'✅' if enabled else '❌'}"

    async def callback(self, interaction: discord.Interaction):
        config.CONFIG.setdefault("security", {})[self.key] = not config.CONFIG["security"].get(self.key, False)
        self.update_style()
        await interaction.response.edit_message(view=self.view)

class CloseButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Fermer", style=discord.ButtonStyle.secondary)

    async def callback(self, interaction: discord.Interaction):
        await interaction.message.delete()

class LogsSetupView(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot
        self.add_item(CreateLogsButton(bot))
        self.add_item(ManualLogsButton(bot))
        self.add_item(CloseButton())

class CreateLogsButton(discord.ui.Button):
    def __init__(self, bot):
        super().__init__(label="Créer", style=discord.ButtonStyle.success)
        self.bot = bot

    async def callback(self, interaction: discord.Interaction):
        try:
            from log_setup import LOG_CATEGORIES
            guild = interaction.guild
            created = []
            for cat_name, channels in LOG_CATEGORIES.items():
                category = discord.utils.get(guild.categories, name=cat_name)
                if not category:
                    category = await guild.create_category(cat_name)
                for ch_name in channels:
                    channel = discord.utils.get(guild.text_channels, name=ch_name)
                    if not channel:
                        ch = await guild.create_text_channel(ch_name, category=category)
                        created.append(f"{cat_name}/{ch_name}")
            await interaction.response.send_message(
                f"✅ Catégories et salons créés :\n" + "\n".join(created) if created else "Tout existe déjà.",
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
        # À compléter : flow étape par étape avec Modal ou messages

class ConfigView(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot

    @discord.ui.button(label="Créer", style=discord.ButtonStyle.green, custom_id="config:create")
    async def create_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        log_setup = self.bot.get_cog("LogSetupCog")
        if log_setup:
            await log_setup._create_category(interaction)
        else:
            await interaction.response.send_message("❌ Système de logs non disponible", ephemeral=True)

class ConfigCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="config", description="Configure le bot")
    @app_commands.checks.has_permissions(administrator=True)
    async def config(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="⚙️ Configuration de Seiko",
            description="Configurez les différents aspects du bot",
            color=discord.Color.blurple()
        )
        await interaction.response.send_message(
            embed=embed,
            view=ConfigMainView(self.bot),
            ephemeral=False
        )

class LoggingCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def get_voice_action_author(self, guild, target_id, max_age_seconds=15):
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
        except:
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

async def setup(bot):
    await bot.add_cog(ConfigCog(bot))
    # Enregistrer la view pour que les boutons persistent
    bot.add_view(ConfigView(bot))
    bot.add_cog(LoggingCog(bot))

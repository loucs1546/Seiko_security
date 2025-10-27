# cogs/config.py
import discord
from discord.ext import commands
import core_config as config

class ConfigCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.app_commands.command(name="config", description="Configure le bot")
    async def config(self, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ Réservé aux administrateurs.", ephemeral=True)
            return

        view = ConfigMainView(self.bot)
        await interaction.response.send_message("🔧 **Configuration du bot**", view=view, ephemeral=True)

class ConfigMainView(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=300)
        self.bot = bot

    @discord.ui.button(label="Sécurité", style=discord.ButtonStyle.primary)
    async def security_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(content="🛡️ **Sécurité**", view=ConfigSecurityView(self.bot))

    @discord.ui.button(label="Logs", style=discord.ButtonStyle.secondary)
    async def logs_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(content="📜 **Logs**", view=ConfigLogsView(self.bot))

class ConfigSecurityView(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=300)
        self.bot = bot

    @discord.ui.button(label="Anti-Spam", style=discord.ButtonStyle.gray)
    async def anti_spam_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        current = config.CONFIG["security"]["anti_spam"]
        config.CONFIG["security"]["anti_spam"] = not current
        button.style = discord.ButtonStyle.green if not current else discord.ButtonStyle.gray
        button.label = "Anti-Spam ✅" if not current else "Anti-Spam"
        await interaction.response.edit_message(view=self)

    @discord.ui.button(label="Anti-Hack", style=discord.ButtonStyle.gray)
    async def anti_hack_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        current = config.CONFIG["security"]["anti_hack"]
        config.CONFIG["security"]["anti_hack"] = not current
        button.style = discord.ButtonStyle.green if not current else discord.ButtonStyle.gray
        button.label = "Anti-Hack ✅" if not current else "Anti-Hack"
        await interaction.response.edit_message(view=self)

    @discord.ui.button(label="Anti-Raid", style=discord.ButtonStyle.gray)
    async def anti_raid_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        current = config.CONFIG["security"]["anti_raid"]
        config.CONFIG["security"]["anti_raid"] = not current
        button.style = discord.ButtonStyle.green if not current else discord.ButtonStyle.gray
        button.label = "Anti-Raid ✅" if not current else "Anti-Raid"
        await interaction.response.edit_message(view=self)

    @discord.ui.button(label="Retour", style=discord.ButtonStyle.danger)
    async def back_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(content="🔧 **Configuration du bot**", view=ConfigMainView(self.bot))

class ConfigLogsView(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=300)
        self.bot = bot

    @discord.ui.button(label="Créer les salons", style=discord.ButtonStyle.success)
    async def create_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        for category in guild.categories:
            if "log" in category.name.lower() or "surveillance" in category.name.lower():
                await interaction.response.send_message(
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

            mapping = [
                ("📜・messages", "messages"),
                ("🎤・vocal", "vocal"),
                ("🛠️・commandes", "commands"),
                ("👑・rôles", "roles"),
                ("📛・profil", "profile"),
                ("🔍・contenu", "content"),
                ("⚖️・sanctions", "sanctions")
            ]

            for name, key in mapping:
                ch = await guild.create_text_channel(name=name, category=category)
                config.CONFIG["logs"][key] = ch.id

            await interaction.response.send_message(
                f"✅ Catégorie **{category.name}** créée avec {len(mapping)} salons !",
                ephemeral=True
            )
        except Exception as e:
            await interaction.response.send_message(f"❌ Erreur : {str(e)}", ephemeral=True)

    @discord.ui.button(label="Définir manuellement", style=discord.ButtonStyle.secondary)
    async def define_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Obtenir la liste des salons textuels
        text_channels = [ch for ch in interaction.guild.text_channels if isinstance(ch, discord.TextChannel)]
        if not text_channels:
            await interaction.response.send_message("❌ Aucun salon texte trouvé.", ephemeral=True)
            return

        options = []
        for ch in text_channels[:25]:  # Discord limite à 25 options
            options.append(discord.SelectOption(label=ch.name, value=str(ch.id)))

        select = discord.ui.Select(
            placeholder="Choisissez un salon pour les logs de messages...",
            options=options,
            custom_id="log_messages"
        )
        select.callback = self.make_callback("messages")

        view = discord.ui.View(timeout=300)
        view.add_item(select)
        await interaction.response.send_message(
            "📝 **Étape 1/7** : Sélectionnez le salon pour les **messages** :",
            view=view,
            ephemeral=True
        )

    def make_callback(self, log_type):
        async def callback(interaction: discord.Interaction):
            channel_id = int(interaction.data["values"][0])
            config.CONFIG["logs"][log_type] = channel_id
            channel = interaction.guild.get_channel(channel_id)

            # Passer à l'étape suivante
            next_steps = {
                "messages": ("vocal", "vocal"),
                "vocal": ("commandes", "commands"),
                "commands": ("rôles", "roles"),
                "roles": ("profil", "profile"),
                "profile": ("contenu", "content"),
                "content": ("sanctions", "sanctions"),
                "sanctions": None
            }

            if next_steps[log_type] is None:
                await interaction.response.edit_message(content="✅ Tous les salons de logs ont été définis !", view=None)
                return

            next_label, next_key = next_steps[log_type]
            text_channels = [ch for ch in interaction.guild.text_channels if isinstance(ch, discord.TextChannel)]
            options = [discord.SelectOption(label=ch.name, value=str(ch.id)) for ch in text_channels[:25]]

            select = discord.ui.Select(
                placeholder=f"Choisissez un salon pour les logs de {next_label}...",
                options=options
            )
            select.callback = self.make_callback(next_key)

            view = discord.ui.View(timeout=300)
            view.add_item(select)
            await interaction.response.edit_message(
                content=f"📝 **Étape suivante** : Sélectionnez le salon pour les **{next_label}** :",
                view=view
            )

        return callback

async def setup(bot):
    await bot.add_cog(ConfigCog(bot))
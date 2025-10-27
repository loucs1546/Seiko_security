# cogs/config.py
import discord
from discord.ext import commands
import core_config as config

class ConfigCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.app_commands.command(name="config", description="Interface de configuration avancée")
    async def config(self, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ Réservé aux administrateurs.", ephemeral=True)
            return

        embed = self.get_security_embed()
        view = SecurityConfigView(self.bot)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    def get_security_embed(self):
        anti_spam = config.CONFIG["security"]["anti_spam"]
        anti_raid = config.CONFIG["security"]["anti_raid"]
        anti_hack = config.CONFIG["security"]["anti_hack"]

        status = {True: "✅ **Activé**", False: "❌ **Désactivé**"}

        embed = discord.Embed(
            title="🛡️ Configuration de la Sécurité",
            description="Cliquez sur les boutons pour basculer l'état.",
            color=0x2ecc71,
            timestamp=discord.utils.utcnow()
        )
        embed.add_field(name="🤖 Anti-Spam", value=status[anti_spam], inline=False)
        embed.add_field(name="👥 Anti-Raid", value=status[anti_raid], inline=False)
        embed.add_field(name="🕵️ Anti-Hack", value=status[anti_hack], inline=False)
        embed.set_footer(text="CyberWatch • Sécurité en temps réel")
        return embed

class SecurityConfigView(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=600)
        self.bot = bot

    async def toggle_and_run(self, interaction: discord.Interaction, setting: str, command_name: str):
        current = config.CONFIG["security"][setting]
        new_value = not current
        config.CONFIG["security"][setting] = new_value

        # Appeler la commande réelle
        cog = self.bot.get_cog("ModerationCommandsCog")
        if cog:
            cmd = getattr(cog, command_name, None)
            if cmd:
                # Créer une fausse interaction avec le booléen
                class FakeInteraction:
                    def __init__(self, orig, val):
                        self._orig = orig
                        self.value = val
                    def __getattr__(self, name):
                        return getattr(self._orig, name)
                    async def response(self):
                        return self
                    async def send_message(self, *args, **kwargs):
                        pass
                    async def defer(self, **kwargs):
                        pass

                fake = FakeInteraction(interaction, new_value)
                await cmd(fake)

        # Mettre à jour l'embed
        embed = ConfigCog(self.bot).get_security_embed()
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="Anti-Spam", emoji="🤖", style=discord.ButtonStyle.secondary)
    async def anti_spam_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.toggle_and_run(interaction, "anti_spam", "anti_spam")

    @discord.ui.button(label="Anti-Raid", emoji="👥", style=discord.ButtonStyle.secondary)
    async def anti_raid_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.toggle_and_run(interaction, "anti_raid", "anti_raid")

    @discord.ui.button(label="Anti-Hack", emoji="🕵️", style=discord.ButtonStyle.secondary)
    async def anti_hack_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.toggle_and_run(interaction, "anti_hack", "anti_hack")

async def setup(bot):
    await bot.add_cog(ConfigCog(bot))
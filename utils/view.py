# utils/views.py
import discord
from discord.ui import View, Button

class ContentReviewView(View):
    def __init__(self, message_content: str, author: discord.Member, original_channel: discord.TextChannel):
        super().__init__(timeout=600)
        self.message_content = message_content
        self.author = author
        self.original_channel = original_channel

    @discord.ui.button(label="✅ Valider", style=discord.ButtonStyle.green)
    async def accept(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.original_channel.send(f"{self.author.mention} (message validé par modérateur)\n{self.message_content}")
        await interaction.response.edit_message(content="✅ Message restauré.", view=None)

    @discord.ui.button(label="❌ Refuser", style=discord.ButtonStyle.red)
    async def reject(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(content="❌ Message supprimé définitivement.", view=None)


class BavureReviewView(View):
    def __init__(self, mod_author: discord.Member, target: discord.Member, command_name: str, reason: str, original_interaction: discord.Interaction):
        super().__init__(timeout=600)
        self.mod_author = mod_author
        self.target = target
        self.command_name = command_name
        self.reason = reason
        self.original_interaction = original_interaction

    @discord.ui.button(label="✅ Accepter", style=discord.ButtonStyle.green)
    async def accept(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Log dans bavures-sanctions
        log_embed = discord.Embed(
            title="✅ Bavure acceptée",
            description=f"**Modérateur** : {self.mod_author.mention}\n**Cible** : {self.target.mention}\n**Commande** : `/{self.command_name}`\n**Raison** : {self.reason}",
            color=0x2ecc71,
            timestamp=discord.utils.utcnow()
        )
        from utils.logging import send_log_to
        await send_log_to(self.original_interaction.client, "bavures-sanctions", log_embed)

        # Exécuter la sanction
        bot = self.original_interaction.client
        if self.command_name == "warn":
            embed = discord.Embed(
                title="⚠️ Avertissement",
                description=f"**Membre** : {self.target.mention}\n**Modérateur** : {self.mod_author.mention}\n**Raison** : {self.reason}",
                color=0xffff00,
                timestamp=discord.utils.utcnow()
            )
            ch = bot.get_channel(bot.config.CONFIG["logs"].get("sanctions"))
            if ch: await ch.send(embed=embed)
            await self.original_interaction.followup.send(f"✅ Avertissement envoyé à {self.target.mention}.", ephemeral=True)

        elif self.command_name == "kick":
            try:
                await self.target.send(f"⚠️ Vous avez été expulsé pour : **{self.reason}**.")
            except:
                pass
            await self.target.kick(reason=self.reason)
            await self.original_interaction.followup.send(f"✅ {self.target.mention} expulsé.", ephemeral=True)

        elif self.command_name == "ban":
            try:
                await self.target.send(f"⚠️ Vous avez été banni pour : **{self.reason}**.")
            except:
                pass
            await self.target.ban(reason=self.reason)
            await self.original_interaction.followup.send(f"✅ {self.target.mention} banni.", ephemeral=True)

        await interaction.response.edit_message(content="✅ Sanction appliquée.", view=None)

    @discord.ui.button(label="❌ Refuser", style=discord.ButtonStyle.red)
    async def reject(self, interaction: discord.Interaction, button: discord.ui.Button):
        log_embed = discord.Embed(
            title="❌ Bavure refusée",
            description=f"**Modérateur** : {self.mod_author.mention}\n**Cible** : {self.target.mention}\n**Commande** : `/{self.command_name}`\n**Raison** : {self.reason}",
            color=0xff6600,
            timestamp=discord.utils.utcnow()
        )
        from utils.logging import send_log_to
        await send_log_to(self.original_interaction.client, "bavures-sanctions", log_embed)
        await interaction.response.edit_message(content="❌ Sanction annulée.", view=None)
# utils/views.py
import discord

class ContentReviewView(discord.ui.View):
    def __init__(self, message_content: str, author: discord.Member, original_channel: discord.TextChannel):
        super().__init__(timeout=600)
        self.message_content = message_content
        self.author = author
        self.original_channel = original_channel

    @discord.ui.button(label="✅ Valider", style=discord.ButtonStyle.green)
    async def accept(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.original_channel.send(f"{self.author.mention} (message validé)\n{self.message_content}")
        await interaction.response.edit_message(content="✅ Message restauré.", view=None)

    @discord.ui.button(label="❌ Refuser", style=discord.ButtonStyle.red)
    async def reject(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(content="❌ Message supprimé définitivement.", view=None)


class BavureReviewView(discord.ui.View):
    def __init__(self, mod_author: discord.Member, target: discord.Member, command_name: str, reason: str, original_interaction: discord.Interaction):
        super().__init__(timeout=600)
        self.mod_author = mod_author
        self.target = target
        self.command_name = command_name
        self.reason = reason
        self.original_interaction = original_interaction

    @discord.ui.button(label="✅ Accepter", style=discord.ButtonStyle.green)
    async def accept(self, interaction: discord.Interaction, button: discord.ui.Button):
        bot = self.original_interaction.client
        from utils.logging import send_log_to
        log_embed = discord.Embed(
            title="✅ Bavure acceptée",
            description=f"**Modérateur** : {self.mod_author.mention}\n**Cible** : {self.target.mention}\n**Commande** : `/{self.command_name}`\n**Raison** : {self.reason}",
            color=0x2ecc71,
            timestamp=discord.utils.utcnow()
        )
        await send_log_to(bot, "bavures-sanctions", log_embed)
        await self.original_interaction.followup.send(f"✅ Sanction appliquée.", ephemeral=True)
        await interaction.response.edit_message(content="✅ Sanction appliquée.", view=None)

    @discord.ui.button(label="❌ Refuser", style=discord.ButtonStyle.red)
    async def reject(self, interaction: discord.Interaction, button: discord.ui.Button):
        bot = self.original_interaction.client
        from utils.logging import send_log_to
        log_embed = discord.Embed(
            title="❌ Bavure refusée",
            description=f"**Modérateur** : {self.mod_author.mention}\n**Cible** : {self.target.mention}\n**Commande** : `/{self.command_name}`\n**Raison** : {self.reason}",
            color=0xff6600,
            timestamp=discord.utils.utcnow()
        )
        await send_log_to(bot, "bavures-sanctions", log_embed)
        await interaction.response.edit_message(content="❌ Sanction annulée.", view=None)
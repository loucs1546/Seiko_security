# main.py
import discord
from discord.ext import commands
import core_config as config
import asyncio
import inspect

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ {bot.user} est en ligne !")
    
    # Charger les cogs
    cog_paths = [
        "cogs.logging",
        "cogs.log_setup",  # Assure-toi que c'est bien ce chemin
        "cogs.security.antiraid",
        "cogs.security.antispam",
        "cogs.security.content_filter",
        "cogs.security.link_filter",
        "cogs.moderation_commands",
        "cogs.tickets",
        "cogs.config"
    ]
    
    for cog in cog_paths:
        try:
            res = bot.load_extension(cog)
            if inspect.isawaitable(res):
                await res
            print(f"✅ Cog chargé : {cog}")
        except Exception as e:
            print(f"❌ Erreur : {e}")

    await asyncio.sleep(2)

    # 🔁 SYNCHRONISATION POUR TON SERVEUR (instantané)
    try:
        if config.GUILD_ID:
            guild = discord.Object(id=config.GUILD_ID)
            # Force sync toutes les commandes
            bot.tree.copy_global_to(guild=guild)
            synced = await bot.tree.sync(guild=guild)
            print(f"✅ {len(synced)} commandes synchronisées pour le serveur: {[c.name for c in synced]}")
        else:
            synced = await bot.tree.sync()
            print(f"✅ {len(synced)} commandes synchronisées globalement: {[c.name for c in synced]}")
    except Exception as e:
        print(f"❌ Erreur de synchronisation: {e}")

@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: discord.app_commands.AppCommandError):
    # Evite l'exception si l'interaction a déjà reçu une réponse
    try:
        already_responded = interaction.response.is_done()
    except Exception:
        already_responded = False

    async def safe_send(content=None, embed=None, ephemeral=True):
        try:
            if not already_responded:
                await interaction.response.send_message(content=content, embed=embed, ephemeral=ephemeral)
            else:
                await interaction.followup.send(content=content, embed=embed, ephemeral=ephemeral)
        except Exception:
            # dernier recours — log dans la console
            print(f"Erreur d'envoi d'erreur: {error}")

    if isinstance(error, discord.app_commands.CommandNotFound):
        await safe_send("❌ Cette commande n'existe pas.", ephemeral=True)
    elif isinstance(error, discord.app_commands.MissingPermissions):
        await safe_send("❌ Permissions insuffisantes.", ephemeral=True)
    else:
        await safe_send(f"❌ Une erreur est survenue: {error}", ephemeral=True)

# === COMMANDES SLASH (comme /ping, /kick, etc.) ===

@bot.tree.command(name="logs", description="Définit le salon pour un type de log")
@discord.app_commands.describe(type="Type de log", salon="Salon de destination")
@discord.app_commands.choices(type=[
    discord.app_commands.Choice(name="messages", value="messages"),
    discord.app_commands.Choice(name="moderation", value="moderation"),
    discord.app_commands.Choice(name="ticket", value="ticket"),
    discord.app_commands.Choice(name="vocal", value="vocal"),
    discord.app_commands.Choice(name="securite", value="securite")
])
@discord.app_commands.checks.has_permissions(administrator=True)
async def logs(interaction: discord.Interaction, type: str, salon: discord.TextChannel):
    # Assure l'existence de la clé logs dans la config
    if not isinstance(config.CONFIG, dict):
        config.CONFIG = {}
    config.CONFIG.setdefault("logs", {})
    config.CONFIG["logs"][type] = salon.id

    # Embed récapitulatif pour meilleure visibilité UI
    embed = discord.Embed(
        title="📌 Configuration des logs",
        description=f"Le type **{type}** sera maintenant envoyé dans {salon.mention}.",
        color=0x2f3136,
        timestamp=discord.utils.utcnow()
    )
    embed.set_footer(text="Utilisez /logs pour modifier d'autres salons.")
    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="scan-deleted", description="Récupère les suppressions récentes manquées")
@discord.app_commands.checks.has_permissions(administrator=True)
async def scan_deleted(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    count = 0
    async for entry in interaction.guild.audit_logs(action=discord.AuditLogAction.message_delete, limit=50):
        if (discord.utils.utcnow() - entry.created_at).total_seconds() > 300:
            break
        embed = discord.Embed(
            title="🗑️ Message supprimé (récupéré)",
            description=f"**Auteur** : {entry.target}\n**Supprimé par** : {entry.user}",
            color=0xff8800,
            timestamp=entry.created_at
        )
        from utils.logging import send_log_to
        await send_log_to(bot, "messages", embed)
        count += 1
    await interaction.followup.send(f"✅ {count} suppressions récupérées.", ephemeral=True)

bot.run(config.DISCORD_TOKEN)
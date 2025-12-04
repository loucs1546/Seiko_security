# main.py
import discord
from discord.ext import commands
import core_config as config
import asyncio
import inspect
from flask import Flask
from threading import Thread

# === MINI SERVEUR WEB POUR RENDRE/KEEP ALIVE ===
app = Flask("")

@app.route("/")
def home():
    return "Bot en ligne ✅"

def run():
    app.run(host="0.0.0.0", port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

keep_alive()  # démarre le serveur en parallèle

# === CONFIGURATION DU BOT DISCORD ===
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ {bot.user} est en ligne !")
    
    cog_paths = [
        "cogs.logging",
        "cogs.log_setup",
        "cogs.security.antiraid",
        "cogs.security.antispam",
        "cogs.security.content_filter",
        "cogs.security.link_filter",
        "cogs.moderation_commands",
        "cogs.tickets",
        "cogs.config",
        "cogs.ticketv2"
        
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

    try:
        if config.GUILD_ID:
            guild = discord.Object(id=config.GUILD_ID)
            bot.tree.copy_global_to(guild=guild)
            synced = await bot.tree.sync(guild=guild)
            print(f"✅ {len(synced)} commandes : {[c.name for c in synced]}")
        else:
            synced = await bot.tree.sync()
            print(f"✅ {len(synced)} commandes globales")
    except Exception as e:
        print(f"❌ Erreur : {e}")

# === COMMANDES PRINCIPALES ===

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
    config.CONFIG.setdefault("logs", {})[type] = salon.id
    embed = discord.Embed(
        title="📌 Configuration des logs",
        description=f"Le type **{type}** sera envoyé dans {salon.mention}.",
        color=0x2f3136,
        timestamp=discord.utils.utcnow()
    )
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

@bot.tree.command(name="logs-messages", description="Configure le salon pour les logs de messages")
@discord.app_commands.describe(salon="Salon de destination pour les logs")
@discord.app_commands.checks.has_permissions(administrator=True)
async def logs_messages(interaction: discord.Interaction, salon: discord.TextChannel):
    if not isinstance(config.CONFIG, dict):
        config.CONFIG = {}
    config.CONFIG.setdefault("logs", {})
    config.CONFIG["logs"]["messages"] = salon.id
    
    embed = discord.Embed(
        title="📌 Configuration - Logs Messages",
        description=f"Les logs de messages seront envoyés dans {salon.mention}",
        color=0x00ff00,
        timestamp=discord.utils.utcnow()
    )
    embed.add_field(name="Type", value="Messages envoyés, modifiés, supprimés", inline=False)
    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="logs-moderation", description="Configure le salon pour les logs de modération")
@discord.app_commands.describe(salon="Salon de destination pour les logs")
@discord.app_commands.checks.has_permissions(administrator=True)
async def logs_moderation(interaction: discord.Interaction, salon: discord.TextChannel):
    if not isinstance(config.CONFIG, dict):
        config.CONFIG = {}
    config.CONFIG.setdefault("logs", {})
    config.CONFIG["logs"]["moderation"] = salon.id
    
    embed = discord.Embed(
        title="📌 Configuration - Logs Modération",
        description=f"Les logs de modération seront envoyés dans {salon.mention}",
        color=0xff9900,
        timestamp=discord.utils.utcnow()
    )
    embed.add_field(name="Type", value="Création/suppression/modification de salons, rôles, pseudos, bans, kicks, mutes", inline=False)
    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="logs-vocal", description="Configure le salon pour les logs vocaux")
@discord.app_commands.describe(salon="Salon de destination pour les logs")
@discord.app_commands.checks.has_permissions(administrator=True)
async def logs_vocal(interaction: discord.Interaction, salon: discord.TextChannel):
    if not isinstance(config.CONFIG, dict):
        config.CONFIG = {}
    config.CONFIG.setdefault("logs", {})
    config.CONFIG["logs"]["vocal"] = salon.id
    
    embed = discord.Embed(
        title="📌 Configuration - Logs Vocaux",
        description=f"Les logs vocaux seront envoyés dans {salon.mention}",
        color=0x0099ff,
        timestamp=discord.utils.utcnow()
    )
    embed.add_field(name="Type", value="Connexions et déconnexions vocales", inline=False)
    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="logs-ticket", description="Configure le salon pour les logs de tickets")
@discord.app_commands.describe(salon="Salon de destination pour les logs")
@discord.app_commands.checks.has_permissions(administrator=True)
async def logs_ticket(interaction: discord.Interaction, salon: discord.TextChannel):
    if not isinstance(config.CONFIG, dict):
        config.CONFIG = {}
    config.CONFIG.setdefault("logs", {})
    config.CONFIG["logs"]["ticket"] = salon.id
    
    embed = discord.Embed(
        title="📌 Configuration - Logs Tickets",
        description=f"Les logs de tickets seront envoyés dans {salon.mention}",
        color=0x9900ff,
        timestamp=discord.utils.utcnow()
    )
    embed.add_field(name="Type", value="Création, fermeture, prise en charge de tickets", inline=False)
    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="logs-giveaway", description="Configure le salon pour les logs de giveaways")
@discord.app_commands.describe(salon="Salon de destination pour les logs")
@discord.app_commands.checks.has_permissions(administrator=True)
async def logs_giveaway(interaction: discord.Interaction, salon: discord.TextChannel):
    if not isinstance(config.CONFIG, dict):
        config.CONFIG = {}
    config.CONFIG.setdefault("logs", {})
    config.CONFIG["logs"]["giveaway"] = salon.id
    
    embed = discord.Embed(
        title="📌 Configuration - Logs Giveaways",
        description=f"Les logs de giveaways seront envoyés dans {salon.mention}",
        color=0xffff00,
        timestamp=discord.utils.utcnow()
    )
    embed.add_field(name="Type", value="Création, fin, gagnants des giveaways", inline=False)
    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="logs-securite", description="Configure le salon pour les logs de sécurité")
@discord.app_commands.describe(salon="Salon de destination pour les logs")
@discord.app_commands.checks.has_permissions(administrator=True)
async def logs_securite(interaction: discord.Interaction, salon: discord.TextChannel):
    if not isinstance(config.CONFIG, dict):
        config.CONFIG = {}
    config.CONFIG.setdefault("logs", {})
    config.CONFIG["logs"]["securite"] = salon.id
    
    embed = discord.Embed(
        title="📌 Configuration - Logs Sécurité",
        description=f"Les logs de sécurité seront envoyés dans {salon.mention}",
        color=0xff0000,
        timestamp=discord.utils.utcnow()
    )
    embed.add_field(name="Type", value="Tentatives suspectes, contenu suspect, alertes de sécurité", inline=False)
    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.event
async def on_ready():
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} commands.")
    except Exception as e:
        print(f"Error syncing commands: {e}")


bot.run(config.DISCORD_TOKEN)
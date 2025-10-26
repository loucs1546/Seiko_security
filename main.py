# main.py
import discord
from discord.ext import commands
import core_config as config
import asyncio

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ {bot.user} est en ligne !")
    
    # Liste des cogs
    cog_paths = [
        "cogs.logging",
        "cogs.security.antiraid",
        "cogs.security.antispam",
        "cogs.security.content_filter",
        "cogs.security.link_filter",
        "cogs.moderation",
        "cogs.moderation_commands",
        "cogs.tickets",
        "cogs.log_setup"
    ]
    
    # Charger TOUS les cogs
    for cog in cog_paths:
        try:
            await bot.load_extension(cog)
            print(f"✅ Cog chargé : {cog}")
        except Exception as e:
            print(f"❌ Erreur au chargement de {cog} : {e}")

    # ⏳ Attendre 1 seconde pour s'assurer que les commandes sont enregistrées
    await asyncio.sleep(1)

    # 🔁 Synchroniser APRÈS le chargement complet
    try:
        guild = discord.Object(id=config.GUILD_ID)
        synced = await bot.tree.sync(guild=guild)
        print(f"✅ {len(synced)} commandes synchronisées : {[c.name for c in synced]}")
    except Exception as e:
        print(f"❌ Erreur de synchronisation : {e}")

# NE PAS ajouter de commandes ici (ex: @bot.tree.command)

bot.run(config.DISCORD_TOKEN)
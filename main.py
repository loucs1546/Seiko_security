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
    
    for cog in cog_paths:
        try:
            await bot.load_extension(cog)
            print(f"✅ Cog chargé : {cog}")
        except Exception as e:
            print(f"❌ Erreur : {e}")

    # ⏳ Attends 2 secondes
    await asyncio.sleep(2)

    # 🔁 SYNCHRONISATION GLOBALE (temporaire)
    try:
        synced = await bot.tree.sync()  # ← Pas de `guild=...`
        print(f"✅ {len(synced)} commandes globales synchronisées : {[c.name for c in synced]}")
    except Exception as e:
        print(f"❌ Erreur : {e}")

bot.run(config.DISCORD_TOKEN)
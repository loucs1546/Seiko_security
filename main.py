# main.py
import discord
from discord.ext import commands
import core_config as config
import asyncio

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

async def load_all_cogs():
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
            print(f"❌ Erreur au chargement de {cog} : {e}")

@bot.event
async def on_ready():
    print(f"✅ {bot.user} est en ligne !")
    await load_all_cogs()
    await asyncio.sleep(2)  # Délai critique

    try:
        guild = discord.Object(id=config.GUILD_ID)
        bot.tree.clear_commands(guild=guild)  # Reset
        synced = await bot.tree.sync(guild=guild)
        print(f"✅ {len(synced)} commandes synchronisées : {[c.name for c in synced]}")
    except Exception as e:
        print(f"❌ Erreur de synchronisation : {e}")

bot.run(config.DISCORD_TOKEN)
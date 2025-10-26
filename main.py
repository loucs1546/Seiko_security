# main.py
import discord
from discord.ext import commands
import core_config as config

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
        "cogs.moderation_commands",  # ← Nouveau
        "cogs.tickets",
        "cogs.log_setup"
    ]
    
    for cog in cog_paths:
        try:
            await bot.load_extension(cog)
            print(f"✅ Cog chargé : {cog}")
        except Exception as e:
            print(f"❌ Erreur au chargement de {cog} : {e}")

    # Synchronisation des commandes slash
    guild = discord.Object(id=config.GUILD_ID)
    try:
        synced = await bot.tree.sync(guild=guild)
        print(f"🔁 {len(synced)} commandes synchronisées : {[c.name for c in synced]}")
    except Exception as e:
        print(f"❌ Erreur de synchronisation : {e}")

# === COMMANDE PING ===
@bot.tree.command(name="ping", description="Vérifie si le bot est en ligne")
async def ping(interaction: discord.Interaction):
    latency = round(bot.latency * 1000)
    await interaction.response.send_message(f"🏓 Pong ! Latence : **{latency} ms**", ephemeral=True)

bot.run(config.DISCORD_TOKEN)
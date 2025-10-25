import discord
from discord.ext import commands
import config

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
        "cogs.security.link_filter",
        "cogs.moderation",
        "cogs.tickets",
        "cogs.log_setup"
    ]

    for cog in cog_paths:
        try:
            await bot.load_extension(cog)
            print(f"✅ Cog chargé : {cog}")
        except Exception as e:
            print(f"❌ Erreur au chargement de {cog} : {e}")

    guild = discord.Object(id=config.GUILD_ID)
    await bot.tree.sync(guild=guild)
    print("🔁 Commandes slash synchronisées.")

bot.run(config.DISCORD_TOKEN)
import discord
import core_config as config
async def send_log(bot, channel_key: str, embed: discord.Embed):
    channel_id = config.LOG_CHANNELS.get(channel_key)
    if not channel_id:
        return
    channel = bot.get_channel(channel_id)
    if channel:
        try:
            await channel.send(embed=embed)
        except Exception:
            pass  # Échec silencieux si salon supprimé
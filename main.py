# main.py - VERSION CONSOLIDÉE AVEC TOUTES LES COMMANDES
import discord
from discord.ext import commands
import core_config as config
import asyncio
from flask import Flask
from threading import Thread
from datetime import datetime
import re
import io
from utils.logging import send_log_to

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

keep_alive()

# === CONFIGURATION DU BOT DISCORD ===
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)
cogs_loaded = False

# === HELPERS ===
def est_bavure_raison(raison: str) -> bool:
    if not raison or raison.strip().lower() in ("", "aucune raison"):
        return True
    mots = re.findall(r'\b[a-zA-Z]{2,}\b', raison)
    if len(mots) < 2:
        return True
    voyelles = "aeiouy"
    valid_count = 0
    for mot in mots:
        if any(c.lower() in voyelles for c in mot):
            valid_count += 1
            if valid_count >= 2:
                return False
    return True

def get_sanction_channel(bot):
    return bot.get_channel(config.CONFIG["logs"].get("sanctions"))

# === VIEWS POUR TICKETS ===
class TicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="📩 Créer un ticket", style=discord.ButtonStyle.success, custom_id="create_ticket")
    async def create_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        user = interaction.user

        for channel in guild.channels:
            if channel.name == f"ticket-{user.id}":
                await interaction.response.send_message(
                    "Vous avez déjà un ticket ouvert !", ephemeral=True
                )
                return

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            user: discord.PermissionOverwrite(read_messages=True, send_messages=True, attach_files=True, embed_links=True),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True, manage_channels=True),
        }

        ticket_channel = await guild.create_text_channel(
            name=f"ticket-{user.id}",
            overwrites=overwrites,
            reason=f"Ticket créé par {user} ({user.id})"
        )

        embed = discord.Embed(
            title="📬 Nouveau ticket",
            description=f"Bonjour {user.mention},\n\nUn membre de l'équipe vous répondra bientôt.\n\nCliquez sur **Prendre en charge** si vous êtes staff.",
            color=0x5865F2,
            timestamp=datetime.utcnow()
        )
        embed.set_footer(text="Seiko Security • Système de tickets")
        view = TicketControls(user.id)
        await ticket_channel.send(embed=embed, view=view)

        log_embed = discord.Embed(
            title="🎟️ Ticket créé",
            description=f"**Utilisateur** : {user.mention} (`{user}`)\n**Salon** : {ticket_channel.mention}",
            color=0x00ff00,
            timestamp=datetime.utcnow()
        )
        log_embed.set_thumbnail(url=user.display_avatar.url)
        await send_log_to(bot, "ticket", log_embed)

        await interaction.response.send_message(f"✅ Votre ticket a été créé : {ticket_channel.mention}", ephemeral=True)


class TicketControls(discord.ui.View):
    def __init__(self, owner_id: int):
        super().__init__(timeout=None)
        self.owner_id = owner_id

    @discord.ui.button(label="🔧 Prendre en charge", style=discord.ButtonStyle.primary, custom_id="claim_ticket")
    async def claim_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not any(role.permissions.administrator or role.permissions.manage_messages for role in interaction.user.roles):
            await interaction.response.send_message("❌ Vous n'avez pas la permission de prendre en charge ce ticket.", ephemeral=True)
            return

        button.disabled = True
        button.style = discord.ButtonStyle.secondary
        button.label = "✅ Pris en charge"

        embed = discord.Embed(
            description=f"✅ Ce ticket est maintenant pris en charge par {interaction.user.mention}.",
            color=0x00ff00
        )
        await interaction.channel.send(embed=embed)

        log_embed = discord.Embed(
            title="🔧 Ticket pris en charge",
            description=f"**Staff** : {interaction.user.mention}\n**Ticket** : {interaction.channel.mention}",
            color=0x00aaff,
            timestamp=datetime.utcnow()
        )
        await send_log_to(bot, "ticket", log_embed)

        await interaction.response.edit_message(view=self)

    @discord.ui.button(label="🔒 Fermer", style=discord.ButtonStyle.danger, custom_id="close_ticket")
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.owner_id and not any(role.permissions.administrator for role in interaction.user.roles):
            await interaction.response.send_message("❌ Seul le propriétaire du ticket ou un admin peut le fermer.", ephemeral=True)
            return

        await interaction.response.defer(ephemeral=True)
        
        # === CAPTURE TOUS LES MESSAGES ===
        messages_history = []
        try:
            async for message in interaction.channel.history(limit=None, oldest_first=True):
                msg_data = {
                    "author": str(message.author),
                    "timestamp": message.created_at.strftime("%d/%m/%Y %H:%M:%S"),
                    "content": message.content or "(pas de texte)",
                    "attachments": [att.url for att in message.attachments] if message.attachments else [],
                }
                messages_history.append(msg_data)
        except Exception as e:
            print(f"❌ Erreur lors de la capture des messages : {e}")

        # === RÉSUMÉ ===
        if messages_history:
            log_content = f"📋 **RÉSUMÉ DU TICKET** - {interaction.channel.name}\n"
            log_content += f"**Ouvert par** : {messages_history[0]['author']}\n"
            log_content += f"**Fermé par** : {interaction.user}\n"
            log_content += f"**Date de fermeture** : {datetime.utcnow().strftime('%d/%m/%Y %H:%M:%S')}\n"
            log_content += f"**Nombre de messages** : {len(messages_history)}\n\n"
            log_content += "="*50 + "\n\n"
            
            for msg in messages_history:
                log_content += f"**{msg['author']}** [{msg['timestamp']}]\n"
                log_content += f"{msg['content']}\n"
                if msg['attachments']:
                    log_content += f"📎 *Pièces jointes* : {', '.join(msg['attachments'])}\n"
                log_content += "\n"

            if len(log_content) > 2000:
                log_file = io.BytesIO(log_content.encode('utf-8'))
                file = discord.File(log_file, filename=f"ticket_{interaction.channel.name}.txt")
                
                ticket_logs_channel_id = config.CONFIG.get("logs", {}).get("ticket")
                if ticket_logs_channel_id:
                    ticket_channel = bot.get_channel(ticket_logs_channel_id)
                    if ticket_channel:
                        embed = discord.Embed(
                            title="📋 Logs complets du ticket",
                            description=f"**Ticket** : {interaction.channel.name}\n**Fermé par** : {interaction.user.mention}\n**Messages** : {len(messages_history)}",
                            color=0x2f3136,
                            timestamp=datetime.utcnow()
                        )
                        embed.set_footer(text="Seiko Security • Logs de ticket")
                        await ticket_channel.send(embed=embed, file=file)
            else:
                ticket_logs_channel_id = config.CONFIG.get("logs", {}).get("ticket")
                if ticket_logs_channel_id:
                    ticket_channel = bot.get_channel(ticket_logs_channel_id)
                    if ticket_channel:
                        chunks = [log_content[i:i+2000] for i in range(0, len(log_content), 2000)]
                        for i, chunk in enumerate(chunks):
                            if i == 0:
                                embed = discord.Embed(
                                    title="📋 Logs complets du ticket",
                                    description=chunk,
                                    color=0x2f3136,
                                    timestamp=datetime.utcnow()
                                )
                            else:
                                embed = discord.Embed(
                                    description=chunk,
                                    color=0x2f3136
                                )
                            await ticket_channel.send(embed=embed)

        log_embed = discord.Embed(
            title="🔒 Ticket fermé",
            description=f"**Fermé par** : {interaction.user.mention}\n**Ticket** : `{interaction.channel.name}`\n**Messages** : {len(messages_history)}",
            color=0xff0000,
            timestamp=datetime.utcnow()
        )
        await send_log_to(bot, "ticket", log_embed)

        await interaction.channel.delete(reason=f"Ticket fermé par {interaction.user} ({interaction.user.id})")


# === EVENT: on_ready ===
@bot.event
async def on_ready():
    global cogs_loaded
    print(f"✅ {bot.user} est en ligne !")
    
    if not cogs_loaded:
        # Charger UNIQUEMENT les listeners (pas de commandes ici!)
        cog_paths = [
            "cogs.logging",
            "cogs.security.antiraid",
            "cogs.security.antispam",
            "cogs.security.content_filter",
            "cogs.security.link_filter",
        ]
        
        for cog in cog_paths:
            try:
                await bot.load_extension(cog)
                print(f"✅ Cog (listener) chargé : {cog}")
            except Exception as e:
                print(f"❌ Erreur chargement {cog} : {e}")

        # Attendre que les cogs soient chargés
        await asyncio.sleep(1)

        # SYNCHRONISER LES COMMANDES
        try:
            if config.GUILD_ID:
                guild = discord.Object(id=config.GUILD_ID)
                bot.tree.copy_global_to(guild=guild)
                synced = await bot.tree.sync(guild=guild)
                print(f"✅ {len(synced)} commandes synchronisées !")
                print(f"📝 Commandes : {[c.name for c in synced]}")
            else:
                synced = await bot.tree.sync()
                print(f"✅ {len(synced)} commandes globales synchronisées")
        except Exception as e:
            print(f"❌ Erreur synchronisation : {e}")
        
        cogs_loaded = True
        
        # AJOUTER LES VIEWS PERSISTANTES
        bot.add_view(TicketView())
        bot.add_view(TicketControls(0))
        print("✅ Views ticket enregistrées")



# ============================
# === COMMANDES GÉNÉRALES ===
# ============================

@bot.tree.command(name="ping", description="Affiche la latence du bot")
async def ping(interaction: discord.Interaction):
    latency = round(bot.latency * 1000)
    await interaction.response.send_message(f"🏓 Pong ! Latence : **{latency} ms**", ephemeral=True)


# ============================
# === COMMANDES DE LOGS ===
# ============================

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
async def logs_cmd(interaction: discord.Interaction, type: str, salon: discord.TextChannel):
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
        await send_log_to(bot, "messages", embed)
        count += 1
    await interaction.followup.send(f"✅ {count} suppressions récupérées.", ephemeral=True)

@bot.tree.command(name="add-cat-log", description="Crée une catégorie complète de salons de surveillance")
@discord.app_commands.checks.has_permissions(administrator=True)
async def add_cat_log(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    guild = interaction.guild

    for category in guild.categories:
        if "log" in category.name.lower() or "surveillance" in category.name.lower():
            await interaction.followup.send(
                f"❌ Une catégorie de logs existe déjà : **{category.name}**",
                ephemeral=True
            )
            return

    try:
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }

        category = await guild.create_category(
            name="𓆩𖤍𓆪۰⟣ SURVEILLANCES ⟢۰𓆩𖤍𓆪",
            overwrites=overwrites
        )

        salon_configs = [
            ("📜・messages", "messages"),
            ("🎤・vocal", "vocal"),
            ("🎫・tickets", "ticket"),
            ("🛠️・commandes", "commands"),
            ("👑・rôles", "moderation"),
            ("📛・profil", "profile"),
            ("🔍・contenu", "content"),
            ("🚨・alertes", "alerts"),
            ("⚖️・sanctions", "sanctions"),
            ("🎉・giveaway", "giveaway"),
            ("💥・bavures", "bavures")
        ]

        channel_ids = {}
        for name, key in salon_configs:
            log_overwrites = {
                guild.default_role: discord.PermissionOverwrite(read_messages=False),
                guild.me: discord.PermissionOverwrite(
                    read_messages=True, 
                    send_messages=True,
                    manage_messages=True
                )
            }
            channel = await guild.create_text_channel(name=name, category=category, overwrites=log_overwrites)
            channel_ids[key] = channel.id

        if not isinstance(config.CONFIG, dict):
            config.CONFIG = {}
        config.CONFIG.setdefault("logs", {})
        config.CONFIG["logs"].update(channel_ids)

        await interaction.followup.send(
            f"✅ Catégorie **{category.name}** créée avec {len(salon_configs)} salons !",
            ephemeral=True
        )

    except Exception as e:
        await interaction.followup.send(f"❌ Erreur : {str(e)}", ephemeral=True)

@bot.tree.command(name="create-categorie", description="Crée une catégorie personnalisée")
@discord.app_commands.describe(nom="Nom de la catégorie")
@discord.app_commands.checks.has_permissions(administrator=True)
async def create_categorie(interaction: discord.Interaction, nom: str):
    await interaction.response.defer(ephemeral=True)
    guild = interaction.guild
    
    try:
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=True),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }
        category = await guild.create_category(name=nom, overwrites=overwrites)
        await interaction.followup.send(
            f"✅ Catégorie **{category.name}** créée avec succès !\nID : `{category.id}`",
            ephemeral=True
        )
    except Exception as e:
        await interaction.followup.send(f"❌ Erreur : {str(e)}", ephemeral=True)

@bot.tree.command(name="create-salon", description="Crée un salon dans une catégorie")
@discord.app_commands.describe(
    nom="Nom du salon",
    categorie="Catégorie où créer le salon"
)
@discord.app_commands.checks.has_permissions(administrator=True)
async def create_salon(interaction: discord.Interaction, nom: str, categorie: discord.CategoryChannel):
    await interaction.response.defer(ephemeral=True)
    
    try:
        channel = await categorie.create_text_channel(name=nom)
        await interaction.followup.send(
            f"✅ Salon **#{channel.name}** créé dans **{categorie.name}** !\nID : `{channel.id}`",
            ephemeral=True
        )
    except Exception as e:
        await interaction.followup.send(f"❌ Erreur : {str(e)}", ephemeral=True)


# ============================
# === COMMANDES DE SALON ===
# ============================

@bot.tree.command(name="clear-salon", description="Supprime tous les messages du salon")
@discord.app_commands.checks.has_permissions(manage_messages=True)
async def clear_salon(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    deleted = await interaction.channel.purge(limit=1000)
    await interaction.followup.send(f"🧹 **{len(deleted)}** messages supprimés.", ephemeral=True)

@bot.tree.command(name="delete-salon", description="Supprime un salon")
@discord.app_commands.describe(salon="Salon à supprimer")
@discord.app_commands.checks.has_permissions(manage_channels=True)
async def delete_salon(interaction: discord.Interaction, salon: discord.TextChannel):
    await salon.delete(reason=f"Supprimé par {interaction.user}")
    await interaction.response.send_message(f"✅ Salon **{salon.name}** supprimé.", ephemeral=True)

@bot.tree.command(name="delete-categorie", description="Supprime une catégorie et ses salons")
@discord.app_commands.describe(categorie="Catégorie à supprimer")
@discord.app_commands.checks.has_permissions(manage_channels=True)
async def delete_categorie(interaction: discord.Interaction, categorie: discord.CategoryChannel):
    await interaction.response.send_message("✅ Suppression en cours...", ephemeral=True)
    for channel in categorie.channels:
        try:
            await channel.delete(reason=f"Supprimé avec la catégorie par {interaction.user}")
        except:
            pass
    try:
        await categorie.delete(reason=f"Supprimé par {interaction.user}")
    except:
        pass

@bot.tree.command(name="say", description="Envoie un message dans un salon")
@discord.app_commands.describe(salon="Salon cible", contenu="Message à envoyer")
@discord.app_commands.checks.has_permissions(manage_messages=True)
async def say(interaction: discord.Interaction, salon: discord.TextChannel, contenu: str):
    contenu_nettoye = contenu.replace("\\n", "\n")
    await salon.send(contenu_nettoye)
    await interaction.response.send_message(f"✅ Message envoyé dans {salon.mention}.", ephemeral=True)


# ============================
# === COMMANDES DE MODÉRATION ===
# ============================

@bot.tree.command(name="kick", description="Expulse un membre")
@discord.app_commands.describe(pseudo="Membre à expulser", raison="Raison du kick")
@discord.app_commands.checks.has_permissions(kick_members=True)
async def kick(interaction: discord.Interaction, pseudo: discord.Member, raison: str = "Aucune raison"):
    if est_bavure_raison(raison):
        embed = discord.Embed(
            title="⚠️ Bavure détectée",
            description=f"**Modérateur** : {interaction.user.mention}\n**Cible** : {pseudo.mention}\n**Commande** : /kick\n**Raison** : *{raison}*",
            color=0xff6600,
            timestamp=discord.utils.utcnow()
        )
        await send_log_to(bot, "bavures", embed)
        await interaction.response.send_message("❌ La raison est invalide (moins de 2 mots ou texte aléatoire).", ephemeral=True)
        return

    try:
        await pseudo.send(f"⚠️ Vous avez été expulsé de **{interaction.guild.name}** pour : **{raison}**.")
    except:
        pass
    await pseudo.kick(reason=raison)
    embed = discord.Embed(
        title="👢 Kick",
        description=f"**Membre** : {pseudo.mention}\n**Modérateur** : {interaction.user.mention}\n**Raison** : {raison}",
        color=0xff9900,
        timestamp=datetime.utcnow()
    )
    ch = get_sanction_channel(bot)
    if ch: 
        await ch.send(embed=embed)
    await interaction.response.send_message(f"✅ {pseudo.mention} expulsé.", ephemeral=True)

@bot.tree.command(name="ban", description="Bannit un membre")
@discord.app_commands.describe(pseudo="Membre à bannir", temps="Jours de suppression des messages (0 = aucun)", raison="Raison du ban")
@discord.app_commands.checks.has_permissions(ban_members=True)
async def ban(interaction: discord.Interaction, pseudo: discord.Member, temps: int = 0, raison: str = "Aucune raison"):
    if est_bavure_raison(raison):
        embed = discord.Embed(
            title="⚠️ Bavure détectée",
            description=f"**Modérateur** : {interaction.user.mention}\n**Cible** : {pseudo.mention}\n**Commande** : /ban\n**Raison** : *{raison}*",
            color=0xff6600,
            timestamp=discord.utils.utcnow()
        )
        await send_log_to(bot, "bavures", embed)
        await interaction.response.send_message("❌ La raison est invalide (moins de 2 mots ou texte aléatoire).", ephemeral=True)
        return

    try:
        await pseudo.send(f"⚠️ Vous avez été banni de **{interaction.guild.name}** pour : **{raison}**.")
    except:
        pass
    await pseudo.ban(reason=raison, delete_message_days=temps)
    embed = discord.Embed(
        title="🔨 Ban",
        description=f"**Membre** : {pseudo.mention}\n**Modérateur** : {interaction.user.mention}\n**Raison** : {raison}",
        color=0xff0000,
        timestamp=datetime.utcnow()
    )
    ch = get_sanction_channel(bot)
    if ch: 
        await ch.send(embed=embed)
    await interaction.response.send_message(f"✅ {pseudo.mention} banni.", ephemeral=True)

@bot.tree.command(name="warn", description="Avertit un membre")
@discord.app_commands.describe(pseudo="Membre à avertir", raison="Raison de l'avertissement")
@discord.app_commands.checks.has_permissions(manage_messages=True)
async def warn(interaction: discord.Interaction, pseudo: discord.Member, raison: str = "Aucune raison"):
    if est_bavure_raison(raison):
        embed = discord.Embed(
            title="⚠️ Bavure détectée",
            description=f"**Modérateur** : {interaction.user.mention}\n**Cible** : {pseudo.mention}\n**Commande** : /warn\n**Raison** : *{raison}*",
            color=0xff6600,
            timestamp=discord.utils.utcnow()
        )
        await send_log_to(bot, "bavures", embed)
        await interaction.response.send_message("❌ La raison est invalide (moins de 2 mots ou texte aléatoire).", ephemeral=True)
        return

    embed = discord.Embed(
        title="⚠️ Avertissement",
        description=f"**Membre** : {pseudo.mention}\n**Modérateur** : {interaction.user.mention}\n**Raison** : {raison}",
        color=0xffff00,
        timestamp=discord.utils.utcnow()
    )
    ch = get_sanction_channel(bot)
    if ch: 
        await ch.send(embed=embed)
    await interaction.response.send_message(f"✅ Avertissement envoyé.", ephemeral=True)

@bot.tree.command(name="anti-spam", description="Active/désactive l'anti-spam")
@discord.app_commands.checks.has_permissions(administrator=True)
async def anti_spam(interaction: discord.Interaction, actif: bool):
    config.CONFIG["security"]["anti_spam"] = actif
    await interaction.response.send_message(f"✅ Anti-spam {'activé' if actif else 'désactivé'}.", ephemeral=True)

@bot.tree.command(name="anti-raid", description="Active/désactive l'anti-raid")
@discord.app_commands.checks.has_permissions(administrator=True)
async def anti_raid(interaction: discord.Interaction, actif: bool):
    config.CONFIG["security"]["anti_raid"] = actif
    await interaction.response.send_message(f"✅ Anti-raid {'activé' if actif else 'désactivé'}.", ephemeral=True)

@bot.tree.command(name="anti-hack", description="Active/désactive l'anti-hack")
@discord.app_commands.checks.has_permissions(administrator=True)
async def anti_hack(interaction: discord.Interaction, actif: bool):
    config.CONFIG["security"]["anti_hack"] = actif
    await interaction.response.send_message(f"✅ Anti-hack {'activé' if actif else 'désactivé'}.", ephemeral=True)


# ============================
# === COMMANDES DE TICKETS ===
# ============================

@bot.tree.command(name="ticket-panel", description="Envoie le panneau de création de ticket")
@discord.app_commands.checks.has_permissions(administrator=True)
async def ticket_panel(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🎟️ Support - Créer un ticket",
        description="Cliquez sur le bouton ci-dessous pour ouvrir un ticket avec l'équipe.\n\n> ⚠️ **Abuse = Sanction**",
        color=0x2f3136,
        timestamp=discord.utils.utcnow()
    )
    embed.set_footer(text="Seiko Security • Système sécurisé")
    await interaction.channel.send(embed=embed, view=TicketView())
    await interaction.response.send_message("✅ Pannel de tickets envoyé.", ephemeral=True)


# ============================
# === COMMANDES DE CONFIGURATION ===
# ============================

@bot.tree.command(name="config", description="Configure le bot")
@discord.app_commands.checks.has_permissions(administrator=True)
async def config_cmd(interaction: discord.Interaction):
    embed = discord.Embed(
        title="⚙️ Configuration de Seiko",
        description="Page de configuration disponible.",
        color=discord.Color.blurple()
    )
    await interaction.response.send_message(embed=embed, ephemeral=True)


# ============================
# === COMMANDES D'AUDIT ===
# ============================

@bot.tree.command(name="reachlog", description="Affiche le dernier log d'audit")
@discord.app_commands.checks.has_permissions(administrator=True)
async def reachlog(interaction: discord.Interaction):
    try:
        async for entry in interaction.guild.audit_logs(limit=1):
            log_msg = f"**{entry.action.name}**\n"
            log_msg += f"**Cible** : {getattr(entry, 'target', 'Inconnue')}\n"
            log_msg += f"**Auteur** : {entry.user}\n"
            log_msg += f"**Date** : <t:{int(entry.created_at.timestamp())}:R>"
            await interaction.response.send_message(log_msg, ephemeral=True)
            return
        await interaction.response.send_message("📭 Aucun log trouvé.", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"❌ Erreur : {e}", ephemeral=True)

@bot.tree.command(name="reach-id", description="Résout un ID Discord")
@discord.app_commands.describe(id="ID à résoudre")
@discord.app_commands.checks.has_permissions(administrator=True)
async def reach_id(interaction: discord.Interaction, id: str):
    try:
        obj_id = int(id)
    except ValueError:
        await interaction.response.send_message("❌ ID invalide. Doit être un nombre.", ephemeral=True)
        return

    guild = interaction.guild
    results = []

    member = guild.get_member(obj_id)
    if member:
        results.append(f"👤 **Membre** : {member.mention} (`{member}`)")

    channel = guild.get_channel(obj_id)
    if channel:
        results.append(f"💬 **Salon** : {channel.mention} (`{channel.name}`)")

    role = guild.get_role(obj_id)
    if role:
        results.append(f"👑 **Rôle** : {role.mention} (`{role.name}`)")

    if results:
        await interaction.response.send_message(
            f"🔍 Résultats pour l'ID `{id}` :\n" + "\n".join(results),
            ephemeral=True
        )
    else:
        await interaction.response.send_message(
            f"❌ Aucun utilisateur, salon ou rôle trouvé avec l'ID `{id}`.",
            ephemeral=True
        )


# ============================
# === LANCEMENT DU BOT ===
# ============================

bot.run(config.DISCORD_TOKEN)
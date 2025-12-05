# 🚀 SEIKO BOT - PROGRESS REPORT

## ✅ COMPLÉTÉ (Session Actuelle)

### Corrections Critiques
- ✅ Erreur 404 interaction timeout - Fixed avec `defer()` + `followup.send()`
- ✅ Boutons retour /config - Tous les back buttons passent maintenant guild
- ✅ LogsConfigView - Stocke maintenant le guild pour back button
- ✅ SelectView classes - Tous les 3 fonctionnels (RoleSelect, ChannelSelect, LogChannelSelect)
- ✅ Flask keep-alive - Utilise PORT env var pour Render

### Anti-AFK Système (NOUVEAU)
- ✅ Changement de status toutes les 4 min pour éviter timeout Render
- ✅ Keep-alive HTTP routes (`/` et `/ping`)
- ✅ Background task avec rotation de 5 activities différentes
- ✅ Resistance aux crash/redémarrage Render

### Config Storage (NOUVEAU)
- ✅ `CONFIG["ticket_config"]` - mode basic/advanced + options[]

---

## 🔄 EN COURS / À FAIRE

### 1️⃣ REFACTORISER /START (Haute Priorité)
**Problème**: Les SetupStep1-6 utilisent que des boutons "Suivant" basiques
**Solution**: Convertir en utilisant Select menus comme /config

**À faire**:
- [ ] SetupStep1View - Utiliser RoleSelectView pour auto-assign roles
- [ ] SetupStep2View - Utiliser RoleSelectView (admin role)
- [ ] SetupStep3View - Utiliser RoleSelectView (mod role)  
- [ ] SetupStep4View - Utiliser RoleSelectView (founder role)
- [ ] SetupStep5View - Utiliser ChannelSelectView (welcome/leave channels)
- [ ] SetupFinishView - Créer logs ou skip
- [ ] Passer `guild` à toutes les SetupStepView classes

**Code Minimal**:
```python
class SetupStep1View(discord.ui.View):
    def __init__(self, guild: discord.Guild):
        super().__init__(timeout=600)
        self.guild = guild
    
    @discord.ui.button(label="➡️ Suivant", style=discord.ButtonStyle.success)
    async def next_step(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(title="🎓 Setup Seiko - Étape 2/5", color=0x3498db)
        await interaction.response.edit_message(embed=embed, view=SetupStep2View(self.guild))
```

---

### 2️⃣ TICKET SYSTEM REFACTOR (Très Haute Priorité)
**Problème**: /ticket-panel très basique. Pas de choix, pas de gestion.
**Solution**: Ajouter interface avec choix + boutons de gestion

**À faire**:
- [ ] TicketChoiceSelect - Select menu pour choisir le type de ticket
- [ ] TicketChoiceView - View avec le Select + bouton "Envoyer"
- [ ] TicketManagementView - 4 boutons (Claim/Close/Reopen/Delete)
- [ ] Auto-generate ticket-XXXXXX avec numéro unique (counter en CONFIG)
- [ ] Claim = Clear tous messages sauf premier du bot
- [ ] Close = Disable SEND_MESSAGES + rename ticket à "close-ticket-XXXXXX"
- [ ] Reopen = Restore toutes les permissions (SEND_MESSAGES, EMBED_LINKS, etc.)
- [ ] Delete = Supprimer le canal ticket après 5 sec confirmation

**Stocker dans CONFIG**:
```python
"ticket_config": {
    "mode": "basic",
    "options": ["Bug Report", "Support", "Suggestion"],  # Basic mode = default
    "counter": 0  # Auto-increment pour ticket numéro
}
```

**Numérotation Ticket**:
- Chaque ticket = `ticket-001`, `ticket-002`, etc.
- Increment automatique dans CONFIG["ticket_config"]["counter"]

---

### 3️⃣ TICKET CONFIG COMMAND (Moyenne Priorité)
**New Commande**: `/ticket-config`

**À faire**:
- [ ] Step 1: Button "Basic Mode" ou "Advanced Mode"
- [ ] Step 2 (Advanced): Modal pour chaque option de ticket
  - Demander texte pour option (ex: "Bug Report")
  - Bouton "Ajouter une autre option?" OUI/NON
  - Si OUI, refaire modal. Si NON, finir
  - Sauvegarder dans `CONFIG["ticket_config"]["options"]`
- [ ] Step 2 (Basic): Garder les options par défaut (rien à faire)
- [ ] TicketChoiceSelect doit lire les options depuis CONFIG au lieu de hardcodées

**Workflow**:
```
/ticket-config
  ↓
Basic Mode? / Advanced Mode?
  ↓ (Advanced)
Modal: "Quel texte pour option 1?" → "Bug Report"
  ↓
Button: "Ajouter autre option?" OUI / NON
  ↓ (OUI)
Modal: "Quel texte pour option 2?" → "Support"
  ↓
Button: "Ajouter autre option?" OUI / NON
  ↓ (NON)
Embed: "✅ Configuration sauvegardée! Options: Bug Report, Support"
```

---

### 4️⃣ TICKET PANEL REFACTOR
**À faire**:
- [ ] Changer TicketView - Ajouter Select menu avec les options de CONFIG
- [ ] Bouton "Envoyer" pour créer le ticket
- [ ] À la création, afficher le ticket number (ticket-001, ticket-002, etc)
- [ ] Envoyer premier message du bot avec:
  - Titre: "Ticket {titre de l'option} - #{number}"
  - Message explicatif
  - Boutons: Claim, Close, Reopen, Delete
- [ ] TicketControls - Implémenter les 4 boutons

**Implémentation Claim**:
```python
async def claim(self, interaction: discord.Interaction, button: discord.ui.Button):
    channel = interaction.channel
    # Récupérer tous les messages
    messages = [msg async for msg in channel.history(limit=None, oldest_first=True)]
    # Garder le premier (du bot), supprimer les autres
    for msg in messages[1:]:
        try:
            await msg.delete()
        except:
            pass
    # Notifier
    embed = discord.Embed(title="✅ Ticket Claimed", description=f"par {interaction.user.mention}", color=0x2ecc71)
    await interaction.response.send_message(embed=embed)
```

**Implémentation Close**:
```python
async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
    channel = interaction.channel
    # Récupérer le numéro depuis le nom
    old_name = channel.name  # ticket-001
    # Récupérer le nombre de messages
    msg_count = len([m async for m in channel.history(limit=None)])
    
    # Créer embed de fermeture
    embed = discord.Embed(
        title="🔒 Ticket Fermé",
        description=f"{msg_count} messages\nFermé par {interaction.user.mention}",
        color=0xe74c3c
    )
    await interaction.response.send_message(embed=embed)
    
    # Désactiver permissions
    await channel.edit(name=f"close-{old_name}")
    for role in channel.guild.roles:
        if role.name != "@everyone":
            await channel.set_permissions(role, send_messages=False)
```

---

## 📋 CHECK LIST FINAL

- [ ] Syntax OK (run Python linter)
- [ ] /start utilise Select menus
- [ ] /ticket-panel avec choix multiples
- [ ] /ticket-config fonctionne
- [ ] Boutons ticket (Claim/Close/Reopen/Delete) tous OK
- [ ] Anti-AFK en production (test 10+ min)
- [ ] Git commit + push
- [ ] Déploiement Render

---

## 🔗 FILES À MODIFIER

- `main.py` - Refactoriser SetupStep, Ticket system, ajouter /ticket-config
- `core_config.py` - Déjà fait (ticket_config section)

---

## 💡 NOTES

- Les SetupStep views doivent accepter `guild: discord.Guild` dans `__init__`
- Chaque Select menu doit être dans une View séparée
- Les buttons doivent tous passer `guild` au suivant
- Ticket numbering: utiliser CONFIG["ticket_config"]["counter"]
- Test sur Render avec `curl -X GET https://seiko-bot.onrender.com/ping`


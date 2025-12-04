# 🤖 Seiko Bot - Guide Complet

## 📊 Résumé des Commandes

### ⚙️ Setup & Configuration (NOUVELLES!)

#### `/start` - Tutoriel de Configuration
Interface interactive en 6 étapes pour configurer votre serveur.

**Étapes:**
1. Rôles à l'arrivée d'un nouveau membre
2. Définir le Rôle Admin
3. Définir le Rôle Modérateur
4. Définir le Rôle Fondateur
5. Configurer Salons Bienvenue/Adieu
6. Création automatique des logs

**Usage:** `/start`

#### `/config` - Interface de Configuration (AMÉLIORÉ)
Interface complète avec 4 sections principales.

**Sections:**
- 📋 **Rôles & Salons** - Définir rôles admin/mod/fondateur et salons
- 📊 **Logs** - Détection automatique et création des salons de logs
- 🛡️ **Sécurité** - Activer/Désactiver Anti-Spam, Anti-Raid, Anti-Hack
- 👋 **Bienvenue/Adieu** - Configurer les salons

**Usage:** `/config`

---

### 📊 Logs & Salons

#### `/logs {type} {salon}`
Définit le salon de destination pour un type de log.

**Types:** messages, moderation, ticket, vocal, securite

#### `/scan-deleted`
Récupère les suppressions de messages récentes manquées (jusqu'à 5 min).

#### `/add-cat-log`
**IMPORTANT:** Crée automatiquement une catégorie complète avec tous les salons de logs:
- 📜 messages
- 🎤 vocal
- 🎫 tickets
- 🛠️ commandes
- 👑 rôles
- 📛 profil
- 🔍 contenu
- 🚨 alertes
- ⚖️ sanctions
- 🎉 giveaway
- 💥 bavures

#### `/create-categorie {nom}`
Crée une catégorie personnalisée.

#### `/create-salon {nom} {categorie}`
Crée un salon dans une catégorie spécifique.

#### `/clear-salon`
Supprime tous les messages du salon actuel.

#### `/delete-salon {salon}`
Supprime un salon spécifique.

#### `/delete-categorie {categorie}`
Supprime une catégorie ET tous ses salons.

---

### 👮 Modération

#### `/kick {pseudo} [raison]`
Expulse un membre du serveur.
- **Protections:** Vérifie que la raison est valide (min 2 mots)
- **Logs:** Enregistré dans le salon "sanctions"
- **Bavures:** Détectées et loggées si raison invalide

#### `/ban {pseudo} [temps] [raison]`
Bannit un membre du serveur.
- **Paramètres:** 
  - `pseudo` (obligatoire)
  - `temps` (jours, défaut: 0)
  - `raison` (défaut: "Aucune raison")
- **Protections:** Vérification raison valide
- **Logs:** Enregistré dans sanctions

#### `/warn {pseudo} [raison]`
Envoie un avertissement à un membre.
- **Logs:** Enregistré dans sanctions

---

### 🛡️ Sécurité

#### `/anti-spam {true/false}`
Active/désactive la protection anti-spam.
- Détecte les messages courts répétitifs
- Supprime automatiquement
- Ignore les messages de la whitelist

#### `/anti-raid {true/false}`
Active/désactive la protection anti-raid.
- Détecte 5+ joins en 60 secondes
- Alerte si même invitation utilisée

#### `/anti-hack {true/false}`
Active/désactive la protection anti-hack.
- Kick automatique: Compte < 5 min + pas d'avatar + nom suspect
- Protection contre les raids de bots

#### Configuration
Accédez à `/config` → 🛡️ **Sécurité** pour voir l'état et basculer les protections.

---

### 🎟️ Système de Tickets

#### `/ticket-panel`
Envoie le panneau de création de tickets dans le salon actuel.

**Boutons:**
- 📩 **Créer un ticket** - Ouvre un salon privé
- 🔧 **Prendre en charge** - Staff claim le ticket
- 🔒 **Fermer** - Ferme et archive les messages

**Fonctionnalités:**
- ✅ Capture automatique de tous les messages
- ✅ Timestamps pour chaque message
- ✅ URLs des pièces jointes
- ✅ Génération d'un fichier .txt si > 2000 caractères
- ✅ Logs dans le salon "tickets"

---

### ⚙️ Général

#### `/ping`
Affiche la latence du bot en ms.

#### `/say {salon} {contenu}`
Envoie un message dans un salon spécifique.

---

### 📜 Audit

#### `/reachlog`
Affiche le dernier log d'audit du serveur (qui a fait quoi).

#### `/reach-id {id}`
Résout un ID Discord et affiche:
- 👤 Profil si c'est un utilisateur
- 💬 Salon si c'est un channel
- 👑 Rôle si c'est un rôle

---

## 🔒 Protections & Sécurité

### Messages de Logs
- **Non modifiables** par les utilisateurs (sauf bot)
- **Non supprimables** par les utilisateurs (sauf bot)
- Seul le bot peut les supprimer

### Détection de Bavures
Logs automatiquement signalés si:
- Raison < 2 mots
- Raison vide ou "Aucune raison"
- Raison trop courte ou aléatoire

Enregistrés dans le salon **bavures**.

### Capture de Tickets
À la fermeture:
1. Tous les messages sont capturés
2. Timestamps et auteurs conservés
3. URLs des pièces jointes listées
4. Fichier .txt généré si volumineux
5. Archived dans le salon "tickets"

---

## 🚀 Installation & Déploiement

### Sur Render

1. **Connecter GitHub**
   - New Web Service
   - Connect Repository
   - Select: `loucs1546/Seiko_security`

2. **Variables d'Environnement**
   - `DISCORD_TOKEN` = votre token
   - `GUILD_ID` = ID de votre serveur

3. **Déployer**
   - Branch: `main`
   - Attendre ~2 minutes
   - Le bot sera online ✅

### Tests Essentiels

```
/ping                    → Doit répondre avec latence
/start                   → Doit ouvrir interface setup
/config                  → Doit ouvrir interface config
/add-cat-log            → Doit créer catégorie logs
/ticket-panel           → Doit envoyer panneau
```

---

## 📋 Architecture

```
main.py (900+ lignes)
├── Flask Keep-Alive
├── Views (Tickets, Config, Setup)
├── Helpers (bavures, sanctions channel)
├── Commandes (22 commandes)
└── on_ready (Charge cogs, sync commandes)

cogs/
├── logging.py (Event listeners)
├── security/
│   ├── antiraid.py
│   ├── antispam.py
│   ├── content_filter.py
│   └── link_filter.py
```

---

## 🎨 Interfaces Discord

### /config
```
┌─ 📋 Rôles & Salons
├─ 📊 Logs
├─ 🛡️ Sécurité
└─ ⬅️ Retour
```

### /start
```
Étape 1 → Étape 2 → Étape 3 → Étape 4 → Étape 5 → Étape 6 (Finaliser)
```

---

## ⚠️ Points Importants

1. **Token:** Ne jamais commit le token (dans .env)
2. **Permissions:** Bot doit avoir `Administrator` ou les perms spécifiques
3. **GUILD_ID:** Doit être défini (ID du serveur)
4. **Cogs:** Chargés automatiquement au démarrage
5. **Sync:** Commandes synchronisées au démarrage (guild si GUILD_ID, sinon global)

---

## 📞 Commandes Admin Uniquement

Toutes les commandes sauf `/ping` nécessitent `Administrator` permissions.

---

**Dernière mise à jour:** Décembre 2025
**Version:** 2.0 - Interfaces Complètes

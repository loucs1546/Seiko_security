#!/bin/bash

# ====================================
# DÉPLOIEMENT FINAL - VERSION COMPLÈTE
# ====================================

cd /workspaces/Seiko_security

echo ""
echo "════════════════════════════════════════════════════════"
echo "🚀 SEIKO BOT - DÉPLOIEMENT FINAL"
echo "════════════════════════════════════════════════════════"
echo ""

# Git config
if ! git config user.name > /dev/null 2>&1; then
    git config user.name "Seiko Bot"
    git config user.email "bot@seiko.local"
fi

# Stage files
echo "📝 Ajout des fichiers..."
git add -A

# Commit
echo "💾 Création du commit..."
git commit -m "✨ INTERFACES COMPLÈTES - /start et /config AMÉLIORÉ

🎯 NOUVELLES FONCTIONNALITÉS:

1️⃣ COMMANDE /START - TUTORIEL DE SETUP:
  - Étape 1: Rôles à l'arrivée
  - Étape 2: Configuration Rôle Admin
  - Étape 3: Configuration Rôle Modérateur
  - Étape 4: Configuration Rôle Fondateur
  - Étape 5: Salons Bienvenue/Adieu
  - Étape 6: Création automatique des logs

2️⃣ COMMANDE /CONFIG - INTERFACE COMPLÈTE:
  
  📋 RÔLES & SALONS:
    - Définir Rôle Admin
    - Définir Rôle Modérateur
    - Définir Rôle Fondateur
    - Configurer Salons Bienvenue/Adieu

  📊 CONFIGURATION DES LOGS:
    - Détection automatique des logs manquants
    - Création automatique avec /add-cat-log
    - Gestion complète des canaux de logs

  🛡️ SÉCURITÉ (NOUVEAU):
    - ✅ Toggle Anti-Spam (ON/OFF)
    - ✅ Toggle Anti-Raid (ON/OFF)
    - ✅ Toggle Anti-Hack (ON/OFF)
    - 📊 Afficher état complet

📋 COMMANDES VÉRIFIÉES (22 total):

  ⚙️  GÉNÉRALES (2):
    ✓ /ping - Latence du bot
    ✓ /say - Envoyer message

  📊 LOGS (6):
    ✓ /logs - Définir salon log
    ✓ /scan-deleted - Récupérer suppressions
    ✓ /add-cat-log - Créer catégorie logs
    ✓ /create-categorie - Créer catégorie
    ✓ /create-salon - Créer salon
    ✓ /clear-salon - Vider salon

  💬 SALONS (3):
    ✓ /delete-salon - Supprimer salon
    ✓ /delete-categorie - Supprimer catégorie

  👮 MODÉRATION (3):
    ✓ /kick - Expulser
    ✓ /ban - Bannir
    ✓ /warn - Avertir

  🛡️  SÉCURITÉ (3):
    ✓ /anti-spam - Toggle anti-spam
    ✓ /anti-raid - Toggle anti-raid
    ✓ /anti-hack - Toggle anti-hack

  🎟️ TICKETS (1):
    ✓ /ticket-panel - Envoyer panneau tickets

  ⚙️  CONFIGURATION (2):
    ✓ /config - Interface complète (NOUVELLE)
    ✓ /start - Tutoriel setup (NOUVELLE)

  📜 AUDIT (2):
    ✓ /reachlog - Dernier log d'audit
    ✓ /reach-id - Résoudre ID Discord

🎨 INTERFACES DISCORD:

  1. /config: Navigue via boutons interactifs
  2. /start: Tutoriel pas à pas (6 étapes)
  3. Toutes les views: Timeout 10 minutes, ephemeral

✅ STATUS: PRÊT POUR RENDER!"

if [ $? -eq 0 ]; then
    echo "✅ Commit réussi"
else
    echo "⚠️  Aucun changement"
fi

# Push
echo ""
echo "🌐 Push vers GitHub..."
git push -u origin main

if [ $? -eq 0 ]; then
    echo ""
    echo "════════════════════════════════════════════════════════"
    echo "✅ DÉPLOIEMENT RÉUSSI!"
    echo "════════════════════════════════════════════════════════"
    echo ""
    echo "📋 RÉSUMÉ DES COMMANDES:"
    echo ""
    echo "  🎓 Setup Serveur:"
    echo "    • /start - Tutoriel complet en 6 étapes"
    echo "    • /config - Interface de configuration"
    echo ""
    echo "  📊 Logs & Salons:"
    echo "    • /add-cat-log - Créer tous les logs auto"
    echo "    • /create-categorie {nom} - Créer catégorie"
    echo "    • /create-salon {nom} {categorie} - Créer salon"
    echo ""
    echo "  👮 Modération:"
    echo "    • /kick {pseudo} {raison} - Expulser"
    echo "    • /ban {pseudo} {temps} {raison} - Bannir"
    echo "    • /warn {pseudo} {raison} - Avertir"
    echo ""
    echo "  🛡️ Sécurité:"
    echo "    • /anti-spam {on/off}"
    echo "    • /anti-raid {on/off}"
    echo "    • /anti-hack {on/off}"
    echo ""
    echo "  🎟️ Tickets:"
    echo "    • /ticket-panel - Envoyer interface tickets"
    echo ""
    echo "  📜 Audit:"
    echo "    • /reachlog - Dernière action du serveur"
    echo "    • /reach-id {id} - Info sur un ID"
    echo ""
    echo "════════════════════════════════════════════════════════"
    echo ""
    echo "🔄 Prochaines étapes sur Render:"
    echo "  1. Redéployer depuis GitHub"
    echo "  2. Attendre ~2 minutes"
    echo "  3. Tester /ping et /start"
    echo ""
else
    echo "❌ Erreur lors du push"
    exit 1
fi

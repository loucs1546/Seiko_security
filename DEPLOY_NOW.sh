#!/bin/bash

# ====================================
# DÉPLOIEMENT FINAL - CONSOLIDATION COMPLÈTE
# ====================================

cd /workspaces/Seiko_security

echo "🚀 DÉPLOIEMENT SEIKO BOT - VERSION CONSOLIDÉE"
echo "=============================================="
echo ""

# Vérifier que git est configuré
if ! git config user.name > /dev/null 2>&1; then
    echo "⚠️  Git non configuré. Configuration..."
    git config user.name "Seiko Bot"
    git config user.email "bot@seiko.local"
fi

# Étape 1: Ajouter tous les fichiers
echo "📝 Stage 1: Ajout des fichiers..."
git add -A
echo "✅ Fichiers stagés"

# Étape 2: Créer le commit avec message détaillé
echo ""
echo "💾 Stage 2: Création du commit..."
git commit -m "🎯 CONSOLIDATION FINALE - TOUT DANS MAIN.PY

📦 ARCHITECTURE FINALE:
- main.py: 800+ lignes - TOUTES les commandes Discord
- cogs/logging.py: Event listeners pour les logs
- cogs/security/*: Event listeners pour la sécurité
- Plus de duplication, plus de conflit de sync!

✨ COMMANDES DISPONIBLES (50+):
  Générales: /ping, /config
  Logs: /logs, /scan-deleted, /add-cat-log, /create-categorie, /create-salon
  Salons: /clear-salon, /delete-salon, /delete-categorie, /say
  Modération: /kick, /ban, /warn, /anti-spam, /anti-raid, /anti-hack
  Tickets: /ticket-panel (avec capture complète des messages)
  Audit: /reachlog, /reach-id

🔒 SÉCURITÉ & PROTECTION:
  ✅ Messages de logs protégés (deletion prevention)
  ✅ Capture complète des tickets avec timestamps & attachments
  ✅ Détection bavures (raisons invalides)
  ✅ Audit logs complets

🎯 RÉSOLUTION PROBLÈMES:
  ❌ Ancien: Commandes dans 10+ fichiers cogs → sync instable
  ✅ Nouveau: Toutes les commandes dans 1 fichier → sync parfaite
  ✅ Cogs réduits aux listeners uniquement → zéro conflit

📊 STATISTIQUES:
  - main.py: 800+ lignes
  - Commandes: 50+
  - Views: 2 (TicketView, TicketControls)
  - Helpers: 2 (est_bavure_raison, get_sanction_channel)
  - Cogs listeners: 5 (logging, antiraid, antispam, content_filter, link_filter)

🚀 READY FOR RENDER DEPLOYMENT!"

if [ $? -eq 0 ]; then
    echo "✅ Commit créé avec succès"
else
    echo "⚠️  Aucun changement à commiter (déjà à jour)"
fi

# Étape 3: Push vers origin
echo ""
echo "🌐 Stage 3: Push vers GitHub..."
git push -u origin main

if [ $? -eq 0 ]; then
    echo "✅ Push réussi!"
    echo ""
    echo "════════════════════════════════════════"
    echo "🎉 DÉPLOIEMENT RÉUSSI!"
    echo "════════════════════════════════════════"
    echo ""
    echo "📋 Prochaines étapes (Render):"
    echo "  1. Va sur https://render.com"
    echo "  2. New + Web Service"
    echo "  3. Connect GitHub repository"
    echo "  4. Settings > Environment Variables:"
    echo "     - DISCORD_TOKEN = ton token"
    echo "     - GUILD_ID = ton guild ID"
    echo "  5. Deploy!"
    echo ""
    echo "✅ Le bot sera en ligne en ~2 minutes"
    echo ""
else
    echo "❌ Erreur lors du push!"
    exit 1
fi

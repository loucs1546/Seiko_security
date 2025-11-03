#!/usr/bin/env bash
set -euo pipefail

# 0) (Optionnel) activer venv si nécessaire
# source .venv/bin/activate

# 1) Générer requirements.txt (exécuter depuis le venv utilisé pour dev)
pip freeze > requirements.txt

# 2) Tester localement rapidement
python main.py & sleep 3 && pkill -f "python main.py" || true
echo "Test local rapide effectué (process démarré puis tué)."

# 3) Préparer le commit
git add .
git commit -m "Prepare deploy: requirements, Procfile, gitignore, fixes"

# 4) Si tu n'as pas encore de remote GitHub, crée et pousse avec gh (optionnel)
# Installe et connecte gh si besoin : https://cli.github.com/
# Remplace TON_REPO par 'utilisateur/nom-du-repo' ou juste 'nom-du-repo' si tu veux créer sous ton compte.
# Exemple : gh repo create mon-repo --public --source=. --remote=origin --push
if ! git ls-remote --exit-code origin >/dev/null 2>&1; then
  echo "Aucun remote 'origin' détecté. Créer le repo avec gh CLI..."
  read -p "Nom du repo GitHub à créer (ex: mon-repo) : " GH_REPO_NAME
  gh repo create "$GH_REPO_NAME" --public --source=. --remote=origin --push
else
  echo "Remote 'origin' détecté, push vers origin main..."
  git branch -M main || true
  git push -u origin main
fi

# 5) Vérifier que requirements.txt et Procfile sont bien présents (Railway les utilisera)
echo "Fichiers présents :"
ls -l Procfile requirements.txt .gitignore

# 6) Déploiement sur Railway (via UI recommandée)
echo ""
echo "Étapes Railway (UI recommandée) :"
echo " - Crée un nouveau projet -> 'Deploy from GitHub' -> sélectionne ton repo."
echo " - Dans Settings > Variables, ajoute DISCORD_TOKEN et GUILD_ID."
echo " - Déploie et surveille les logs."
echo ""
echo "Si tu utilises railway CLI, tu peux aussi lier le repo et définir les variables via la CLI."

# 7) Rappels de sécurité
echo ""
echo "Ne pousse jamais ton token dans le dépôt public. Assure-toi que .env est dans .gitignore."

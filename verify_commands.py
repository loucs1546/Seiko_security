#!/usr/bin/env python3
"""
Vérificateur de commandes Discord - Seiko Bot
Affiche toutes les commandes disponibles et leur description
"""

import ast
import re

def extract_commands(filepath):
    """Extrait toutes les commandes @bot.tree.command du fichier"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Trouver tous les @bot.tree.command
    pattern = r'@bot\.tree\.command\(name="([^"]+)",\s*description="([^"]+)"'
    matches = re.findall(pattern, content)
    
    commands = []
    for name, description in matches:
        commands.append({
            'name': name,
            'description': description
        })
    
    return commands

def main():
    commands = extract_commands('/workspaces/Seiko_security/main.py')
    
    print("\n" + "="*70)
    print("📋 VÉRIFICATION DES COMMANDES SEIKO BOT")
    print("="*70 + "\n")
    
    # Grouper par catégorie (inférée du nom)
    categories = {
        'general': [],
        'logs': [],
        'salon': [],
        'moderation': [],
        'security': [],
        'ticket': [],
        'audit': [],
        'config': []
    }
    
    for cmd in commands:
        name = cmd['name'].lower()
        
        if name in ['ping', 'say']:
            categories['general'].append(cmd)
        elif 'log' in name or 'scan' in name or 'cat' in name or 'categor' in name:
            categories['logs'].append(cmd)
        elif 'salon' in name or 'categor' in name:
            categories['salon'].append(cmd)
        elif any(x in name for x in ['kick', 'ban', 'warn']):
            categories['moderation'].append(cmd)
        elif any(x in name for x in ['anti', 'spam', 'raid', 'hack']):
            categories['security'].append(cmd)
        elif 'ticket' in name:
            categories['ticket'].append(cmd)
        elif any(x in name for x in ['reach', 'audit']):
            categories['audit'].append(cmd)
        else:
            categories['config'].append(cmd)
    
    total = len(commands)
    
    # Afficher par catégorie
    for category, cmds in categories.items():
        if cmds:
            emoji_map = {
                'general': '⚙️',
                'logs': '📊',
                'salon': '💬',
                'moderation': '👮',
                'security': '🛡️',
                'ticket': '🎟️',
                'audit': '📜',
                'config': '⚙️'
            }
            emoji = emoji_map.get(category, '📌')
            print(f"\n{emoji} {category.upper()} ({len(cmds)})")
            print("-" * 70)
            
            for cmd in cmds:
                print(f"  ✓ /{cmd['name']:<20} - {cmd['description']}")
    
    print("\n" + "="*70)
    print(f"✅ TOTAL: {total} commandes disponibles")
    print("="*70 + "\n")
    
    # Vérifications
    required = [
        'ping', 'config', 'start', 'logs', 'add-cat-log',
        'kick', 'ban', 'warn', 'ticket-panel', 'anti-spam'
    ]
    
    found_commands = {cmd['name'] for cmd in commands}
    missing = [cmd for cmd in required if cmd not in found_commands]
    
    if missing:
        print(f"⚠️  COMMANDES MANQUANTES: {missing}")
    else:
        print("✅ Toutes les commandes essentielles sont présentes!")
    
    return len(missing) == 0

if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)

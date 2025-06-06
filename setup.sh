#!/bin/bash
# Script de configuration rapide pour NextGen-Agent

set -e

echo "🚀 Configuration de NextGen-Agent"
echo "=================================="

# Vérifier Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 non trouvé"
    exit 1
fi

# Vérifier Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js non trouvé"
    exit 1
fi

# Vérifier npm
if ! command -v npm &> /dev/null; then
    echo "❌ npm non trouvé"
    exit 1
fi

echo "✅ Prérequis vérifiés"

# Créer l'environnement virtuel Python (optionnel)
if [ ! -d "venv" ]; then
    echo "📦 Création de l'environnement virtuel..."
    python3 -m venv venv
fi

# Activer l'environnement virtuel
if [ -f "venv/bin/activate" ]; then
    echo "🔄 Activation de l'environnement virtuel..."
    source venv/bin/activate
fi

# Lancer la configuration
echo "🔧 Lancement de la configuration automatique..."
python3 scripts/quick_start.py

echo "✅ Configuration terminée!"

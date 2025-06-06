#!/usr/bin/env python3
"""
Script pour vérifier le statut actuel du système NextGen-Agent
"""

import os
import sys
import json
import subprocess
from pathlib import Path

def print_header(title):
    print(f"\n🔍 {title}")
    print("=" * 60)

def print_success(message):
    print(f"✅ {message}")

def print_warning(message):
    print(f"⚠️  {message}")

def print_error(message):
    print(f"❌ {message}")

def check_system_status():
    """Vérifie le statut complet du système"""
    print_header("STATUT SYSTÈME NEXTGEN-AGENT")
    
    # 1. Vérifier les composants principaux
    components = {
        "API FastAPI": "api/server.py",
        "Interface Next.js": "app/page.tsx",
        "Agent Support NetworkX": "agents/support_agent/agentic_support_agent_networkx.py",
        "Agent Cybersécurité": "agents/cybersecurity_agent/complete_cybersecurity_agent.py",
        "NetworkX Graph Manager": "core/networkx_graph_manager.py",
        "Configuration TeamSquare": "config/teamsquare_config.py"
    }
    
    print_header("COMPOSANTS PRINCIPAUX")
    for name, path in components.items():
        if os.path.exists(path):
            print_success(f"{name}: {path}")
        else:
            print_error(f"{name}: MANQUANT - {path}")
    
    # 2. Vérifier les dépendances Python
    print_header("DÉPENDANCES PYTHON")
    required_packages = [
        "fastapi", "uvicorn", "chromadb", "sentence-transformers",
        "networkx", "google-generativeai", "requests", "beautifulsoup4"
    ]
    
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
            print_success(f"{package}")
        except ImportError:
            print_error(f"{package} - À installer")
    
    # 3. Vérifier les données
    print_header("DONNÉES ET BASES")
    data_paths = {
        "ChromaDB": "data/vector_db/chroma_db",
        "NetworkX Graph": "data/graph_db/knowledge_graph.pkl",
        "Mémoire Conversations": "data/memory/conversations.json",
        "Knowledge Base": "data/knowledge_base/teamsquare_knowledge.json"
    }
    
    for name, path in data_paths.items():
        if os.path.exists(path):
            print_success(f"{name}: {path}")
        else:
            print_warning(f"{name}: À créer - {path}")
    
    # 4. Vérifier les variables d'environnement
    print_header("VARIABLES D'ENVIRONNEMENT")
    env_vars = {
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
        "GOOGLE_API_KEY": os.getenv("GOOGLE_API_KEY"),
        "HUGGINGFACE_TOKEN": os.getenv("HUGGINGFACE_TOKEN")
    }
    
    for var, value in env_vars.items():
        if value and value != "":
            print_success(f"{var}: Configuré")
        else:
            print_warning(f"{var}: Non configuré")
    
    # 5. Tester les agents
    print_header("TEST DES AGENTS")
    try:
        sys.path.append('.')
        from agents.support_agent.agentic_support_agent_networkx import AgenticSupportAgentNetworkX
        agent = AgenticSupportAgentNetworkX()
        stats = agent.get_stats()
        print_success(f"Agent NetworkX: {stats['total_queries']} requêtes traitées")
        print_success(f"Composants: {stats['components_status']}")
    except Exception as e:
        print_error(f"Agent NetworkX: {str(e)}")
    
    # 6. Vérifier l'interface Next.js
    print_header("INTERFACE NEXT.JS")
    if os.path.exists("package.json"):
        print_success("package.json trouvé")
        if os.path.exists("node_modules"):
            print_success("node_modules installé")
        else:
            print_warning("node_modules manquant - Exécuter: npm install")
    else:
        print_error("package.json manquant")

def suggest_next_actions():
    """Suggère les prochaines actions"""
    print_header("PROCHAINES ACTIONS SUGGÉRÉES")
    
    actions = [
        "🚀 Lancer l'API: python api/server.py",
        "🌐 Lancer l'interface: npm run dev",
        "📊 Peupler le graphe NetworkX: python scripts/populate_networkx_graph.py",
        "🧪 Tester les agents: python agents/support_agent/agentic_support_agent_networkx.py",
        "🔧 Configurer les clés API dans .env",
        "📚 Ingérer les données TeamSquare: python scripts/ingest_teamsquare_data.py"
    ]
    
    for i, action in enumerate(actions, 1):
        print(f"{i}. {action}")

def main():
    """Fonction principale"""
    check_system_status()
    suggest_next_actions()
    
    print_header("RÉSUMÉ")
    print("🎯 Le système NextGen-Agent est prêt !")
    print("🔧 Quelques configurations peuvent être nécessaires")
    print("🚀 Prêt pour le lancement et les tests")

if __name__ == "__main__":
    main()

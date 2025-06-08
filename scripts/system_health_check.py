#!/usr/bin/env python3
"""
Système de vérification complète de l'état de NextGen Agent
"""

import os
import sys
import json
import importlib
import subprocess
from pathlib import Path
from typing import Dict, List, Any
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SystemHealthChecker:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.results = {
            "environment": {},
            "dependencies": {},
            "models": {},
            "databases": {},
            "agents": {},
            "apis": {},
            "overall_status": "UNKNOWN"
        }
    
    def check_environment(self):
        """Vérification de l'environnement"""
        print("🔍 VÉRIFICATION DE L'ENVIRONNEMENT")
        print("=" * 50)
        
        # Python version
        python_version = sys.version
        print(f"✅ Python: {python_version}")
        self.results["environment"]["python"] = python_version
        
        # Variables d'environnement critiques
        env_vars = [
            "OPENAI_API_KEY", "HUGGINGFACE_TOKEN", "HUGGINGFACE_USERNAME",
            "NEO4J_URI", "NEO4J_USER", "NEO4J_PASSWORD"
        ]
        
        for var in env_vars:
            value = os.getenv(var)
            status = "✅" if value else "❌"
            print(f"{status} {var}: {'SET' if value else 'NOT SET'}")
            self.results["environment"][var] = bool(value)
    
    def check_dependencies(self):
        """Vérification des dépendances Python"""
        print("\n🔍 VÉRIFICATION DES DÉPENDANCES")
        print("=" * 50)
        
        critical_packages = [
            "fastapi", "uvicorn", "langchain", "langchain_openai",
            "transformers", "torch", "scikit-learn", "numpy",
            "pandas", "chromadb", "neo4j", "structlog",
            "crawl4ai", "requests", "aiohttp"
        ]
        
        for package in critical_packages:
            try:
                importlib.import_module(package)
                print(f"✅ {package}: INSTALLÉ")
                self.results["dependencies"][package] = True
            except ImportError:
                print(f"❌ {package}: MANQUANT")
                self.results["dependencies"][package] = False
    
    def check_models(self):
        """Vérification des modèles ML"""
        print("\n🔍 VÉRIFICATION DES MODÈLES")
        print("=" * 50)
        
        models_dir = self.project_root / "models"
        if not models_dir.exists():
            print("❌ Dossier models/ n'existe pas")
            self.results["models"]["directory"] = False
            return
        
        expected_models = [
            "intent_classifier",
            "vulnerability_classifier", 
            "network_analyzer",
            "bge_embeddings"
        ]
        
        for model in expected_models:
            model_path = models_dir / model
            if model_path.exists():
                print(f"✅ {model}: TROUVÉ")
                self.results["models"][model] = True
            else:
                print(f"❌ {model}: MANQUANT")
                self.results["models"][model] = False
    
    def check_databases(self):
        """Vérification des bases de données"""
        print("\n🔍 VÉRIFICATION DES BASES DE DONNÉES")
        print("=" * 50)
        
        # ChromaDB
        try:
            import chromadb
            print("✅ ChromaDB: DISPONIBLE")
            self.results["databases"]["chromadb"] = True
        except Exception as e:
            print(f"❌ ChromaDB: ERREUR - {e}")
            self.results["databases"]["chromadb"] = False
        
        # Neo4j
        try:
            from neo4j import GraphDatabase
            neo4j_uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
            print(f"✅ Neo4j: CONFIGURÉ ({neo4j_uri})")
            self.results["databases"]["neo4j"] = True
        except Exception as e:
            print(f"❌ Neo4j: ERREUR - {e}")
            self.results["databases"]["neo4j"] = False
    
    def check_agents(self):
        """Vérification des agents"""
        print("\n🔍 VÉRIFICATION DES AGENTS")
        print("=" * 50)
        
        agents = [
            "agents.support_agent.agent",
            "agents.cybersecurity_agent.agent", 
            "agents.teamsquare_agent.agent"
        ]
        
        for agent in agents:
            try:
                module = importlib.import_module(agent)
                print(f"✅ {agent}: IMPORTABLE")
                self.results["agents"][agent] = True
            except Exception as e:
                print(f"❌ {agent}: ERREUR - {e}")
                self.results["agents"][agent] = False
    
    def check_apis(self):
        """Vérification des APIs"""
        print("\n🔍 VÉRIFICATION DES APIs")
        print("=" * 50)
        
        # API FastAPI
        try:
            from api.server1 import app
            print("✅ FastAPI: IMPORTABLE")
            self.results["apis"]["fastapi"] = True
        except Exception as e:
            print(f"❌ FastAPI: ERREUR - {e}")
            self.results["apis"]["fastapi"] = False
        
        # Test de connectivité OpenAI
        if os.getenv("OPENAI_API_KEY"):
            try:
                from openai import OpenAI
                client = OpenAI()
                print("✅ OpenAI API: CONFIGURÉE")
                self.results["apis"]["openai"] = True
            except Exception as e:
                print(f"❌ OpenAI API: ERREUR - {e}")
                self.results["apis"]["openai"] = False
    
    def generate_report(self):
        """Génération du rapport final"""
        print("\n📊 RAPPORT FINAL")
        print("=" * 50)
        
        # Calcul du score global
        total_checks = 0
        passed_checks = 0
        
        for category, checks in self.results.items():
            if category == "overall_status":
                continue
            for check, status in checks.items():
                total_checks += 1
                if status:
                    passed_checks += 1
        
        success_rate = (passed_checks / total_checks) * 100 if total_checks > 0 else 0
        
        if success_rate >= 80:
            self.results["overall_status"] = "EXCELLENT"
            status_emoji = "🟢"
        elif success_rate >= 60:
            self.results["overall_status"] = "BON"
            status_emoji = "🟡"
        else:
            self.results["overall_status"] = "CRITIQUE"
            status_emoji = "🔴"
        
        print(f"{status_emoji} STATUT GLOBAL: {self.results['overall_status']}")
        print(f"📈 SCORE: {passed_checks}/{total_checks} ({success_rate:.1f}%)")
        
        # Sauvegarde du rapport
        report_file = self.project_root / "health_report.json"
        with open(report_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"💾 Rapport sauvegardé: {report_file}")
        
        return self.results
    
    def run_full_check(self):
        """Exécution de toutes les vérifications"""
        print("🚀 NEXTGEN AGENT - VÉRIFICATION SYSTÈME COMPLÈTE")
        print("=" * 60)
        
        self.check_environment()
        self.check_dependencies()
        self.check_models()
        self.check_databases()
        self.check_agents()
        self.check_apis()
        
        return self.generate_report()

def main():
    checker = SystemHealthChecker()
    results = checker.run_full_check()
    
    # Recommandations basées sur les résultats
    print("\n💡 RECOMMANDATIONS")
    print("=" * 50)
    
    if not results["environment"].get("OPENAI_API_KEY"):
        print("🔑 Configurez OPENAI_API_KEY dans votre .env")
    
    missing_deps = [k for k, v in results["dependencies"].items() if not v]
    if missing_deps:
        print(f"📦 Installez les dépendances manquantes: {', '.join(missing_deps)}")
    
    missing_models = [k for k, v in results["models"].items() if not v]
    if missing_models:
        print(f"🤖 Téléchargez les modèles manquants: {', '.join(missing_models)}")
    
    if not results["databases"].get("chromadb"):
        print("🗄️ Initialisez ChromaDB")
    
    if not results["databases"].get("neo4j"):
        print("🕸️ Configurez Neo4j")

if __name__ == "__main__":
    main()

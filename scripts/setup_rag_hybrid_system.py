"""
Configuration complète du système RAG hybride (Vector + Graph)
"""

import os
import sys
import logging
import json
from pathlib import Path

# Ajouter le répertoire racine au path
sys.path.append(str(Path(__file__).parent.parent))

def setup_neo4j_config():
    """Configure Neo4j dans settings.py"""
    print("🔧 Configuration Neo4j...")
    
    settings_path = "config/settings.py"
    
    # Lire le fichier settings.py
    with open(settings_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Ajouter les variables Neo4j si elles n'existent pas
    neo4j_vars = """
# Neo4j Configuration
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")
"""
    
    if "NEO4J_URI" not in content:
        # Trouver la ligne avec CHROMA_PERSIST_DIR et ajouter après
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if "CHROMA_PERSIST_DIR" in line:
                lines.insert(i + 1, neo4j_vars)
                break
        
        content = '\n'.join(lines)
        
        with open(settings_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ Variables Neo4j ajoutées à settings.py")
    else:
        print("✅ Variables Neo4j déjà présentes")

def setup_env_file():
    """Configure le fichier .env"""
    print("🔧 Configuration .env...")
    
    env_content = """
# Neo4j Configuration
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=password

# Existing variables...
"""
    
    # Lire le .env existant
    env_path = ".env"
    existing_content = ""
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            existing_content = f.read()
    
    # Ajouter Neo4j si pas présent
    if "NEO4J_URI" not in existing_content:
        with open(env_path, 'a') as f:
            f.write(env_content)
        print("✅ Variables Neo4j ajoutées à .env")
    else:
        print("✅ Variables Neo4j déjà présentes dans .env")

def populate_chromadb():
    """Peuple ChromaDB avec des données d'exemple"""
    print("🔧 Population ChromaDB...")
    
    try:
        from sentence_transformers import SentenceTransformer
        import chromadb
        from chromadb.config import Settings
        
        # Initialiser ChromaDB
        chroma_path = "./data/vector_db/chroma_db"
        os.makedirs(chroma_path, exist_ok=True)
        
        client = chromadb.PersistentClient(
            path=chroma_path,
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Supprimer et recréer la collection
        try:
            client.delete_collection("knowledge_base")
        except:
            pass
        
        collection = client.create_collection("knowledge_base")
        
        # Charger le modèle d'embedding
        model = SentenceTransformer('BAAI/bge-large-en-v1.5')
        
        # Documents d'exemple TeamSquare
        documents = [
            {
                "content": "TeamSquare propose trois plans tarifaires : Plan Starter à 29€/mois pour jusqu'à 10 utilisateurs avec fonctionnalités de base, Plan Professional à 79€/mois pour jusqu'à 50 utilisateurs avec fonctionnalités avancées et API, Plan Enterprise à 199€/mois pour utilisateurs illimités avec toutes fonctionnalités et support dédié.",
                "metadata": {"type": "pricing", "source": "official_docs"}
            },
            {
                "content": "TeamSquare est une plateforme de collaboration moderne qui offre collaboration en temps réel avec chat intégré, gestion de projets intuitive et visuelle, partage de fichiers sécurisé, tableaux de bord et analytics avancés, API complète pour intégrations, sécurité de niveau entreprise.",
                "metadata": {"type": "features", "source": "product_description"}
            },
            {
                "content": "L'API TeamSquare permet d'intégrer facilement la plateforme avec vos outils existants. Elle offre des endpoints REST pour gérer les utilisateurs, projets, tâches, et fichiers. Documentation complète disponible avec exemples de code en Python, JavaScript, et PHP.",
                "metadata": {"type": "api", "source": "api_docs"}
            },
            {
                "content": "TeamSquare s'intègre avec plus de 50 outils populaires : Slack, Microsoft Teams, Google Workspace, Trello, Asana, GitHub, GitLab, Jira, Salesforce, HubSpot, Zoom, et bien d'autres. Intégrations natives et via API.",
                "metadata": {"type": "integrations", "source": "integrations_list"}
            },
            {
                "content": "Support TeamSquare disponible 24/7 pour les plans Enterprise, support prioritaire pour les plans Professional, support email pour les plans Starter. Base de connaissances complète, tutoriels vidéo, et webinaires de formation disponibles.",
                "metadata": {"type": "support", "source": "support_info"}
            }
        ]
        
        # Générer les embeddings et ajouter à ChromaDB
        texts = [doc["content"] for doc in documents]
        embeddings = model.encode(texts).tolist()
        
        collection.add(
            ids=[f"doc_{i}" for i in range(len(documents))],
            documents=texts,
            metadatas=[doc["metadata"] for doc in documents],
            embeddings=embeddings
        )
        
        print(f"✅ {len(documents)} documents ajoutés à ChromaDB")
        
    except Exception as e:
        print(f"❌ Erreur population ChromaDB: {e}")

def populate_neo4j():
    """Peuple Neo4j avec des données d'exemple"""
    print("🔧 Population Neo4j...")
    
    try:
        # Vérifier si Neo4j est disponible
        import subprocess
        result = subprocess.run(['docker', 'ps'], capture_output=True, text=True)
        
        if 'neo4j' not in result.stdout:
            print("⚠️  Neo4j non détecté. Démarrage avec Docker...")
            
            # Démarrer Neo4j avec Docker
            docker_cmd = [
                'docker', 'run', '-d',
                '--name', 'neo4j-teamsquare',
                '-p', '7474:7474', '-p', '7687:7687',
                '-e', 'NEO4J_AUTH=neo4j/password',
                'neo4j:latest'
            ]
            
            subprocess.run(docker_cmd, check=True)
            print("✅ Neo4j démarré avec Docker")
            
            # Attendre que Neo4j soit prêt
            import time
            print("⏳ Attente du démarrage de Neo4j...")
            time.sleep(10)
        
        # Importer et utiliser le graph manager
        from core.graph_manager import KnowledgeGraphManager
        
        graph_manager = KnowledgeGraphManager()
        
        # Ajouter des entités TeamSquare
        entities = [
            ("TeamSquare", "Platform", {"description": "Plateforme de collaboration moderne"}),
            ("Plan Starter", "PricingPlan", {"price": "29€/mois", "users": "10"}),
            ("Plan Professional", "PricingPlan", {"price": "79€/mois", "users": "50"}),
            ("Plan Enterprise", "PricingPlan", {"price": "199€/mois", "users": "unlimited"}),
            ("API", "Feature", {"type": "REST", "documentation": "available"}),
            ("Chat", "Feature", {"type": "real-time", "integrated": True}),
            ("Projects", "Feature", {"type": "management", "visual": True}),
            ("Files", "Feature", {"type": "sharing", "secure": True}),
            ("Slack", "Integration", {"type": "chat", "native": True}),
            ("GitHub", "Integration", {"type": "development", "native": True})
        ]
        
        # Ajouter les entités
        for name, entity_type, properties in entities:
            graph_manager.add_entity(name, entity_type, properties)
        
        # Ajouter des relations
        relations = [
            ("TeamSquare", "HAS_PLAN", "Plan Starter"),
            ("TeamSquare", "HAS_PLAN", "Plan Professional"),
            ("TeamSquare", "HAS_PLAN", "Plan Enterprise"),
            ("TeamSquare", "HAS_FEATURE", "API"),
            ("TeamSquare", "HAS_FEATURE", "Chat"),
            ("TeamSquare", "HAS_FEATURE", "Projects"),
            ("TeamSquare", "HAS_FEATURE", "Files"),
            ("TeamSquare", "INTEGRATES_WITH", "Slack"),
            ("TeamSquare", "INTEGRATES_WITH", "GitHub"),
            ("Plan Professional", "INCLUDES", "API"),
            ("Plan Enterprise", "INCLUDES", "API")
        ]
        
        for from_entity, relation_type, to_entity in relations:
            graph_manager.add_relation(from_entity, relation_type, to_entity)
        
        print(f"✅ {len(entities)} entités et {len(relations)} relations ajoutées à Neo4j")
        
    except Exception as e:
        print(f"❌ Erreur population Neo4j: {e}")
        print("💡 Conseil: Installez Docker et Neo4j pour utiliser le Graph RAG")

def main():
    """Configuration complète du système RAG hybride"""
    print("🚀 CONFIGURATION SYSTÈME RAG HYBRIDE")
    print("=" * 50)
    
    try:
        # 1. Configuration Neo4j
        setup_neo4j_config()
        setup_env_file()
        
        # 2. Population ChromaDB
        populate_chromadb()
        
        # 3. Population Neo4j
        populate_neo4j()
        
        print("\n🎉 CONFIGURATION TERMINÉE !")
        print("=" * 50)
        print("✅ ChromaDB peuplé avec des documents TeamSquare")
        print("✅ Neo4j configuré avec entités et relations")
        print("✅ Variables d'environnement configurées")
        print("\n🚀 Testez maintenant :")
        print("python agents/support_agent/agentic_support_agent_rag_graph.py")
        
    except Exception as e:
        print(f"❌ Erreur configuration: {e}")

if __name__ == "__main__":
    main()

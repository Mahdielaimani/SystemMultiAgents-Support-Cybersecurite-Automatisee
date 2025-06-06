"""
Script pour peupler ChromaDB avec des données TeamSquare
"""

import os
import sys
from pathlib import Path
import logging
import chromadb
from sentence_transformers import SentenceTransformer

# Ajouter le répertoire racine au path
sys.path.append(str(Path(__file__).parent.parent))

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def populate_chromadb():
    """Peuple ChromaDB avec des données TeamSquare"""
    
    print("🚀 POPULATION DE CHROMADB")
    print("=" * 50)
    
    try:
        # Initialiser ChromaDB
        print("🔧 Initialisation ChromaDB...")
        chroma_path = "./data/vector_db/chroma_db"
        os.makedirs(chroma_path, exist_ok=True)
        
        client = chromadb.PersistentClient(path=chroma_path)
        
        # Supprimer et recréer la collection
        print("🔧 Création/réinitialisation de la collection...")
        try:
            client.delete_collection("teamsquare_knowledge")
            print("✅ Collection existante supprimée")
        except:
            print("ℹ️ Aucune collection existante à supprimer")
        
        collection = client.create_collection("teamsquare_knowledge")
        print("✅ Nouvelle collection créée")
        
        # Charger le modèle d'embedding
        print("🔧 Chargement du modèle d'embedding...")
        model = SentenceTransformer('BAAI/bge-large-en-v1.5')
        print("✅ Modèle chargé")
        
        # Documents TeamSquare
        print("🔧 Préparation des documents...")
        documents = [
            {
                "id": "pricing_plans",
                "content": "TeamSquare propose trois plans tarifaires : Plan Starter à 29€/mois pour jusqu'à 10 utilisateurs avec fonctionnalités de base, Plan Professional à 79€/mois pour jusqu'à 50 utilisateurs avec fonctionnalités avancées et API, Plan Enterprise à 199€/mois pour utilisateurs illimités avec toutes fonctionnalités et support dédié.",
                "metadata": {"type": "pricing", "source": "official_docs"}
            },
            {
                "id": "features_overview",
                "content": "TeamSquare est une plateforme de collaboration moderne qui offre collaboration en temps réel avec chat intégré, gestion de projets intuitive et visuelle, partage de fichiers sécurisé, tableaux de bord et analytics avancés, API complète pour intégrations, sécurité de niveau entreprise.",
                "metadata": {"type": "features", "source": "product_description"}
            },
            {
                "id": "api_documentation",
                "content": "L'API TeamSquare permet d'intégrer facilement la plateforme avec vos outils existants. Elle offre des endpoints REST pour gérer les utilisateurs, projets, tâches, et fichiers. Documentation complète disponible avec exemples de code en Python, JavaScript, et PHP.",
                "metadata": {"type": "api", "source": "api_docs"}
            },
            {
                "id": "integrations_list",
                "content": "TeamSquare s'intègre avec plus de 50 outils populaires : Slack, Microsoft Teams, Google Workspace, Trello, Asana, GitHub, GitLab, Jira, Salesforce, HubSpot, Zoom, et bien d'autres. Intégrations natives et via API.",
                "metadata": {"type": "integrations", "source": "integrations_list"}
            },
            {
                "id": "support_info",
                "content": "Support TeamSquare disponible 24/7 pour les plans Enterprise, support prioritaire pour les plans Professional, support email pour les plans Starter. Base de connaissances complète, tutoriels vidéo, et webinaires de formation disponibles.",
                "metadata": {"type": "support", "source": "support_info"}
            },
            {
                "id": "security_features",
                "content": "TeamSquare protège vos données avec un chiffrement de bout en bout, authentification à deux facteurs, contrôles d'accès granulaires, journalisation des activités, et conformité RGPD. Audits de sécurité réguliers et certifications ISO 27001.",
                "metadata": {"type": "security", "source": "security_docs"}
            },
            {
                "id": "mobile_apps",
                "content": "TeamSquare propose des applications mobiles pour iOS et Android permettant d'accéder à toutes les fonctionnalités essentielles en déplacement. Synchronisation en temps réel, notifications push, et mode hors ligne disponibles.",
                "metadata": {"type": "mobile", "source": "app_store"}
            },
            {
                "id": "onboarding_process",
                "content": "L'onboarding TeamSquare est simple et rapide. Créez votre compte, invitez votre équipe, importez vos données existantes avec nos outils de migration, et commencez à collaborer immédiatement. Support dédié disponible pour les plans Professional et Enterprise.",
                "metadata": {"type": "onboarding", "source": "getting_started"}
            },
            {
                "id": "use_cases",
                "content": "TeamSquare est utilisé par des équipes de toutes tailles dans divers secteurs : développement logiciel, marketing, design, RH, finance, éducation, et plus. Cas d'usage populaires : gestion de projets agiles, collaboration créative, suivi client, et coordination d'équipes distantes.",
                "metadata": {"type": "use_cases", "source": "case_studies"}
            },
            {
                "id": "testimonials",
                "content": "Nos clients adorent TeamSquare : 'TeamSquare a transformé notre façon de travailler. Notre productivité a augmenté de 35%.' - Marie D., Directrice Marketing. '90% de nos réunions ont été remplacées par une collaboration asynchrone efficace.' - Thomas L., CTO.",
                "metadata": {"type": "testimonials", "source": "customer_stories"}
            }
        ]
        
        print(f"✅ {len(documents)} documents préparés")
        
        # Générer les embeddings et ajouter à ChromaDB
        print("🔧 Génération des embeddings et ajout à ChromaDB...")
        
        ids = [doc["id"] for doc in documents]
        texts = [doc["content"] for doc in documents]
        metadatas = [doc["metadata"] for doc in documents]
        
        # Générer les embeddings
        embeddings = model.encode(texts).tolist()
        
        # Ajouter à ChromaDB
        collection.add(
            ids=ids,
            documents=texts,
            metadatas=metadatas,
            embeddings=embeddings
        )
        
        print(f"✅ {len(documents)} documents ajoutés à ChromaDB")
        
        # Vérifier que les documents sont bien ajoutés
        print("🔧 Vérification des documents...")
        count = collection.count()
        print(f"✅ Collection contient {count} documents")
        
        # Test de recherche
        print("🔧 Test de recherche...")
        query_embedding = model.encode(["prix TeamSquare"]).tolist()
        results = collection.query(
            query_embeddings=query_embedding,
            n_results=2
        )
        
        print(f"✅ Test de recherche réussi - {len(results['documents'][0])} résultats trouvés")
        print(f"   Premier résultat: {results['documents'][0][0][:100]}...")
        
        print("\n🎉 POPULATION DE CHROMADB TERMINÉE AVEC SUCCÈS !")
        print("=" * 50)
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        logger.error(f"Erreur: {e}")

if __name__ == "__main__":
    populate_chromadb()

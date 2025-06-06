"""
Script pour peupler le graphe NetworkX avec des données TeamSquare
"""
import sys
import os
from pathlib import Path

# Ajouter le répertoire racine au path
sys.path.append(str(Path(__file__).parent.parent))

from core.networkx_graph_manager import NetworkXGraphManager

def populate_teamsquare_graph():
    """Peuple le graphe NetworkX avec des données TeamSquare"""
    print("🚀 POPULATION DU GRAPHE NETWORKX")
    print("=" * 50)
    
    # Initialiser le gestionnaire
    graph_manager = NetworkXGraphManager()
    
    print("🔧 Ajout des entités TeamSquare...")
    
    # Entités principales
    entities = [
        ("TeamSquare", "Platform", {
            "description": "Plateforme de collaboration moderne",
            "website": "https://teamsquare.com",
            "founded": "2020"
        }),
        
        # Plans tarifaires
        ("Plan Starter", "PricingPlan", {
            "price": "29€/mois",
            "users": "10",
            "features": "fonctionnalités de base"
        }),
        ("Plan Professional", "PricingPlan", {
            "price": "79€/mois", 
            "users": "50",
            "features": "fonctionnalités avancées et API"
        }),
        ("Plan Enterprise", "PricingPlan", {
            "price": "199€/mois",
            "users": "illimités",
            "features": "toutes fonctionnalités et support dédié"
        }),
        
        # Fonctionnalités
        ("Chat", "Feature", {
            "type": "communication",
            "real_time": True,
            "integrated": True
        }),
        ("Gestion de Projets", "Feature", {
            "type": "management",
            "visual": True,
            "intuitive": True
        }),
        ("Partage de Fichiers", "Feature", {
            "type": "storage",
            "secure": True,
            "cloud": True
        }),
        ("API", "Feature", {
            "type": "integration",
            "rest": True,
            "documentation": "complète"
        }),
        ("Tableaux de Bord", "Feature", {
            "type": "analytics",
            "advanced": True,
            "customizable": True
        }),
        
        # Intégrations
        ("Slack", "Integration", {
            "type": "chat",
            "native": True,
            "popular": True
        }),
        ("Microsoft Teams", "Integration", {
            "type": "collaboration",
            "native": True,
            "enterprise": True
        }),
        ("Google Workspace", "Integration", {
            "type": "productivity",
            "native": True,
            "cloud": True
        }),
        ("GitHub", "Integration", {
            "type": "development",
            "native": True,
            "version_control": True
        }),
        ("Trello", "Integration", {
            "type": "project_management",
            "native": True,
            "kanban": True
        }),
        
        # Support
        ("Support 24/7", "Service", {
            "availability": "24/7",
            "plans": ["Enterprise"],
            "type": "premium"
        }),
        ("Support Prioritaire", "Service", {
            "availability": "business_hours",
            "plans": ["Professional"],
            "type": "priority"
        }),
        ("Support Email", "Service", {
            "availability": "standard",
            "plans": ["Starter"],
            "type": "basic"
        }),
        
        # Secteurs d'activité
        ("Développement Logiciel", "Industry", {
            "type": "technology",
            "use_case": "gestion de projets agiles"
        }),
        ("Marketing", "Industry", {
            "type": "business",
            "use_case": "campagnes collaboratives"
        }),
        ("Éducation", "Industry", {
            "type": "education",
            "use_case": "projets étudiants"
        }),
        ("Consulting", "Industry", {
            "type": "services",
            "use_case": "gestion de clients"
        })
    ]
    
    # Ajouter les entités
    entity_ids = {}
    for name, entity_type, properties in entities:
        entity_id = graph_manager.add_entity(name, entity_type, properties)
        entity_ids[name] = entity_id
    
    print(f"✅ {len(entities)} entités ajoutées")
    
    print("🔧 Ajout des relations...")
    
    # Relations
    relations = [
        # Plans de TeamSquare
        ("TeamSquare", "HAS_PLAN", "Plan Starter"),
        ("TeamSquare", "HAS_PLAN", "Plan Professional"),
        ("TeamSquare", "HAS_PLAN", "Plan Enterprise"),
        
        # Fonctionnalités de TeamSquare
        ("TeamSquare", "HAS_FEATURE", "Chat"),
        ("TeamSquare", "HAS_FEATURE", "Gestion de Projets"),
        ("TeamSquare", "HAS_FEATURE", "Partage de Fichiers"),
        ("TeamSquare", "HAS_FEATURE", "API"),
        ("TeamSquare", "HAS_FEATURE", "Tableaux de Bord"),
        
        # Fonctionnalités par plan
        ("Plan Starter", "INCLUDES", "Chat"),
        ("Plan Starter", "INCLUDES", "Gestion de Projets"),
        ("Plan Starter", "INCLUDES", "Partage de Fichiers"),
        
        ("Plan Professional", "INCLUDES", "Chat"),
        ("Plan Professional", "INCLUDES", "Gestion de Projets"),
        ("Plan Professional", "INCLUDES", "Partage de Fichiers"),
        ("Plan Professional", "INCLUDES", "API"),
        ("Plan Professional", "INCLUDES", "Tableaux de Bord"),
        
        ("Plan Enterprise", "INCLUDES", "Chat"),
        ("Plan Enterprise", "INCLUDES", "Gestion de Projets"),
        ("Plan Enterprise", "INCLUDES", "Partage de Fichiers"),
        ("Plan Enterprise", "INCLUDES", "API"),
        ("Plan Enterprise", "INCLUDES", "Tableaux de Bord"),
        
        # Intégrations
        ("TeamSquare", "INTEGRATES_WITH", "Slack"),
        ("TeamSquare", "INTEGRATES_WITH", "Microsoft Teams"),
        ("TeamSquare", "INTEGRATES_WITH", "Google Workspace"),
        ("TeamSquare", "INTEGRATES_WITH", "GitHub"),
        ("TeamSquare", "INTEGRATES_WITH", "Trello"),
        
        # Support par plan
        ("Plan Starter", "INCLUDES_SUPPORT", "Support Email"),
        ("Plan Professional", "INCLUDES_SUPPORT", "Support Prioritaire"),
        ("Plan Enterprise", "INCLUDES_SUPPORT", "Support 24/7"),
        
        # Secteurs d'activité
        ("TeamSquare", "USED_BY", "Développement Logiciel"),
        ("TeamSquare", "USED_BY", "Marketing"),
        ("TeamSquare", "USED_BY", "Éducation"),
        ("TeamSquare", "USED_BY", "Consulting"),
        
        # Relations entre fonctionnalités
        ("API", "ENABLES", "Slack"),
        ("API", "ENABLES", "Microsoft Teams"),
        ("API", "ENABLES", "Google Workspace"),
        ("API", "ENABLES", "GitHub"),
        ("API", "ENABLES", "Trello"),
        
        # Relations entre plans (upgrade path)
        ("Plan Starter", "UPGRADES_TO", "Plan Professional"),
        ("Plan Professional", "UPGRADES_TO", "Plan Enterprise")
    ]
    
    # Ajouter les relations
    relation_count = 0
    for from_entity, relation_type, to_entity in relations:
        if graph_manager.add_relation(from_entity, relation_type, to_entity):
            relation_count += 1
    
    print(f"✅ {relation_count} relations ajoutées")
    
    # Afficher les statistiques
    stats = graph_manager.get_stats()
    print("\n📊 STATISTIQUES DU GRAPHE")
    print("-" * 30)
    for key, value in stats.items():
        print(f"{key}: {value}")
    
    # Exporter en JSON pour inspection
    export_file = "./data/graph_db/teamsquare_graph.json"
    if graph_manager.export_to_json(export_file):
        print(f"\n✅ Graphe exporté vers {export_file}")
    
    print("\n🎉 POPULATION DU GRAPHE TERMINÉE !")
    print("=" * 50)
    
    return graph_manager

def test_graph_search():
    """Test des fonctionnalités de recherche"""
    print("\n🧪 TEST DES FONCTIONNALITÉS DE RECHERCHE")
    print("-" * 50)
    
    graph_manager = NetworkXGraphManager()
    
    # Test de recherche d'entités
    test_queries = ["TeamSquare", "prix", "API", "Professional", "Slack"]
    
    for query in test_queries:
        print(f"\n🔍 Recherche: '{query}'")
        entities = graph_manager.search_entities(query, limit=3)
        for entity in entities:
            print(f"  - {entity['name']} ({entity['type']}) - Score: {entity['score']}")
        
        # Test de voisinage
        if entities:
            entity_name = entities[0]['name']
            print(f"\n🕸️ Voisinage de '{entity_name}':")
            neighborhood = graph_manager.get_entity_neighborhood(entity_name, depth=1)
            print(f"  - Nœuds: {len(neighborhood['nodes'])}")
            print(f"  - Relations: {len(neighborhood['relationships'])}")
            
            # Afficher quelques relations
            relations = graph_manager.get_entity_relations(entity_name)
            for relation in relations[:3]:
                print(f"  - {relation}")

if __name__ == "__main__":
    # Peupler le graphe
    graph_manager = populate_teamsquare_graph()
    
    # Tester les fonctionnalités
    test_graph_search()

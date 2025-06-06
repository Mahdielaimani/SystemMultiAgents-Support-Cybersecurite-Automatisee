#!/usr/bin/env python3
"""
Script de test d'accuracy pour l'agent RAG hybride (Vector + Graph)
"""

import sys
import os
import time
import json
import logging
from typing import Dict, List, Any, Tuple
from tabulate import tabulate
import matplotlib.pyplot as plt
from pathlib import Path
import numpy as np
from datetime import datetime

# Ajouter le répertoire racine au PYTHONPATH
sys.path.append(str(Path(__file__).parent.parent))

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("RAG_Accuracy_Test")

# Questions de test avec réponses attendues et mots-clés
TEST_QUESTIONS = [
    {
        "id": "prix-1",
        "category": "pricing",
        "question": "Quels sont les prix de TeamSquare ?",
        "expected_keywords": ["29€", "79€", "199€", "Starter", "Professional", "Enterprise"],
        "expected_answer_contains": ["plan", "prix", "tarif", "€"]
    },
    {
        "id": "prix-2",
        "category": "pricing",
        "question": "Combien coûte l'abonnement TeamSquare ?",
        "expected_keywords": ["29€", "79€", "199€", "mensuel", "mois"],
        "expected_answer_contains": ["plan", "prix", "tarif", "€"]
    },
    {
        "id": "fonctionnalités-1",
        "category": "features",
        "question": "Quelles sont les fonctionnalités de TeamSquare ?",
        "expected_keywords": ["collaboration", "temps réel", "projets", "fichiers", "sécurité"],
        "expected_answer_contains": ["fonctionnalité", "permet", "offre"]
    },
    {
        "id": "fonctionnalités-2",
        "category": "features",
        "question": "Qu'est-ce que TeamSquare permet de faire ?",
        "expected_keywords": ["collaboration", "équipe", "projets", "partage"],
        "expected_answer_contains": ["permet", "fonctionnalité", "plateforme"]
    },
    {
        "id": "api-1",
        "category": "technical",
        "question": "Comment fonctionne l'API de TeamSquare ?",
        "expected_keywords": ["API", "REST", "JSON", "endpoints", "documentation"],
        "expected_answer_contains": ["API", "développeur", "intégration"]
    },
    {
        "id": "api-2",
        "category": "technical",
        "question": "Comment intégrer TeamSquare avec mon application ?",
        "expected_keywords": ["API", "intégration", "webhook", "documentation"],
        "expected_answer_contains": ["API", "intégrer", "développeur"]
    },
    {
        "id": "sécurité-1",
        "category": "security",
        "question": "Comment TeamSquare protège mes données ?",
        "expected_keywords": ["chiffrement", "sécurité", "RGPD", "confidentialité"],
        "expected_answer_contains": ["sécurité", "données", "protection"]
    },
    {
        "id": "support-1",
        "category": "support",
        "question": "Comment contacter le support TeamSquare ?",
        "expected_keywords": ["support", "email", "téléphone", "ticket", "contact"],
        "expected_answer_contains": ["support", "contacter", "aide"]
    },
    {
        "id": "utilisateurs-1",
        "category": "users",
        "question": "Combien d'utilisateurs sont inclus dans chaque plan ?",
        "expected_keywords": ["10 utilisateurs", "50 utilisateurs", "illimités"],
        "expected_answer_contains": ["utilisateur", "plan", "inclus"]
    },
    {
        "id": "intégrations-1",
        "category": "integrations",
        "question": "Quelles intégrations sont disponibles avec TeamSquare ?",
        "expected_keywords": ["Slack", "Google", "Microsoft", "Trello", "intégration"],
        "expected_answer_contains": ["intégration", "connecter", "compatible"]
    }
]

def test_agent_vector_only():
    """Test l'agent avec Vector RAG uniquement"""
    try:
        from agents.support_agent.agentic_support_agent_rag_graph import AgenticSupportAgentRAGGraph
        
        # Créer une version de l'agent avec Graph RAG désactivé
        agent = AgenticSupportAgentRAGGraph()
        agent.graph_manager = None  # Désactiver Graph RAG
        
        return agent
    except Exception as e:
        logger.error(f"❌ Erreur initialisation agent Vector: {e}")
        return None

def test_agent_graph_only():
    """Test l'agent avec Graph RAG uniquement"""
    try:
        from agents.support_agent.agentic_support_agent_rag_graph import AgenticSupportAgentRAGGraph
        
        # Créer une version de l'agent avec Vector RAG désactivé
        agent = AgenticSupportAgentRAGGraph()
        agent.embedding_model = None  # Désactiver Vector RAG
        agent.collection = None
        
        return agent
    except Exception as e:
        logger.error(f"❌ Erreur initialisation agent Graph: {e}")
        return None

def test_agent_hybrid():
    """Test l'agent avec RAG hybride (Vector + Graph)"""
    try:
        from agents.support_agent.agentic_support_agent_rag_graph import AgenticSupportAgentRAGGraph
        
        # Créer une version de l'agent avec les deux RAG activés
        agent = AgenticSupportAgentRAGGraph()
        
        return agent
    except Exception as e:
        logger.error(f"❌ Erreur initialisation agent Hybride: {e}")
        return None

def calculate_metrics(response: str, question_data: Dict) -> Dict:
    """Calcule les métriques pour une réponse"""
    metrics = {
        "keyword_recall": 0.0,
        "content_precision": 0.0,
        "relevance_score": 0.0
    }
    
    # Calcul du rappel des mots-clés
    keywords_found = 0
    for keyword in question_data["expected_keywords"]:
        if keyword.lower() in response.lower():
            keywords_found += 1
    
    if question_data["expected_keywords"]:
        metrics["keyword_recall"] = keywords_found / len(question_data["expected_keywords"])
    
    # Calcul de la précision du contenu
    content_matches = 0
    for content in question_data["expected_answer_contains"]:
        if content.lower() in response.lower():
            content_matches += 1
    
    if question_data["expected_answer_contains"]:
        metrics["content_precision"] = content_matches / len(question_data["expected_answer_contains"])
    
    # Score de pertinence global
    metrics["relevance_score"] = (metrics["keyword_recall"] + metrics["content_precision"]) / 2
    
    return metrics

def run_accuracy_test():
    """Exécute le test d'accuracy complet"""
    print("\n🧪 TEST D'ACCURACY AGENT RAG HYBRIDE")
    print("=" * 60)
    
    # Initialiser les agents
    print("\n📊 INITIALISATION DES AGENTS")
    print("-" * 40)
    
    vector_agent = test_agent_vector_only()
    graph_agent = test_agent_graph_only()
    hybrid_agent = test_agent_hybrid()
    
    if not vector_agent:
        print("❌ Agent Vector non disponible")
    else:
        print("✅ Agent Vector initialisé")
    
    if not graph_agent:
        print("❌ Agent Graph non disponible")
    else:
        print("✅ Agent Graph initialisé")
    
    if not hybrid_agent:
        print("❌ Agent Hybride non disponible")
    else:
        print("✅ Agent Hybride initialisé")
    
    # Résultats
    results = {
        "vector": [],
        "graph": [],
        "hybrid": []
    }
    
    # Exécuter les tests
    print("\n📝 EXÉCUTION DES TESTS")
    print("-" * 40)
    
    for question_data in TEST_QUESTIONS:
        question_id = question_data["id"]
        category = question_data["category"]
        question = question_data["question"]
        
        print(f"\n🔍 Test {question_id}: '{question}' (Catégorie: {category})")
        
        # Test Vector
        if vector_agent:
            start_time = time.time()
            vector_response = vector_agent.process_query(question)
            vector_time = time.time() - start_time
            
            vector_metrics = calculate_metrics(vector_response, question_data)
            vector_metrics["response_time"] = vector_time
            vector_metrics["response"] = vector_response[:100] + "..." if len(vector_response) > 100 else vector_response
            
            results["vector"].append({
                "question_id": question_id,
                "category": category,
                "metrics": vector_metrics
            })
            
            print(f"  ↳ Vector: {vector_metrics['relevance_score']:.2f} score, {vector_time:.2f}s")
        
        # Test Graph
        if graph_agent:
            start_time = time.time()
            graph_response = graph_agent.process_query(question)
            graph_time = time.time() - start_time
            
            graph_metrics = calculate_metrics(graph_response, question_data)
            graph_metrics["response_time"] = graph_time
            graph_metrics["response"] = graph_response[:100] + "..." if len(graph_response) > 100 else graph_response
            
            results["graph"].append({
                "question_id": question_id,
                "category": category,
                "metrics": graph_metrics
            })
            
            print(f"  ↳ Graph: {graph_metrics['relevance_score']:.2f} score, {graph_time:.2f}s")
        
        # Test Hybrid
        if hybrid_agent:
            start_time = time.time()
            hybrid_response = hybrid_agent.process_query(question)
            hybrid_time = time.time() - start_time
            
            hybrid_metrics = calculate_metrics(hybrid_response, question_data)
            hybrid_metrics["response_time"] = hybrid_time
            hybrid_metrics["response"] = hybrid_response[:100] + "..." if len(hybrid_response) > 100 else hybrid_response
            
            results["hybrid"].append({
                "question_id": question_id,
                "category": category,
                "metrics": hybrid_metrics
            })
            
            print(f"  ↳ Hybrid: {hybrid_metrics['relevance_score']:.2f} score, {hybrid_time:.2f}s")
    
    # Générer le rapport
    generate_report(results)
    
    # Générer les graphiques
    generate_charts(results)
    
    print("\n✅ TEST D'ACCURACY TERMINÉ")
    print("=" * 60)

def generate_report(results: Dict):
    """Génère un rapport détaillé des résultats"""
    print("\n📊 RAPPORT D'ACCURACY")
    print("-" * 40)
    
    # Tableau comparatif
    table_data = []
    headers = ["Question ID", "Catégorie", "Vector Score", "Graph Score", "Hybrid Score", "Meilleur"]
    
    for i, question_data in enumerate(TEST_QUESTIONS):
        question_id = question_data["id"]
        category = question_data["category"]
        
        vector_score = results["vector"][i]["metrics"]["relevance_score"] if results["vector"] else 0
        graph_score = results["graph"][i]["metrics"]["relevance_score"] if results["graph"] else 0
        hybrid_score = results["hybrid"][i]["metrics"]["relevance_score"] if results["hybrid"] else 0
        
        # Déterminer le meilleur
        scores = [
            ("Vector", vector_score),
            ("Graph", graph_score),
            ("Hybrid", hybrid_score)
        ]
        best = max(scores, key=lambda x: x[1])
        
        table_data.append([
            question_id,
            category,
            f"{vector_score:.2f}",
            f"{graph_score:.2f}",
            f"{hybrid_score:.2f}",
            f"{best[0]} ({best[1]:.2f})"
        ])
    
    print(tabulate(table_data, headers=headers, tablefmt="grid"))
    
    # Moyennes par catégorie
    print("\n📈 MOYENNES PAR CATÉGORIE")
    print("-" * 40)
    
    categories = set(q["category"] for q in TEST_QUESTIONS)
    category_table = []
    
    for category in categories:
        vector_scores = [r["metrics"]["relevance_score"] for i, r in enumerate(results["vector"]) 
                        if TEST_QUESTIONS[i]["category"] == category] if results["vector"] else []
        
        graph_scores = [r["metrics"]["relevance_score"] for i, r in enumerate(results["graph"]) 
                       if TEST_QUESTIONS[i]["category"] == category] if results["graph"] else []
        
        hybrid_scores = [r["metrics"]["relevance_score"] for i, r in enumerate(results["hybrid"]) 
                        if TEST_QUESTIONS[i]["category"] == category] if results["hybrid"] else []
        
        vector_avg = sum(vector_scores) / len(vector_scores) if vector_scores else 0
        graph_avg = sum(graph_scores) / len(graph_scores) if graph_scores else 0
        hybrid_avg = sum(hybrid_scores) / len(hybrid_scores) if hybrid_scores else 0
        
        category_table.append([
            category,
            f"{vector_avg:.2f}",
            f"{graph_avg:.2f}",
            f"{hybrid_avg:.2f}"
        ])
    
    print(tabulate(category_table, headers=["Catégorie", "Vector Avg", "Graph Avg", "Hybrid Avg"], tablefmt="grid"))
    
    # Moyennes globales
    print("\n🏆 MOYENNES GLOBALES")
    print("-" * 40)
    
    vector_avg = sum(r["metrics"]["relevance_score"] for r in results["vector"]) / len(results["vector"]) if results["vector"] else 0
    graph_avg = sum(r["metrics"]["relevance_score"] for r in results["graph"]) / len(results["graph"]) if results["graph"] else 0
    hybrid_avg = sum(r["metrics"]["relevance_score"] for r in results["hybrid"]) / len(results["hybrid"]) if results["hybrid"] else 0
    
    vector_time_avg = sum(r["metrics"]["response_time"] for r in results["vector"]) / len(results["vector"]) if results["vector"] else 0
    graph_time_avg = sum(r["metrics"]["response_time"] for r in results["graph"]) / len(results["graph"]) if results["graph"] else 0
    hybrid_time_avg = sum(r["metrics"]["response_time"] for r in results["hybrid"]) / len(results["hybrid"]) if results["hybrid"] else 0
    
    global_table = [
        ["Score moyen", f"{vector_avg:.2f}", f"{graph_avg:.2f}", f"{hybrid_avg:.2f}"],
        ["Temps moyen (s)", f"{vector_time_avg:.2f}", f"{graph_time_avg:.2f}", f"{hybrid_time_avg:.2f}"]
    ]
    
    print(tabulate(global_table, headers=["Métrique", "Vector", "Graph", "Hybrid"], tablefmt="grid"))
    
    # Sauvegarder les résultats
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = f"rag_accuracy_results_{timestamp}.json"
    
    with open(results_file, "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\n💾 Résultats sauvegardés dans {results_file}")

def generate_charts(results: Dict):
    """Génère des graphiques pour visualiser les résultats"""
    try:
        # Créer le dossier pour les graphiques
        charts_dir = "accuracy_charts"
        os.makedirs(charts_dir, exist_ok=True)
        
        # Données pour les graphiques
        categories = [q["category"] for q in TEST_QUESTIONS]
        question_ids = [q["id"] for q in TEST_QUESTIONS]
        
        vector_scores = [r["metrics"]["relevance_score"] for r in results["vector"]] if results["vector"] else [0] * len(TEST_QUESTIONS)
        graph_scores = [r["metrics"]["relevance_score"] for r in results["graph"]] if results["graph"] else [0] * len(TEST_QUESTIONS)
        hybrid_scores = [r["metrics"]["relevance_score"] for r in results["hybrid"]] if results["hybrid"] else [0] * len(TEST_QUESTIONS)
        
        vector_times = [r["metrics"]["response_time"] for r in results["vector"]] if results["vector"] else [0] * len(TEST_QUESTIONS)
        graph_times = [r["metrics"]["response_time"] for r in results["graph"]] if results["graph"] else [0] * len(TEST_QUESTIONS)
        hybrid_times = [r["metrics"]["response_time"] for r in results["hybrid"]] if results["hybrid"] else [0] * len(TEST_QUESTIONS)
        
        # 1. Graphique des scores par question
        plt.figure(figsize=(12, 6))
        x = np.arange(len(question_ids))
        width = 0.25
        
        plt.bar(x - width, vector_scores, width, label='Vector')
        plt.bar(x, graph_scores, width, label='Graph')
        plt.bar(x + width, hybrid_scores, width, label='Hybrid')
        
        plt.xlabel('Questions')
        plt.ylabel('Score de pertinence')
        plt.title('Comparaison des scores par question')
        plt.xticks(x, question_ids, rotation=45)
        plt.legend()
        plt.tight_layout()
        plt.savefig(f"{charts_dir}/scores_by_question.png")
        
        # 2. Graphique des temps de réponse
        plt.figure(figsize=(12, 6))
        
        plt.bar(x - width, vector_times, width, label='Vector')
        plt.bar(x, graph_times, width, label='Graph')
        plt.bar(x + width, hybrid_times, width, label='Hybrid')
        
        plt.xlabel('Questions')
        plt.ylabel('Temps de réponse (s)')
        plt.title('Comparaison des temps de réponse')
        plt.xticks(x, question_ids, rotation=45)
        plt.legend()
        plt.tight_layout()
        plt.savefig(f"{charts_dir}/response_times.png")
        
        # 3. Graphique des moyennes par catégorie
        unique_categories = list(set(categories))
        category_scores = {cat: {"vector": [], "graph": [], "hybrid": []} for cat in unique_categories}
        
        for i, cat in enumerate(categories):
            if i < len(vector_scores):
                category_scores[cat]["vector"].append(vector_scores[i])
            if i < len(graph_scores):
                category_scores[cat]["graph"].append(graph_scores[i])
            if i < len(hybrid_scores):
                category_scores[cat]["hybrid"].append(hybrid_scores[i])
        
        vector_avgs = [np.mean(category_scores[cat]["vector"]) if category_scores[cat]["vector"] else 0 for cat in unique_categories]
        graph_avgs = [np.mean(category_scores[cat]["graph"]) if category_scores[cat]["graph"] else 0 for cat in unique_categories]
        hybrid_avgs = [np.mean(category_scores[cat]["hybrid"]) if category_scores[cat]["hybrid"] else 0 for cat in unique_categories]
        
        plt.figure(figsize=(12, 6))
        x = np.arange(len(unique_categories))
        
        plt.bar(x - width, vector_avgs, width, label='Vector')
        plt.bar(x, graph_avgs, width, label='Graph')
        plt.bar(x + width, hybrid_avgs, width, label='Hybrid')
        
        plt.xlabel('Catégories')
        plt.ylabel('Score moyen')
        plt.title('Scores moyens par catégorie')
        plt.xticks(x, unique_categories, rotation=45)
        plt.legend()
        plt.tight_layout()
        plt.savefig(f"{charts_dir}/scores_by_category.png")
        
        print(f"\n📊 Graphiques générés dans le dossier {charts_dir}/")
        
    except Exception as e:
        logger.error(f"❌ Erreur génération graphiques: {e}")
        print(f"❌ Erreur génération graphiques: {e}")

if __name__ == "__main__":
    run_accuracy_test()

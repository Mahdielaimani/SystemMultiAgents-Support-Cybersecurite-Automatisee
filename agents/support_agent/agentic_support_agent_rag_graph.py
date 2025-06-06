"""
Agent Support Agentic avec RAG hybride : Vector (ChromaDB) + Graph (Neo4j) + Gemini/Mistral
"""

import logging
import os
import sys
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
import json
import re

# Ajouter le répertoire racine au path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Imports pour RAG Vector
try:
    from sentence_transformers import SentenceTransformer
    import chromadb
    from chromadb.config import Settings
    CHROMADB_AVAILABLE = True
except ImportError:
    print("⚠️  ChromaDB non disponible")
    CHROMADB_AVAILABLE = False

# Imports pour RAG Graph
try:
    from core.graph_manager import KnowledgeGraphManager
    GRAPH_AVAILABLE = True
except ImportError:
    print("⚠️  KnowledgeGraphManager non disponible")
    GRAPH_AVAILABLE = False

# Imports pour LLM hybride Gemini
try:
    from utils.hybrid_llm_manager_gemini import HybridLLMManagerGemini
    HYBRID_LLM_AVAILABLE = True
except ImportError:
    print("⚠️  Gestionnaire LLM hybride Gemini non disponible")
    HYBRID_LLM_AVAILABLE = False

@dataclass
class RAGResult:
    """Résultat combiné Vector + Graph RAG"""
    vector_results: List[Dict[str, Any]]
    graph_results: List[Dict[str, Any]]
    combined_context: str
    confidence_score: float

class AgenticSupportAgentRAGGraph:
    """
    Agent Support avec RAG hybride (Vector + Graph) + Gemini/Mistral
    """
    
    def __init__(self):
        self.logger = self._setup_logger()
        
        # Initialisation des composants
        self.embedding_model = None
        self.chroma_client = None
        self.collection = None
        self.graph_manager = None
        self.llm_manager = None
        
        # Patterns de détection
        self.greeting_patterns = [
            r'\b(bonjour|salut|hello|hi|bonsoir|hey|coucou)\b',
            r'\b(comment ça va|ça va)\b'
        ]
        
        self.pricing_patterns = [
            r'\b(prix|tarif|coût|combien|pricing)\b',
            r'\b(donner.*prix|montrer.*prix|voir.*prix)\b',
            r'\b(plan|abonnement|forfait)\b'
        ]
        
        self.teamsquare_patterns = [
            r'\b(teamsquare|team square)\b',
            r'\b(qu.*est.*teamsquare|c.*est.*quoi.*teamsquare)\b',
            r'\b(fonctionnalité|feature|service|api|intégration)\b'
        ]
        
        self._initialize_components()
    
    def _setup_logger(self):
        """Configure le logger"""
        logger = logging.getLogger("AgenticSupportAgentRAGGraph")
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def _initialize_components(self):
        """Initialise tous les composants RAG hybride"""
        try:
            # 1. Gestionnaire LLM hybride Gemini
            if HYBRID_LLM_AVAILABLE:
                self.logger.info("🔄 Initialisation du gestionnaire LLM hybride Gemini...")
                self.llm_manager = HybridLLMManagerGemini()
                self.logger.info(f"✅ LLM hybride Gemini initialisé - Provider: {self.llm_manager.current_provider}")
            
            # 2. Modèle d'embedding pour Vector RAG
            if CHROMADB_AVAILABLE:
                self.logger.info("🔄 Chargement du modèle BGE-Large-EN...")
                try:
                    self.embedding_model = SentenceTransformer('BAAI/bge-large-en-v1.5')
                    self.logger.info("✅ Modèle BGE-Large-EN chargé")
                except Exception as e:
                    self.logger.warning(f"⚠️  Erreur chargement BGE: {e}")
                
                # 3. ChromaDB pour Vector RAG
                self.logger.info("🔄 Connexion à ChromaDB...")
                try:
                    chroma_path = "./data/vector_db/chroma_db"
                    os.makedirs(chroma_path, exist_ok=True)
                    
                    self.chroma_client = chromadb.PersistentClient(
                        path=chroma_path,
                        settings=Settings(anonymized_telemetry=False)
                    )
                    
                    try:
                        self.collection = self.chroma_client.get_collection("knowledge_base")
                        self.logger.info("✅ Collection ChromaDB trouvée")
                    except:
                        self.logger.warning("⚠️  Collection ChromaDB non trouvée")
                        
                except Exception as e:
                    self.logger.error(f"❌ Erreur ChromaDB: {e}")
            
            # 4. Neo4j pour Graph RAG
            if GRAPH_AVAILABLE:
                self.logger.info("🔄 Initialisation du gestionnaire de graphe Neo4j...")
                try:
                    self.graph_manager = KnowledgeGraphManager()
                    self.logger.info("✅ Gestionnaire de graphe Neo4j initialisé")
                except Exception as e:
                    self.logger.warning(f"⚠️  Erreur Neo4j: {e}")
                    self.graph_manager = None
                
        except Exception as e:
            self.logger.error(f"❌ Erreur initialisation: {e}")
    
    def process_query(self, query: str) -> str:
        """
        Traite une requête avec RAG hybride (Vector + Graph) + LLM
        """
        self.logger.info(f"🔍 Traitement requête RAG hybride: {query[:50]}...")
        
        try:
            # 1. Détection du type de requête
            query_type = self._detect_query_type(query)
            
            # 2. RAG hybride : Vector + Graph
            rag_result = self._hybrid_rag_search(query, query_type)
            
            # 3. Génération avec LLM hybride
            if self.llm_manager and query_type != "greeting":
                response = self._generate_with_llm(query, rag_result, query_type)
            else:
                response = self._generate_fallback(query, rag_result.combined_context, query_type)
            
            # 4. Mise à jour du graphe de connaissances
            self._update_knowledge_graph(query, response, query_type)
            
            self.logger.info(f"✅ Réponse générée ({len(response)} chars) - Confiance: {rag_result.confidence_score:.2f}")
            return response
            
        except Exception as e:
            self.logger.error(f"❌ Erreur traitement requête: {e}")
            return "Désolé, j'ai rencontré un problème technique. Pouvez-vous reformuler votre question ?"
    
    def _hybrid_rag_search(self, query: str, query_type: str) -> RAGResult:
        """
        Recherche hybride : Vector RAG (ChromaDB) + Graph RAG (Neo4j)
        """
        self.logger.info("🔍 Recherche RAG hybride (Vector + Graph)...")
        
        # Résultats par défaut
        vector_results = []
        graph_results = []
        
        # 1. Vector RAG avec ChromaDB
        if self.embedding_model and self.collection:
            try:
                self.logger.info("📊 Recherche vectorielle...")
                query_embedding = self.embedding_model.encode([query]).tolist()[0]
                
                chroma_results = self.collection.query(
                    query_embeddings=query_embedding,
                    n_results=5,
                    include=['documents', 'metadatas', 'distances']
                )
                
                if chroma_results['documents'] and chroma_results['documents'][0]:
                    for doc, metadata, distance in zip(
                        chroma_results['documents'][0],
                        chroma_results['metadatas'][0] or [{}] * len(chroma_results['documents'][0]),
                        chroma_results['distances'][0]
                    ):
                        if distance < 0.7:  # Seuil de pertinence
                            vector_results.append({
                                'content': doc,
                                'metadata': metadata,
                                'score': 1 - distance,
                                'source': 'vector_db'
                            })
                
                self.logger.info(f"📊 Trouvé {len(vector_results)} résultats vectoriels")
                
            except Exception as e:
                self.logger.error(f"❌ Erreur recherche vectorielle: {e}")
        
        # 2. Graph RAG avec Neo4j
        if self.graph_manager:
            try:
                self.logger.info("🕸️ Recherche dans le graphe...")
                
                # Recherche d'entités similaires
                graph_entities = self.graph_manager.search_entities(query, limit=3)
                
                for entity in graph_entities:
                    # Récupérer le voisinage de chaque entité
                    neighborhood = self.graph_manager.get_entity_neighborhood(
                        entity['name'], depth=2
                    )
                    
                    if neighborhood['nodes']:
                        graph_results.append({
                            'entity': entity['name'],
                            'type': entity['type'],
                            'score': entity.get('score', 0.5),
                            'neighborhood': neighborhood,
                            'source': 'knowledge_graph'
                        })
                
                self.logger.info(f"🕸️ Trouvé {len(graph_results)} résultats graphiques")
                
            except Exception as e:
                self.logger.error(f"❌ Erreur recherche graphique: {e}")
        
        # 3. Combinaison des contextes
        combined_context = self._combine_contexts(vector_results, graph_results, query_type)
        
        # 4. Calcul du score de confiance
        confidence_score = self._calculate_confidence(vector_results, graph_results)
        
        return RAGResult(
            vector_results=vector_results,
            graph_results=graph_results,
            combined_context=combined_context,
            confidence_score=confidence_score
        )
    
    def _combine_contexts(self, vector_results: List[Dict], graph_results: List[Dict], query_type: str) -> str:
        """Combine les contextes vectoriel et graphique"""
        
        context_parts = []
        
        # Contexte par défaut
        default_context = self._get_default_context(query_type)
        context_parts.append(f"INFORMATIONS DE BASE:\n{default_context}")
        
        # Contexte vectoriel
        if vector_results:
            vector_context = "\n".join([result['content'] for result in vector_results[:3]])
            context_parts.append(f"DOCUMENTS PERTINENTS:\n{vector_context}")
        
        # Contexte graphique
        if graph_results:
            graph_context = []
            for result in graph_results[:2]:
                entity_info = f"Entité: {result['entity']} (Type: {result['type']})"
                
                # Ajouter les relations
                neighborhood = result.get('neighborhood', {})
                if neighborhood.get('relationships'):
                    relations = []
                    for rel in neighborhood['relationships'][:3]:
                        relations.append(f"- {rel['type']}")
                    entity_info += f"\nRelations: {', '.join(relations)}"
                
                graph_context.append(entity_info)
            
            if graph_context:
                context_parts.append(f"RELATIONS DANS LE GRAPHE:\n" + "\n\n".join(graph_context))
        
        return "\n\n".join(context_parts)
    
    def _calculate_confidence(self, vector_results: List[Dict], graph_results: List[Dict]) -> float:
        """Calcule un score de confiance basé sur les résultats RAG"""
        
        confidence = 0.0
        
        # Score vectoriel
        if vector_results:
            avg_vector_score = sum(r['score'] for r in vector_results) / len(vector_results)
            confidence += avg_vector_score * 0.6
        
        # Score graphique
        if graph_results:
            avg_graph_score = sum(r['score'] for r in graph_results) / len(graph_results)
            confidence += avg_graph_score * 0.4
        
        # Bonus si les deux sources sont disponibles
        if vector_results and graph_results:
            confidence += 0.1
        
        return min(confidence, 1.0)
    
    def _update_knowledge_graph(self, query: str, response: str, query_type: str):
        """Met à jour le graphe de connaissances avec l'interaction"""
        
        if not self.graph_manager:
            return
        
        try:
            self.logger.info("🕸️ Mise à jour du graphe de connaissances...")
            
            # Utiliser la méthode existante du graph_manager
            self.graph_manager.update_with_interaction(
                query=query,
                response=response,
                agent_type="agentic_rag_graph"
            )
            
            self.logger.info("✅ Graphe de connaissances mis à jour")
            
        except Exception as e:
            self.logger.error(f"❌ Erreur mise à jour graphe: {e}")
    
    def _detect_query_type(self, query: str) -> str:
        """Détecte le type de requête"""
        query_lower = query.lower()
        
        if any(re.search(pattern, query_lower, re.IGNORECASE) for pattern in self.greeting_patterns):
            return "greeting"
        elif any(re.search(pattern, query_lower, re.IGNORECASE) for pattern in self.pricing_patterns):
            return "pricing"
        elif any(re.search(pattern, query_lower, re.IGNORECASE) for pattern in self.teamsquare_patterns):
            return "teamsquare"
        else:
            return "general"
    
    def _get_default_context(self, query_type: str) -> str:
        """Contexte par défaut basé sur le type de requête"""
        
        if query_type == "pricing":
            return """TeamSquare propose trois plans tarifaires :
- Plan Starter : 29€/mois (jusqu'à 10 utilisateurs, fonctionnalités de base)
- Plan Professional : 79€/mois (jusqu'à 50 utilisateurs, fonctionnalités avancées, API)
- Plan Enterprise : 199€/mois (utilisateurs illimités, toutes fonctionnalités, support dédié)"""
        
        elif query_type == "teamsquare":
            return """TeamSquare est une plateforme de collaboration moderne qui offre :
- Collaboration en temps réel avec chat intégré
- Gestion de projets intuitive et visuelle
- Partage de fichiers sécurisé
- Tableaux de bord et analytics avancés
- API complète pour intégrations
- Sécurité de niveau entreprise"""
        
        else:
            return "Je suis un assistant spécialisé dans TeamSquare, une plateforme de collaboration pour équipes."
    
    def _generate_with_llm(self, query: str, rag_result: RAGResult, query_type: str) -> str:
        """Génère une réponse avec le gestionnaire LLM hybride"""
        
        system_prompt = f"""Tu es un assistant support intelligent pour TeamSquare, une plateforme de collaboration.

CONTEXTE RAG HYBRIDE (Vector + Graph) :
{rag_result.combined_context}

SCORE DE CONFIANCE : {rag_result.confidence_score:.2f}
SOURCES DISPONIBLES : {len(rag_result.vector_results)} documents + {len(rag_result.graph_results)} entités graphiques

INSTRUCTIONS :
- Réponds de manière naturelle et amicale en français
- Utilise prioritairement le contexte fourni
- Si le score de confiance est élevé (>0.7), sois confiant dans ta réponse
- Si le score est moyen (0.4-0.7), mentionne que tu as des informations partielles
- Si le score est faible (<0.4), sois honnête sur les limitations
- Reste focalisé sur TeamSquare et ses services
- Sois concis mais informatif (maximum 300 mots)

STYLE :
- Conversationnel et humain
- Professionnel mais accessible
- Utilise des emojis avec parcimonie"""
        
        try:
            response = self.llm_manager.generate(query, system_prompt)
            
            # Vérifier la qualité de la réponse
            if len(response) < 20 or "erreur" in response.lower():
                return self._generate_fallback(query, rag_result.combined_context, query_type)
            
            return response
            
        except Exception as e:
            self.logger.error(f"❌ Erreur génération LLM: {e}")
            return self._generate_fallback(query, rag_result.combined_context, query_type)
    
    def _generate_fallback(self, query: str, context: str, query_type: str) -> str:
        """Génération de fallback sans LLM"""
        
        if query_type == "greeting":
            return "Bonjour ! Je suis votre assistant TeamSquare avec recherche avancée. Comment puis-je vous aider aujourd'hui ?"
        
        elif query_type == "pricing":
            return """Voici nos tarifs TeamSquare :

**Plan Starter** - 29€/mois
• Jusqu'à 10 utilisateurs
• Fonctionnalités de base
• Support email

**Plan Professional** - 79€/mois  
• Jusqu'à 50 utilisateurs
• Fonctionnalités avancées
• API incluse
• Support prioritaire

**Plan Enterprise** - 199€/mois
• Utilisateurs illimités
• Toutes les fonctionnalités
• Support dédié 24/7
• Personnalisations

Quel plan vous intéresse le plus ?"""
        
        elif query_type == "teamsquare":
            return """TeamSquare est une plateforme de collaboration moderne qui permet aux équipes de :

🚀 **Collaborer en temps réel** avec chat intégré
📊 **Gérer des projets** de manière intuitive et visuelle  
📁 **Partager des fichiers** en toute sécurité
📈 **Analyser les performances** avec des tableaux de bord
🔌 **Intégrer facilement** grâce à notre API complète
🛡️ **Sécuriser les données** avec un niveau entreprise

Que souhaitez-vous savoir de plus sur TeamSquare ?"""
        
        else:
            if context and len(context) > 100:
                return f"Basé sur mes recherches avancées :\n\n{context[:500]}...\n\nAvez-vous des questions plus spécifiques ?"
            else:
                return f"Je comprends votre question sur '{query}'. Pouvez-vous être plus spécifique ? Je peux vous aider avec les prix, fonctionnalités, et services TeamSquare."

# Test rapide
def test_agent():
    """Test de l'agent RAG hybride"""
    print("🧪 TEST AGENT RAG HYBRIDE (Vector + Graph)")
    print("-" * 60)
    
    agent = AgenticSupportAgentRAGGraph()
    
    test_queries = [
        "bonjour",
        "donner moi les prix",
        "qu'est-ce que TeamSquare ?",
        "comment fonctionne l'API TeamSquare ?",
        "quelles sont les intégrations disponibles ?"
    ]
    
    for query in test_queries:
        print(f"\n🔍 Test: {query}")
        response = agent.process_query(query)
        print(f"📝 Réponse: {response[:200]}...")

if __name__ == "__main__":
    test_agent()

"""
Agent de support avec RAG hybride utilisant LangChain pour les prompts
"""
import logging
import time
import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
import chromadb
from sentence_transformers import SentenceTransformer
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from utils.hybrid_llm_manager_gemini import HybridLLMManagerGemini
from core.networkx_graph_manager import NetworkXGraphManager
from agents.support_agent.langchain_prompt_manager import LangChainPromptManager
from config.settings import Settings

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ConversationMemory:
    """Structure pour stocker la mémoire conversationnelle"""
    session_id: str
    messages: List[Dict[str, Any]]
    context: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'session_id': self.session_id,
            'messages': self.messages,
            'context': self.context,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class AgenticSupportAgentLangChain:
    """Agent de support avec RAG hybride et LangChain pour les prompts"""
    
    def __init__(self):
        self.settings = Settings()
        self.llm_manager = None
        self.embedding_model = None
        self.chroma_client = None
        self.collection = None
        self.graph_manager = None
        self.memory_store = {}
        self.memory_file = "data/memory/conversations.json"
        self.prompt_manager = LangChainPromptManager()
        
        # Statistiques
        self.stats = {
            'total_queries': 0,
            'vector_hits': 0,
            'graph_hits': 0,
            'memory_hits': 0,
            'avg_confidence': 0.0,
            'avg_response_time': 0.0
        }
        
        self.last_confidence_score = 0.0
        self._initialize()
    
    def _initialize(self):
        """Initialise tous les composants"""
        try:
            logger.info("🔄 Initialisation de l'agent LangChain...")
            
            # 1. LLM Manager
            self._init_llm_manager()
            
            # 2. Modèle d'embeddings
            self._init_embedding_model()
            
            # 3. ChromaDB
            self._init_chromadb()
            
            # 4. NetworkX Graph Manager
            self._init_networkx_graph()
            
            # 5. Memory System
            self._init_memory_system()
            
            logger.info("✅ Agent LangChain initialisé avec succès")
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de l'initialisation: {e}")
            raise
    
    def _init_llm_manager(self):
        """Initialise le gestionnaire LLM hybride"""
        try:
            logger.info("🔄 Initialisation du gestionnaire LLM hybride...")
            self.llm_manager = HybridLLMManagerGemini()
            logger.info(f"✅ LLM hybride initialisé - Provider: {self.llm_manager.current_provider}")
        except Exception as e:
            logger.error(f"❌ Erreur LLM Manager: {e}")
            self.llm_manager = None
    
    def _init_embedding_model(self):
        """Initialise le modèle d'embeddings"""
        try:
            logger.info("🔄 Chargement du modèle BGE-Large-EN...")
            self.embedding_model = SentenceTransformer('BAAI/bge-large-en-v1.5')
            logger.info("✅ Modèle BGE-Large-EN chargé")
        except Exception as e:
            logger.error(f"❌ Erreur modèle embeddings: {e}")
            self.embedding_model = None
    
    def _init_chromadb(self):
        """Initialise ChromaDB"""
        try:
            logger.info("🔄 Connexion à ChromaDB...")
            self.chroma_client = chromadb.PersistentClient(path="./data/vector_db/chroma_db")
            
            try:
                self.collection = self.chroma_client.get_collection("teamsquare_knowledge")
                logger.info("✅ Collection ChromaDB trouvée")
            except:
                logger.warning("⚠️  Collection ChromaDB non trouvée, création...")
                self.collection = self.chroma_client.create_collection("teamsquare_knowledge")
                logger.info("✅ Collection ChromaDB créée")
                
        except Exception as e:
            logger.error(f"❌ Erreur ChromaDB: {e}")
            self.chroma_client = None
            self.collection = None
    
    def _init_networkx_graph(self):
        """Initialise le gestionnaire de graphe NetworkX"""
        try:
            logger.info("🔄 Initialisation du gestionnaire NetworkX...")
            self.graph_manager = NetworkXGraphManager()
            stats = self.graph_manager.get_stats()
            logger.info(f"✅ NetworkX initialisé - {stats['entities_count']} entités, {stats['relations_count']} relations")
        except Exception as e:
            logger.error(f"❌ Erreur NetworkX: {e}")
            self.graph_manager = None
    
    def _init_memory_system(self):
        """Initialise le système de mémoire"""
        try:
            logger.info("🔄 Initialisation du système de mémoire...")
            
            os.makedirs(os.path.dirname(self.memory_file), exist_ok=True)
            
            if os.path.exists(self.memory_file):
                with open(self.memory_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for session_id, conv_data in data.items():
                        self.memory_store[session_id] = ConversationMemory(
                            session_id=conv_data['session_id'],
                            messages=conv_data['messages'],
                            context=conv_data['context'],
                            created_at=datetime.fromisoformat(conv_data['created_at']),
                            updated_at=datetime.fromisoformat(conv_data['updated_at'])
                        )
            
            logger.info(f"✅ Système de mémoire initialisé - {len(self.memory_store)} conversations chargées")
            
        except Exception as e:
            logger.error(f"❌ Erreur système de mémoire: {e}")
    
    def _save_memory(self):
        """Sauvegarde la mémoire sur disque"""
        try:
            data = {session_id: conv.to_dict() for session_id, conv in self.memory_store.items()}
            with open(self.memory_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"❌ Erreur sauvegarde mémoire: {e}")
    
    def _get_or_create_memory(self, session_id: str) -> ConversationMemory:
        """Récupère ou crée une mémoire conversationnelle"""
        if session_id not in self.memory_store:
            self.memory_store[session_id] = ConversationMemory(
                session_id=session_id,
                messages=[],
                context={},
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
        return self.memory_store[session_id]
    
    def _update_memory(self, session_id: str, query: str, response: str, context: Dict[str, Any]):
        """Met à jour la mémoire conversationnelle"""
        try:
            memory = self._get_or_create_memory(session_id)
            
            memory.messages.append({
                'timestamp': datetime.now().isoformat(),
                'query': query,
                'response': response,
                'context': context
            })
            
            if len(memory.messages) > 50:
                memory.messages = memory.messages[-50:]
            
            memory.context.update(context)
            memory.updated_at = datetime.now()
            
            self._save_memory()
            self.stats['memory_hits'] += 1
            
        except Exception as e:
            logger.error(f"❌ Erreur mise à jour mémoire: {e}")
    
    def _get_memory_messages(self, session_id: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Récupère les messages récents de la mémoire conversationnelle"""
        try:
            if session_id not in self.memory_store:
                return []
            
            memory = self.memory_store[session_id]
            recent_messages = memory.messages[-limit:] if memory.messages else []
            
            return recent_messages
            
        except Exception as e:
            logger.error(f"❌ Erreur récupération messages mémoire: {e}")
            return []
    
    def _vector_search(self, query: str, n_results: int = 5) -> Tuple[List[str], float]:
        """Recherche vectorielle dans ChromaDB"""
        try:
            if not self.embedding_model or not self.collection:
                return [], 0.0
            
            logger.info("📊 Recherche vectorielle...")
            
            query_embedding = self.embedding_model.encode([query]).tolist()[0]
            
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results
            )
            
            documents = results.get('documents', [[]])[0]
            distances = results.get('distances', [[]])[0]
            
            logger.info(f"📊 Trouvé {len(documents)} résultats vectoriels")
            
            confidence = 1.0 - (sum(distances) / len(distances)) if distances else 0.0
            
            if documents:
                self.stats['vector_hits'] += 1
            
            return documents, confidence
            
        except Exception as e:
            logger.error(f"❌ Erreur recherche vectorielle: {e}")
            return [], 0.0
    
    def _graph_search(self, query: str) -> Tuple[List[str], float]:
        """Recherche dans le graphe NetworkX"""
        try:
            if not self.graph_manager:
                return [], 0.0
            
            logger.info("🕸️ Recherche dans le graphe NetworkX...")
            
            # Rechercher les entités pertinentes
            entities = self.graph_manager.search_entities(query, limit=3)
            
            graph_results = []
            for entity in entities:
                # Récupérer les relations de l'entité
                relations = self.graph_manager.get_entity_relations(entity['name'])
                graph_results.extend(relations)
                
                # Ajouter des informations sur l'entité elle-même
                neighborhood = self.graph_manager.get_entity_neighborhood(entity['name'], depth=1)
                for node in neighborhood['nodes']:
                    if node['name'] == entity['name']:
                        entity_info = f"{node['name']} est un {node['type']}"
                        if node['properties']:
                            props = ", ".join([f"{k}: {v}" for k, v in node['properties'].items() if isinstance(v, (str, int, float))])
                            entity_info += f" ({props})"
                        graph_results.append(entity_info)
            
            logger.info(f"🕸️ Trouvé {len(graph_results)} résultats graphiques")
            
            confidence = 0.8 if graph_results else 0.0
            
            if graph_results:
                self.stats['graph_hits'] += 1
            
            return graph_results, confidence
            
        except Exception as e:
            logger.error(f"❌ Erreur recherche graphique: {e}")
            return [], 0.0
    
    def _hybrid_search(self, query: str) -> Tuple[List[str], float]:
        """Recherche hybride combinant Vector et NetworkX Graph RAG"""
        try:
            logger.info("🔍 Recherche RAG hybride (Vector + NetworkX Graph)...")
            
            # Recherche vectorielle
            vector_docs, vector_confidence = self._vector_search(query)
            
            # Recherche graphique
            graph_docs, graph_confidence = self._graph_search(query)
            
            # Combiner les résultats
            all_docs = vector_docs + graph_docs
            
            # Calculer la confiance hybride
            if vector_docs and graph_docs:
                hybrid_confidence = (vector_confidence + graph_confidence) / 2
            elif vector_docs:
                hybrid_confidence = vector_confidence * 0.8
            elif graph_docs:
                hybrid_confidence = graph_confidence * 0.6
            else:
                hybrid_confidence = 0.0
            
            # Dédupliquer et limiter
            unique_docs = list(dict.fromkeys(all_docs))[:7]
            
            logger.info(f"🔍 Recherche hybride: {len(vector_docs)} vector + {len(graph_docs)} graph = {len(unique_docs)} total")
            
            return unique_docs, hybrid_confidence
            
        except Exception as e:
            logger.error(f"❌ Erreur recherche hybride: {e}")
            return [], 0.0
    
    def _generate_response_with_langchain(self, query: str, context_docs: List[str], session_id: str, confidence: float) -> str:
        """Génère une réponse avec LangChain"""
        try:
            if not self.llm_manager:
                return "Désolé, le système de génération n'est pas disponible."
            
            # Récupérer les messages récents
            recent_messages = self._get_memory_messages(session_id)
            
            # Formater les messages pour LangChain
            formatted_messages = self.prompt_manager.format_memory_for_langchain(recent_messages)
            
            # Détecter le type de prompt
            prompt_type = self.prompt_manager.detect_prompt_type(query)
            logger.info(f"🔍 Type de prompt détecté: {prompt_type}")
            
            # Générer le prompt avec LangChain
            prompt = self.prompt_manager.get_prompt_with_context(
                query=query,
                context_docs=context_docs,
                memory_context=formatted_messages,
                prompt_type=prompt_type
            )
            
            # Générer la réponse
            response = self.llm_manager.generate(str(prompt))
            return response
            
        except Exception as e:
            logger.error(f"❌ Erreur génération avec LangChain: {e}")
            return f"Désolé, je ne peux pas traiter votre demande pour le moment."
    
    def process_query(self, query: str, session_id: str = "default") -> str:
        """Traite une requête avec RAG hybride + mémoire + LangChain"""
        start_time = time.time()
        
        try:
            logger.info(f"🔍 Traitement requête LangChain: {query[:50]}...")
            
            # Recherche hybride
            context_docs, confidence = self._hybrid_search(query)
            self.last_confidence_score = confidence
            
            # Générer la réponse avec LangChain
            response = self._generate_response_with_langchain(query, context_docs, session_id, confidence)
            
            # Calculer le temps de réponse
            response_time = time.time() - start_time
            
            # Mettre à jour les statistiques
            self.stats['total_queries'] += 1
            self.stats['avg_confidence'] = (self.stats['avg_confidence'] * (self.stats['total_queries'] - 1) + confidence) / self.stats['total_queries']
            self.stats['avg_response_time'] = (self.stats['avg_response_time'] * (self.stats['total_queries'] - 1) + response_time) / self.stats['total_queries']
            
            # Mettre à jour la mémoire
            context_info = {
                'confidence': confidence,
                'sources_count': len(context_docs),
                'response_time': response_time,
                'provider': self.llm_manager.current_provider if self.llm_manager else 'unknown',
                'prompt_type': self.prompt_manager.detect_prompt_type(query)
            }
            self._update_memory(session_id, query, response, context_info)
            
            # Mettre à jour le graphe avec l'interaction
            if self.graph_manager:
                self.graph_manager.update_with_interaction(query, response, "support_agent")
            
            logger.info(f"✅ Réponse générée ({len(response)} chars) - Confiance: {confidence:.2f}")
            
            return response
            
        except Exception as e:
            logger.error(f"❌ Erreur traitement requête: {e}")
            return f"Désolé, une erreur s'est produite: {str(e)}"
    
    def get_memory_manager(self):
        """Retourne le gestionnaire de mémoire pour compatibilité"""
        class MemoryManager:
            def __init__(self, agent):
                self.agent = agent
            
            def get_messages(self, session_id: str, limit: int = 20):
                if session_id in self.agent.memory_store:
                    return self.agent.memory_store[session_id].messages[-limit:]
                return []
            
            def clear_session(self, session_id: str):
                if session_id in self.agent.memory_store:
                    del self.agent.memory_store[session_id]
                    self.agent._save_memory()
            
            @property
            def sessions(self):
                return self.agent.memory_store
        
        return MemoryManager(self)
    
    @property
    def memory_manager(self):
        """Propriété pour compatibilité avec l'API"""
        return self.get_memory_manager()
    
    @property
    def chroma_collection(self):
        """Propriété pour compatibilité avec l'API"""
        return self.collection
    
    def get_stats(self) -> Dict[str, Any]:
        """Récupère les statistiques de l'agent"""
        stats = {
            **self.stats,
            'memory_sessions': len(self.memory_store),
            'components_status': {
                'llm_manager': bool(self.llm_manager),
                'embedding_model': bool(self.embedding_model),
                'chromadb': bool(self.collection),
                'networkx_graph': bool(self.graph_manager),
                'langchain_prompts': True
            }
        }
        
        if self.graph_manager:
            graph_stats = self.graph_manager.get_stats()
            stats['graph_stats'] = graph_stats
        
        return stats

def main():
    """Test de l'agent LangChain"""
    print("🧪 TEST AGENT LANGCHAIN (Vector + NetworkX Graph + Memory + LangChain)")
    print("-" * 70)
    
    # Initialiser l'agent
    agent = AgenticSupportAgentLangChain()
    
    # Tests avec mémoire conversationnelle
    session_id = "test_langchain_session"
    
    test_queries = [
        "Bonjour, je m'appelle Charlie",
        "Quels sont les prix de TeamSquare ?",
        "Parle-moi du plan Professional",
        "Quelles intégrations sont disponibles ?",
        "Tu te souviens de mon nom ?"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n🔍 Test {i}: '{query}'")
        
        response = agent.process_query(query, session_id)
        
        print(f"📝 Réponse: {response[:200]}...")
        print(f"📊 Confiance: {agent.last_confidence_score:.2f}")
    
    # Afficher les statistiques
    print(f"\n📊 STATISTIQUES FINALES")
    print("-" * 40)
    stats = agent.get_stats()
    for key, value in stats.items():
        if key != 'graph_stats':
            print(f"{key}: {value}")
    
    if 'graph_stats' in stats:
        print(f"\n🕸️ STATISTIQUES GRAPHE NETWORKX")
        print("-" * 40)
        for key, value in stats['graph_stats'].items():
            print(f"{key}: {value}")

if __name__ == "__main__":
    main()

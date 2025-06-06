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
from core.graph_manager import KnowledgeGraphManager
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

class AgenticSupportAgentHybridComplete:
    """Agent de support avec RAG hybride (Vector + Graph) + Mémoire conversationnelle"""
    
    def __init__(self):
        self.settings = Settings()
        self.llm_manager = None
        self.embedding_model = None
        self.chroma_client = None
        self.collection = None
        self.graph_manager = None
        self.memory_store = {}  # Stockage en mémoire des conversations
        self.memory_file = "data/memory/conversations.json"
        
        # Statistiques
        self.stats = {
            'total_queries': 0,
            'vector_hits': 0,
            'graph_hits': 0,
            'memory_hits': 0,
            'avg_confidence': 0.0,
            'avg_response_time': 0.0
        }
        
        self._initialize()
    
    def _initialize(self):
        """Initialise tous les composants"""
        try:
            logger.info("🔄 Initialisation de l'agent hybride complet...")
            
            # 1. LLM Manager
            self._init_llm_manager()
            
            # 2. Modèle d'embeddings
            self._init_embedding_model()
            
            # 3. ChromaDB
            self._init_chromadb()
            
            # 4. Graph Manager (optionnel)
            self._init_graph_manager()
            
            # 5. Memory System
            self._init_memory_system()
            
            logger.info("✅ Agent hybride complet initialisé avec succès")
            
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
    
    def _init_graph_manager(self):
        """Initialise le gestionnaire de graphe Neo4j"""
        try:
            logger.info("🔄 Initialisation du gestionnaire de graphe Neo4j...")
            self.graph_manager = KnowledgeGraphManager()
            logger.info("✅ Gestionnaire de graphe initialisé")
        except Exception as e:
            logger.warning(f"⚠️  Erreur Neo4j: {e}")
            self.graph_manager = None
    
    def _init_memory_system(self):
        """Initialise le système de mémoire"""
        try:
            logger.info("🔄 Initialisation du système de mémoire...")
            
            # Créer le dossier de mémoire
            os.makedirs(os.path.dirname(self.memory_file), exist_ok=True)
            
            # Charger les conversations existantes
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
            
            # Ajouter le message
            memory.messages.append({
                'timestamp': datetime.now().isoformat(),
                'query': query,
                'response': response,
                'context': context
            })
            
            # Limiter à 50 messages par session
            if len(memory.messages) > 50:
                memory.messages = memory.messages[-50:]
            
            # Mettre à jour le contexte
            memory.context.update(context)
            memory.updated_at = datetime.now()
            
            # Sauvegarder
            self._save_memory()
            
            self.stats['memory_hits'] += 1
            
        except Exception as e:
            logger.error(f"❌ Erreur mise à jour mémoire: {e}")
    
    def _get_memory_context(self, session_id: str) -> str:
        """Récupère le contexte de la mémoire conversationnelle"""
        try:
            if session_id not in self.memory_store:
                return ""
            
            memory = self.memory_store[session_id]
            
            # Récupérer les 5 derniers messages
            recent_messages = memory.messages[-5:] if memory.messages else []
            
            if not recent_messages:
                return ""
            
            context_parts = ["Contexte conversationnel récent:"]
            for msg in recent_messages:
                context_parts.append(f"Q: {msg['query'][:100]}...")
                context_parts.append(f"R: {msg['response'][:100]}...")
            
            return "\n".join(context_parts)
            
        except Exception as e:
            logger.error(f"❌ Erreur récupération contexte mémoire: {e}")
            return ""
    
    def _vector_search(self, query: str, n_results: int = 5) -> Tuple[List[str], float]:
        """Recherche vectorielle dans ChromaDB"""
        try:
            if not self.embedding_model or not self.collection:
                return [], 0.0
            
            logger.info("📊 Recherche vectorielle...")
            
            # Générer l'embedding de la requête
            query_embedding = self.embedding_model.encode([query]).tolist()[0]
            
            # Rechercher dans ChromaDB
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results
            )
            
            documents = results.get('documents', [[]])[0]
            distances = results.get('distances', [[]])[0]
            
            logger.info(f"📊 Trouvé {len(documents)} résultats vectoriels")
            
            # Calculer le score de confiance (1 - distance moyenne)
            confidence = 1.0 - (sum(distances) / len(distances)) if distances else 0.0
            
            if documents:
                self.stats['vector_hits'] += 1
            
            return documents, confidence
            
        except Exception as e:
            logger.error(f"❌ Erreur recherche vectorielle: {e}")
            return [], 0.0
    
    def _graph_search(self, query: str) -> Tuple[List[str], float]:
        """Recherche dans le graphe de connaissances"""
        try:
            if not self.graph_manager:
                return [], 0.0
            
            logger.info("🕸️ Recherche dans le graphe...")
            
            # Extraire les entités de la requête
            entities = self._extract_entities(query)
            
            graph_results = []
            for entity in entities:
                # Rechercher les relations de l'entité
                relations = self.graph_manager.get_entity_relations(entity)
                graph_results.extend(relations)
            
            logger.info(f"🕸️ Trouvé {len(graph_results)} résultats graphiques")
            
            confidence = 0.8 if graph_results else 0.0
            
            if graph_results:
                self.stats['graph_hits'] += 1
            
            return graph_results, confidence
            
        except Exception as e:
            logger.error(f"❌ Erreur recherche graphique: {e}")
            return [], 0.0
    
    def _extract_entities(self, query: str) -> List[str]:
        """Extrait les entités de la requête"""
        # Entités TeamSquare connues
        entities = []
        query_lower = query.lower()
        
        entity_keywords = {
            'teamsquare': ['teamsquare', 'team square'],
            'plan_starter': ['starter', 'plan starter'],
            'plan_professional': ['professional', 'plan professional', 'pro'],
            'plan_enterprise': ['enterprise', 'plan enterprise'],
            'api': ['api', 'interface'],
            'prix': ['prix', 'tarif', 'coût', 'price'],
            'utilisateur': ['utilisateur', 'user', 'membre'],
            'support': ['support', 'aide', 'help']
        }
        
        for entity, keywords in entity_keywords.items():
            if any(keyword in query_lower for keyword in keywords):
                entities.append(entity)
        
        return entities
    
    def _hybrid_search(self, query: str) -> Tuple[List[str], float]:
        """Recherche hybride combinant Vector et Graph RAG"""
        try:
            logger.info("🔍 Recherche RAG hybride (Vector + Graph)...")
            
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
                hybrid_confidence = vector_confidence * 0.8  # Pénalité pour absence de graph
            elif graph_docs:
                hybrid_confidence = graph_confidence * 0.6  # Pénalité pour absence de vector
            else:
                hybrid_confidence = 0.0
            
            # Dédupliquer et limiter
            unique_docs = list(dict.fromkeys(all_docs))[:5]
            
            logger.info(f"🔍 Recherche hybride: {len(vector_docs)} vector + {len(graph_docs)} graph = {len(unique_docs)} total")
            
            return unique_docs, hybrid_confidence
            
        except Exception as e:
            logger.error(f"❌ Erreur recherche hybride: {e}")
            return [], 0.0
    
    def _generate_response(self, query: str, context_docs: List[str], memory_context: str, confidence: float) -> str:
        """Génère une réponse avec le LLM"""
        try:
            if not self.llm_manager:
                return "Désolé, le système de génération n'est pas disponible."
            
            # Construire le contexte
            context_text = "\n".join(context_docs) if context_docs else "Aucun contexte spécifique trouvé."
            
            # Prompt enrichi avec mémoire
            prompt = f"""Tu es un assistant spécialisé TeamSquare. Réponds de manière naturelle et utile.

{memory_context}

Contexte actuel:
{context_text}

Question: {query}

Instructions:
- Utilise le contexte pour répondre précisément
- Si le contexte est insuffisant, dis-le honnêtement
- Sois naturel et conversationnel
- Mentionne ton niveau de confiance: {confidence:.2f}

Réponse:"""
            
            # Générer avec le LLM hybride
            response = self.llm_manager.generate(prompt)
            
            return response
            
        except Exception as e:
            logger.error(f"❌ Erreur génération: {e}")
            return f"Désolé, je ne peux pas traiter votre demande pour le moment. (Confiance: {confidence:.2f})"
    
    def process_query(self, query: str, session_id: str = "default") -> Dict[str, Any]:
        """Traite une requête avec RAG hybride + mémoire"""
        start_time = time.time()
        
        try:
            logger.info(f"🔍 Traitement requête hybride: {query[:50]}...")
            
            # Récupérer le contexte de mémoire
            memory_context = self._get_memory_context(session_id)
            
            # Recherche hybride
            context_docs, confidence = self._hybrid_search(query)
            
            # Générer la réponse
            response = self._generate_response(query, context_docs, memory_context, confidence)
            
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
                'provider': self.llm_manager.current_provider if self.llm_manager else 'unknown'
            }
            self._update_memory(session_id, query, response, context_info)
            
            logger.info(f"✅ Réponse générée ({len(response)} chars) - Confiance: {confidence:.2f}")
            
            return {
                'response': response,
                'confidence': confidence,
                'sources_count': len(context_docs),
                'response_time': response_time,
                'session_id': session_id,
                'provider': self.llm_manager.current_provider if self.llm_manager else 'unknown',
                'memory_context_used': bool(memory_context)
            }
            
        except Exception as e:
            logger.error(f"❌ Erreur traitement requête: {e}")
            return {
                'response': f"Désolé, une erreur s'est produite: {str(e)}",
                'confidence': 0.0,
                'sources_count': 0,
                'response_time': time.time() - start_time,
                'session_id': session_id,
                'provider': 'error',
                'memory_context_used': False
            }
    
    def get_memory(self, session_id: str) -> Dict[str, Any]:
        """Récupère la mémoire d'une session"""
        if session_id in self.memory_store:
            return self.memory_store[session_id].to_dict()
        return {}
    
    def clear_memory(self, session_id: str) -> bool:
        """Efface la mémoire d'une session"""
        if session_id in self.memory_store:
            del self.memory_store[session_id]
            self._save_memory()
            return True
        return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Récupère les statistiques de l'agent"""
        return {
            **self.stats,
            'memory_sessions': len(self.memory_store),
            'components_status': {
                'llm_manager': bool(self.llm_manager),
                'embedding_model': bool(self.embedding_model),
                'chromadb': bool(self.collection),
                'graph_manager': bool(self.graph_manager)
            }
        }

def main():
    """Test de l'agent hybride complet"""
    print("🧪 TEST AGENT HYBRIDE COMPLET (Vector + Graph + Memory)")
    print("-" * 70)
    
    # Initialiser l'agent
    agent = AgenticSupportAgentHybridComplete()
    
    # Tests avec mémoire conversationnelle
    session_id = "test_session_123"
    
    test_queries = [
        "Bonjour, je m'appelle Alice",
        "Quels sont les prix de TeamSquare ?",
        "Et pour le plan Professional ?",
        "Je suis Alice, tu te souviens de moi ?",
        "Qu'est-ce que TeamSquare ?"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n🔍 Test {i}: '{query}'")
        
        result = agent.process_query(query, session_id)
        
        print(f"📝 Réponse: {result['response'][:200]}...")
        print(f"📊 Confiance: {result['confidence']:.2f}")
        print(f"⏱️ Temps: {result['response_time']:.2f}s")
        print(f"🧠 Mémoire utilisée: {result['memory_context_used']}")
        print(f"🔧 Provider: {result['provider']}")
    
    # Afficher les statistiques
    print(f"\n📊 STATISTIQUES FINALES")
    print("-" * 40)
    stats = agent.get_stats()
    for key, value in stats.items():
        print(f"{key}: {value}")
    
    # Afficher la mémoire
    print(f"\n🧠 MÉMOIRE DE SESSION")
    print("-" * 40)
    memory = agent.get_memory(session_id)
    print(f"Messages: {len(memory.get('messages', []))}")
    print(f"Contexte: {memory.get('context', {})}")

if __name__ == "__main__":
    main()

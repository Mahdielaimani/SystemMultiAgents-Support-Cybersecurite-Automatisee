"""
Agent de support principal utilisant le système NetworkX hybride
"""
import logging
import sys
import os
from pathlib import Path

# Ajouter le répertoire racine au path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    # Importer l'agent NetworkX hybride comme agent principal
    from agents.support_agent.agentic_support_agent_networkx import AgenticSupportAgentNetworkX
    
    class SupportAgent(AgenticSupportAgentNetworkX):
        """
        Agent de support principal basé sur NetworkX hybride.
        
        Cette classe hérite de AgenticSupportAgentNetworkX et peut être
        étendue avec des fonctionnalités spécifiques si nécessaire.
        """
        
        def __init__(self):
            super().__init__()
            logger.info("✅ Agent de support principal initialisé avec NetworkX hybride")
        
        def get_agent_info(self):
            """Informations sur l'agent"""
            return {
                "name": "TeamSquare Support Agent",
                "version": "5.0.0",
                "type": "NetworkX Hybrid RAG Agent",
                "features": [
                    "Vector RAG (ChromaDB + BGE)",
                    "Graph RAG (NetworkX)",
                    "Conversational Memory",
                    "Hybrid LLM (Gemini + Mistral)",
                    "Real-time Learning"
                ],
                "capabilities": [
                    "TeamSquare product support",
                    "Technical documentation",
                    "Pricing information",
                    "Integration guidance",
                    "Contextual conversations"
                ]
            }
        
        def health_check(self):
            """Vérification de santé de l'agent"""
            try:
                status = {
                    "agent_status": "healthy",
                    "components": {
                        "llm_manager": bool(self.llm_manager),
                        "embedding_model": bool(self.embedding_model),
                        "chromadb": bool(self.collection),
                        "networkx_graph": bool(self.graph_manager),
                        "memory_system": bool(self.memory_store is not None)
                    }
                }
                
                # Vérifier les statistiques
                if self.graph_manager:
                    graph_stats = self.graph_manager.get_stats()
                    status["graph_stats"] = {
                        "entities": graph_stats.get('entities_count', 0),
                        "relations": graph_stats.get('relations_count', 0),
                        "connected": graph_stats.get('is_connected', False)
                    }
                
                if self.collection:
                    try:
                        vector_count = self.collection.count()
                        status["vector_stats"] = {"documents": vector_count}
                    except:
                        status["vector_stats"] = {"documents": 0}
                
                status["memory_stats"] = {"sessions": len(self.memory_store)}
                
                return status
                
            except Exception as e:
                logger.error(f"❌ Erreur health check: {e}")
                return {
                    "agent_status": "error",
                    "error": str(e)
                }
        
        def process_support_query(self, query: str, session_id: str = "default", context: dict = None):
            """
            Traite une requête de support avec contexte additionnel.
            
            Args:
                query: Question de l'utilisateur
                session_id: ID de session pour la mémoire
                context: Contexte additionnel (optionnel)
            
            Returns:
                Réponse de l'agent avec métadonnées
            """
            try:
                # Ajouter le contexte à la requête si fourni
                if context:
                    enhanced_query = f"Contexte: {context}\n\nQuestion: {query}"
                else:
                    enhanced_query = query
                
                # Traiter avec l'agent NetworkX hybride
                response = self.process_query(enhanced_query, session_id)
                
                # Retourner avec métadonnées
                return {
                    "response": response,
                    "confidence": self.last_confidence_score,
                    "session_id": session_id,
                    "agent_type": "networkx_hybrid",
                    "context_used": bool(context)
                }
                
            except Exception as e:
                logger.error(f"❌ Erreur process_support_query: {e}")
                return {
                    "response": f"Désolé, je ne peux pas traiter votre demande pour le moment: {str(e)}",
                    "confidence": 0.0,
                    "session_id": session_id,
                    "agent_type": "networkx_hybrid",
                    "error": str(e)
                }

    # Créer une instance globale pour l'API
    support_agent = SupportAgent()
    
    logger.info("✅ Agent de support principal chargé avec succès")

except ImportError as e:
    logger.error(f"❌ Erreur import agent NetworkX: {e}")
    
    # Fallback vers un agent simple
    class SupportAgent:
        def __init__(self):
            self.agent_type = "fallback"
            logger.warning("⚠️ Agent de fallback initialisé")
        
        def process_query(self, query: str, session_id: str = "default"):
            return "Désolé, l'agent principal n'est pas disponible."
        
        def health_check(self):
            return {"agent_status": "fallback", "error": "Agent principal non disponible"}
        
        def get_agent_info(self):
            return {"name": "Fallback Agent", "version": "1.0.0", "type": "Fallback"}
    
    support_agent = SupportAgent()

def get_support_agent():
    """Retourne l'instance de l'agent de support"""
    return support_agent

def main():
    """Test de l'agent de support principal"""
    print("🧪 TEST AGENT DE SUPPORT PRINCIPAL")
    print("-" * 50)
    
    agent = get_support_agent()
    
    # Informations sur l'agent
    info = agent.get_agent_info()
    print(f"Agent: {info['name']} v{info['version']}")
    print(f"Type: {info['type']}")
    
    # Health check
    health = agent.health_check()
    print(f"Status: {health['agent_status']}")
    
    # Test de requête
    if hasattr(agent, 'process_support_query'):
        result = agent.process_support_query("Bonjour, quels sont les prix de TeamSquare ?")
        print(f"Réponse: {result['response'][:100]}...")
        print(f"Confiance: {result['confidence']}")

if __name__ == "__main__":
    main()

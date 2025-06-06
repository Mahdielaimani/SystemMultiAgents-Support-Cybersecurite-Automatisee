"""
Agent de support TeamSquare - VERSION SIMPLIFIÉE ET NATURELLE
"""
import logging
import json
import time
import random
from typing import Dict, List, Any, Optional
from pathlib import Path
import sys

# Ajouter le répertoire racine au path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AgenticSupportAgentWithExternalRouting:
    """Agent de support TeamSquare simplifié et naturel"""
    
    def __init__(self):
        """Initialisation simplifiée"""
        logger.info("🔄 Initialisation de l'agent TeamSquare...")
        
        # Composants essentiels seulement
        self._init_llm_manager()
        self._init_embeddings()
        self._init_vectorstore()
        self._init_external_routing()
        
        # Mémoire de session simple
        self.session_memory = {}
        
        # Statistiques
        self.stats = {
            "queries_processed": 0,
            "external_searches": 0,
            "greetings_handled": 0
        }
        
        # Sessions avec recherche externe en attente
        self.pending_external_searches = {}
        
        # Connaissances de base TeamSquare
        self.teamsquare_info = {
            "company": "TeamSquare est une plateforme de collaboration d'équipe qui aide les entreprises à mieux travailler ensemble.",
            "features": ["Chat en temps réel", "Gestion de projets", "Partage de fichiers", "Visioconférences"],
            "pricing": {
                "Starter": "9€/mois par utilisateur - Parfait pour petites équipes",
                "Professional": "19€/mois par utilisateur - Idéal pour équipes en croissance", 
                "Enterprise": "Sur devis - Pour grandes organisations"
            }
        }
        
        logger.info("✅ Agent TeamSquare initialisé")
    
    def _init_llm_manager(self):
        """Initialiser le LLM"""
        try:
            from utils.hybrid_llm_manager_gemini import HybridLLMManagerGemini
            self.llm_manager = HybridLLMManagerGemini()
            logger.info("✅ LLM initialisé")
        except Exception as e:
            logger.error(f"❌ Erreur LLM: {e}")
            self.llm_manager = None
    
    def _init_embeddings(self):
        """Initialiser les embeddings"""
        try:
            from sentence_transformers import SentenceTransformer
            self.embedding_model = SentenceTransformer('BAAI/bge-large-en-v1.5')
            logger.info("✅ Embeddings initialisés")
        except Exception as e:
            logger.error(f"❌ Erreur embeddings: {e}")
            self.embedding_model = None
    
    def _init_vectorstore(self):
        """Initialiser ChromaDB"""
        try:
            import chromadb
            self.chroma_client = chromadb.PersistentClient(path="data/vector_db")
            try:
                self.collection = self.chroma_client.get_collection("teamsquare_knowledge")
                logger.info("✅ ChromaDB connecté")
            except:
                self.collection = self.chroma_client.create_collection("teamsquare_knowledge")
                logger.info("✅ ChromaDB créé")
        except Exception as e:
            logger.error(f"❌ Erreur ChromaDB: {e}")
            self.collection = None
    
    def _init_external_routing(self):
        """Initialiser l'agent externe"""
        try:
            from agents.external_search_agent.simple_web_search_agent import SimpleWebSearchAgent
            self.external_agent = SimpleWebSearchAgent()
            logger.info("✅ Agent externe initialisé")
        except Exception as e:
            logger.warning(f"⚠️ Agent externe non disponible: {e}")
            self.external_agent = None
    
    def _is_greeting(self, query: str) -> bool:
        """Détecter les salutations"""
        greetings = ['bonjour', 'bonsoir', 'salut', 'hello', 'hi', 'hey', 'coucou']
        return any(g in query.lower() for g in greetings) and len(query.split()) <= 3
    
    def _is_teamsquare_question(self, query: str) -> bool:
        """Détecter les questions TeamSquare"""
        keywords = [
            'teamsquare', 'prix', 'tarif', 'fonctionnalité', 'collaboration',
            'équipe', 'projet', 'entreprise', 'société', 'que fait', 'votre entreprise'
        ]
        return any(k in query.lower() for k in keywords)
    
    def _should_search_externally(self, query: str) -> bool:
        """Déterminer si recherche externe nécessaire"""
        # Pas de recherche externe pour salutations
        if self._is_greeting(query):
            return False
        
        # Pas de recherche externe pour questions TeamSquare
        if self._is_teamsquare_question(query):
            return False
        
        # Recherche externe pour tout le reste
        external_indicators = [
            'nvidia', 'invidia', 'google', 'microsoft', 'apple', 'amazon',
            'météo', 'weather', 'actualité', 'news', 'recette', 'cuisine',
            'c\'est quoi', 'qu\'est-ce que', 'qui est', 'définition'
        ]
        
        query_lower = query.lower()
        return any(indicator in query_lower for indicator in external_indicators)
    
    def _get_varied_greeting(self, session_id: str) -> str:
        """Générer une salutation variée"""
        # Vérifier si c'est la première fois dans cette session
        if session_id not in self.session_memory:
            self.session_memory[session_id] = {
                "greeted": False,
                "messages": []
            }
        
        if not self.session_memory[session_id]["greeted"]:
            # Première salutation
            self.session_memory[session_id]["greeted"] = True
            greetings = [
                "Salut ! 😊 Je suis l'assistant TeamSquare. Comment puis-je vous aider ?",
                "Bonjour ! Ravi de vous rencontrer ! Je suis là pour vous aider avec TeamSquare.",
                "Hello ! 👋 Assistant TeamSquare à votre service ! Que puis-je faire pour vous ?",
                "Bonjour ! 😊 Je suis votre assistant TeamSquare. En quoi puis-je vous aider aujourd'hui ?"
            ]
        else:
            # Salutations suivantes
            greetings = [
                "Re-bonjour ! 😊 Que puis-je faire d'autre pour vous ?",
                "Salut ! De retour ? Comment puis-je vous aider cette fois ?",
                "Hello ! 👋 Encore moi ! Que voulez-vous savoir ?",
                "Re ! 😊 Une autre question ?"
            ]
        
        return random.choice(greetings)
    
    def _search_knowledge(self, query: str) -> List[str]:
        """Rechercher dans la base de connaissances"""
        results = []
        
        # Recherche dans ChromaDB si disponible
        if self.collection and self.embedding_model:
            try:
                query_embedding = self.embedding_model.encode([query]).tolist()[0]
                chroma_results = self.collection.query(
                    query_embeddings=[query_embedding],
                    n_results=3
                )
                if chroma_results['documents'] and chroma_results['documents'][0]:
                    results.extend(chroma_results['documents'][0])
            except Exception as e:
                logger.error(f"❌ Erreur recherche ChromaDB: {e}")
        
        return results
    
    def _generate_teamsquare_response(self, query: str, context: List[str]) -> str:
        """Générer une réponse sur TeamSquare"""
        if not self.llm_manager:
            # Réponses de fallback
            if 'prix' in query.lower() or 'tarif' in query.lower():
                return """Nos tarifs TeamSquare :

💰 **Starter** : 9€/mois par utilisateur
   Parfait pour les petites équipes

💰 **Professional** : 19€/mois par utilisateur  
   Idéal pour les équipes en croissance

💰 **Enterprise** : Sur devis
   Pour les grandes organisations

Quel plan vous intéresse ?"""
            
            elif 'entreprise' in query.lower() or 'société' in query.lower():
                return """TeamSquare est une plateforme de collaboration d'équipe moderne ! 🚀

Nous aidons les entreprises à :
• Mieux communiquer en équipe
• Gérer leurs projets efficacement  
• Partager des fichiers en sécurité
• Organiser des réunions virtuelles

Que voulez-vous savoir de plus ?"""
            
            else:
                return "Je suis l'assistant TeamSquare ! Comment puis-je vous aider avec notre plateforme de collaboration ?"
        
        # Construire le contexte
        context_text = "\n".join(context) if context else ""
        
        # Informations TeamSquare
        company_info = self.teamsquare_info["company"]
        features = ", ".join(self.teamsquare_info["features"])
        
        prompt = f"""Tu es l'assistant TeamSquare. Réponds de manière naturelle et amicale.

INFORMATIONS TEAMSQUARE :
- {company_info}
- Fonctionnalités : {features}
- Plans : Starter (9€/mois), Professional (19€/mois), Enterprise (sur devis)

CONTEXTE DISPONIBLE :
{context_text}

QUESTION : {query}

INSTRUCTIONS :
- Réponds naturellement comme un humain
- Utilise les infos TeamSquare
- Sois concis et utile
- Pas de formatage excessif

RÉPONSE :"""
        
        try:
            return self.llm_manager.generate(prompt)
        except Exception as e:
            logger.error(f"❌ Erreur génération: {e}")
            return "Désolé, petit problème technique ! Pouvez-vous reformuler votre question ?"
    
    def _offer_external_search(self, query: str) -> str:
        """Proposer une recherche externe"""
        offers = [
            f"Votre question sur '{query}' ne concerne pas TeamSquare. Voulez-vous que je fasse une recherche externe ? (oui/non)",
            f"'{query}' n'est pas lié à TeamSquare, mais je peux chercher sur le web ! Vous voulez ? (oui/non)",
            f"Cette question sort de mon domaine TeamSquare. Je peux demander à mon collègue de chercher '{query}' sur internet ? (oui/non)"
        ]
        return random.choice(offers)
    
    def _handle_external_search_response(self, query: str, session_id: str) -> str:
        """Gérer la réponse à la recherche externe"""
        query_lower = query.lower().strip()
        
        if session_id not in self.pending_external_searches:
            return "Je n'ai pas de recherche en attente."
        
        original_query = self.pending_external_searches[session_id]
        
        if query_lower in ['oui', 'yes', 'ok', 'okay', 'd\'accord']:
            del self.pending_external_searches[session_id]
            self.stats["external_searches"] += 1
            
            if self.external_agent:
                try:
                    search_result = self.external_agent.search(original_query)
                    if search_result.get("success"):
                        return f"""🔍 Voici ce que j'ai trouvé sur '{original_query}' :

{search_result.get("response", "Aucun résultat.")}

Autre chose sur TeamSquare ?"""
                    else:
                        return "Désolé, la recherche a échoué. Une question sur TeamSquare ?"
                except Exception as e:
                    return "Problème technique avec la recherche. Une question TeamSquare ?"
            else:
                return "Service de recherche indisponible. Une question TeamSquare ?"
        
        elif query_lower in ['non', 'no', 'nan']:
            del self.pending_external_searches[session_id]
            return "Pas de souci ! Une question sur TeamSquare ?"
        
        else:
            return f"Voulez-vous une recherche sur '{original_query}' ? Répondez oui ou non."
    
    def process_query(self, query: str, session_id: str = "default") -> str:
        """Traiter une requête - VERSION SIMPLIFIÉE"""
        try:
            logger.info(f"🔍 Requête: {query[:50]}...")
            
            self.stats["queries_processed"] += 1
            
            # Vérifier recherche externe en attente
            if session_id in self.pending_external_searches:
                return self._handle_external_search_response(query, session_id)
            
            # Ajouter à la mémoire de session
            if session_id not in self.session_memory:
                self.session_memory[session_id] = {"greeted": False, "messages": []}
            
            self.session_memory[session_id]["messages"].append({
                "user": query,
                "timestamp": time.time()
            })
            
            # Garder seulement les 10 derniers messages
            if len(self.session_memory[session_id]["messages"]) > 10:
                self.session_memory[session_id]["messages"] = self.session_memory[session_id]["messages"][-10:]
            
            # Gestion des salutations
            if self._is_greeting(query):
                self.stats["greetings_handled"] += 1
                return self._get_varied_greeting(session_id)
            
            # Vérifier si recherche externe nécessaire
            if self._should_search_externally(query):
                self.pending_external_searches[session_id] = query
                return self._offer_external_search(query)
            
            # Question TeamSquare - rechercher et répondre
            context = self._search_knowledge(query)
            response = self._generate_teamsquare_response(query, context)
            
            # Ajouter la réponse à la mémoire
            self.session_memory[session_id]["messages"][-1]["agent"] = response
            
            return response
            
        except Exception as e:
            logger.error(f"❌ Erreur: {e}")
            return "Oups, petit problème ! Reformulez votre question ?"
    
    def get_stats(self) -> Dict[str, Any]:
        """Statistiques simplifiées"""
        return {
            "agent_type": "simplified_natural_agent",
            "version": "9.0.0",
            "stats": self.stats,
            "active_sessions": len(self.session_memory),
            "pending_searches": len(self.pending_external_searches)
        }

# Test
if __name__ == "__main__":
    agent = AgenticSupportAgentWithExternalRouting()
    
    print("=== Test 1: Première salutation ===")
    print(agent.process_query("Bonjour", "test1"))
    
    print("\n=== Test 2: Deuxième salutation ===")
    print(agent.process_query("Salut", "test1"))
    
    print("\n=== Test 3: Question NVIDIA ===")
    print(agent.process_query("C'est quoi NVIDIA ?", "test2"))
    
    print("\n=== Test 4: Prix TeamSquare ===")
    print(agent.process_query("Quels sont vos prix ?", "test3"))

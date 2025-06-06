"""
Agent Support Agentic avec génération LLM hybride (OpenAI -> Mistral 7B)
Version corrigée pour utilisation normale d'OpenAI
"""

import logging
import os
import sys
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import json
import re

# Ajouter le répertoire racine au path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Imports pour RAG
try:
    from sentence_transformers import SentenceTransformer
    import chromadb
    from chromadb.config import Settings
    CHROMADB_AVAILABLE = True
except ImportError:
    print("⚠️  ChromaDB non disponible")
    CHROMADB_AVAILABLE = False

# Imports pour LLM hybride
try:
    from utils.hybrid_llm_manager import HybridLLMManager
    HYBRID_LLM_AVAILABLE = True
except ImportError:
    print("⚠️  Gestionnaire LLM hybride non disponible")
    HYBRID_LLM_AVAILABLE = False

class AgenticSupportAgentHybrid:
    """
    Agent Support avec génération LLM hybride (OpenAI -> Mistral 7B)
    """
    
    def __init__(self):
        self.logger = self._setup_logger()
        
        # Initialisation des composants
        self.embedding_model = None
        self.chroma_client = None
        self.collection = None
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
            r'\b(fonctionnalité|feature|service)\b'
        ]
        
        self._initialize_components()
    
    def _setup_logger(self):
        """Configure le logger"""
        logger = logging.getLogger("AgenticSupportAgentHybrid")
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
        """Initialise tous les composants"""
        try:
            # 1. Gestionnaire LLM hybride
            if HYBRID_LLM_AVAILABLE:
                self.logger.info("🔄 Initialisation du gestionnaire LLM hybride...")
                self.llm_manager = HybridLLMManager()
                self.logger.info(f"✅ LLM hybride initialisé - Provider: {self.llm_manager.current_provider}")
            
            # 2. Modèle d'embedding
            if CHROMADB_AVAILABLE:
                self.logger.info("🔄 Chargement du modèle BGE-Large-EN...")
                try:
                    self.embedding_model = SentenceTransformer('BAAI/bge-large-en-v1.5')
                    self.logger.info("✅ Modèle BGE-Large-EN chargé")
                except Exception as e:
                    self.logger.warning(f"⚠️  Erreur chargement BGE: {e}")
                
                # 3. ChromaDB
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
                
        except Exception as e:
            self.logger.error(f"❌ Erreur initialisation: {e}")
    
    def process_query(self, query: str) -> str:
        """
        Traite une requête avec génération LLM hybride
        """
        self.logger.info(f"🔍 Traitement requête: {query[:50]}...")
        
        try:
            # 1. Détection du type de requête
            query_type = self._detect_query_type(query)
            
            # 2. Récupération du contexte
            context = self._get_context(query, query_type)
            
            # 3. Génération avec LLM hybride
            if self.llm_manager and query_type != "greeting":
                response = self._generate_with_llm(query, context, query_type)
            else:
                response = self._generate_fallback(query, context, query_type)
            
            self.logger.info(f"✅ Réponse générée ({len(response)} chars)")
            return response
            
        except Exception as e:
            self.logger.error(f"❌ Erreur traitement requête: {e}")
            return "Désolé, j'ai rencontré un problème technique. Pouvez-vous reformuler votre question ?"
    
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
    
    def _get_context(self, query: str, query_type: str) -> str:
        """Récupère le contexte depuis la base de connaissances"""
        
        # Contexte par défaut selon le type
        default_context = self._get_default_context(query_type)
        
        if not self.embedding_model or not self.collection:
            return default_context
        
        try:
            # Recherche vectorielle
            query_embedding = self.embedding_model.encode([query]).tolist()[0]
            
            results = self.collection.query(
                query_embeddings=query_embedding,
                n_results=3,
                include=['documents', 'metadatas', 'distances']
            )
            
            # Construction du contexte
            context_parts = [default_context]
            if results['documents'] and results['documents'][0]:
                for doc, distance in zip(results['documents'][0], results['distances'][0]):
                    if distance < 0.6:  # Seuil de pertinence
                        context_parts.append(doc)
            
            return "\n\n".join(context_parts)
                
        except Exception as e:
            self.logger.error(f"❌ Erreur récupération contexte: {e}")
            return default_context
    
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
    
    def _generate_with_llm(self, query: str, context: str, query_type: str) -> str:
        """Génère une réponse avec le gestionnaire LLM hybride"""
        
        system_prompt = f"""Tu es un assistant support intelligent pour TeamSquare, une plateforme de collaboration.

CONTEXTE DISPONIBLE :
{context}

INSTRUCTIONS :
- Réponds de manière naturelle et amicale en français
- Utilise le contexte fourni quand c'est pertinent
- Si tu n'as pas l'information exacte, dis-le honnêtement
- Reste focalisé sur TeamSquare et ses services
- Évite les réponses trop techniques ou robotiques
- Sois concis mais informatif (maximum 300 mots)

STYLE :
- Conversationnel et humain
- Professionnel mais accessible
- Utilise des emojis avec parcimonie"""
        
        try:
            response = self.llm_manager.generate(query, system_prompt)
            
            # Vérifier la qualité de la réponse
            if len(response) < 20 or "erreur" in response.lower():
                return self._generate_fallback(query, context, query_type)
            
            return response
            
        except Exception as e:
            self.logger.error(f"❌ Erreur génération LLM: {e}")
            return self._generate_fallback(query, context, query_type)
    
    def _generate_fallback(self, query: str, context: str, query_type: str) -> str:
        """Génération de fallback sans LLM"""
        
        if query_type == "greeting":
            return "Bonjour ! Je suis votre assistant TeamSquare. Comment puis-je vous aider aujourd'hui ?"
        
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
            return f"Je comprends votre question sur '{query}'. Pouvez-vous être plus spécifique ? Je peux vous aider avec les prix, fonctionnalités, et services TeamSquare."

# Test rapide
def test_agent():
    """Test de l'agent hybride"""
    print("🧪 TEST AGENT HYBRIDE LLM")
    print("-" * 40)
    
    agent = AgenticSupportAgentHybrid()
    
    test_queries = [
        "bonjour",
        "donner moi les prix",
        "qu'est-ce que TeamSquare ?",
        "comment installer l'API ?"
    ]
    
    for query in test_queries:
        print(f"\n🔍 Test: {query}")
        response = agent.process_query(query)
        print(f"📝 Réponse: {response[:200]}...")

if __name__ == "__main__":
    test_agent()

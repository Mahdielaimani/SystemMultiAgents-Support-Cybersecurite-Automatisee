
from typing import Dict, Any, Optional, List
import os
import json
import time
from datetime import datetime
import asyncio
import chromadb
from chromadb.utils import embedding_functions
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.prompts import ChatPromptTemplate
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import LLMChainExtractor
from agents.base_agent import BaseAgent
from utils.logger import get_logger

logger = get_logger("support_agent_rag")

# Vérifier si la clé OpenAI est disponible
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
USE_OPENAI = bool(OPENAI_API_KEY)

# Configuration du modèle
if USE_OPENAI:
    MODEL_NAME = "gpt-3.5-turbo"
    EMBEDDING_MODEL = "text-embedding-ada-002"
else:
    # Fallback vers Mistral si pas d'OpenAI
    MODEL_NAME = "mistral-7b-instruct"
    EMBEDDING_MODEL = "all-MiniLM-L6-v2"

class EnhancedSupportAgent:
    """
    Agent de support amélioré avec RAG et génération via OpenAI/Mistral
    """
    
    def __init__(self):
        self.name = "enhanced_support_agent"
        self.chroma_client = None
        self.collection = None
        self.retriever = None
        self.qa_chain = None
        self.llm = None
        self.last_init_time = 0
        self.init_interval = 300  # 5 minutes
        
        # Initialiser l'agent
        self.initialize()
    
    def initialize(self):
        """Initialiser l'agent et les composants RAG"""
        try:
            current_time = time.time()
            
            # Ne réinitialiser que si nécessaire (toutes les 5 minutes)
            if current_time - self.last_init_time < self.init_interval:
                return
                
            logger.info("🔄 Initialisation de l'agent de support avec RAG...")
            
            # 1. Initialiser ChromaDB
            self._setup_chromadb()
            
            # 2. Initialiser le LLM
            self._setup_llm()
            
            # 3. Configurer le retriever et la chaîne QA
            self._setup_retriever()
            
            self.last_init_time = current_time
            logger.info("✅ Agent de support initialisé avec succès")
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de l'initialisation: {e}")
    
    def _setup_chromadb(self):
        """Configurer ChromaDB et la collection"""
        try:
            # Définir le chemin de persistance
            persist_directory = "./data/vector_db"
            
            # Créer le répertoire s'il n'existe pas
            os.makedirs(persist_directory, exist_ok=True)
            
            # Fonction d'embedding selon disponibilité
            if USE_OPENAI:
                ef = embedding_functions.OpenAIEmbeddingFunction(
                    api_key=OPENAI_API_KEY,
                    model_name=EMBEDDING_MODEL
                )
            else:
                ef = embedding_functions.SentenceTransformerEmbeddingFunction(
                    model_name=EMBEDDING_MODEL
                )
            
            # Initialiser le client ChromaDB
            self.chroma_client = chromadb.PersistentClient(path=persist_directory)
            
            # Obtenir ou créer la collection
            try:
                self.collection = self.chroma_client.get_collection(
                    name="teamsquare_knowledge",
                    embedding_function=ef
                )
                logger.info(f"✅ Collection ChromaDB trouvée avec {self.collection.count()} documents")
            except:
                # Créer la collection si elle n'existe pas
                self.collection = self.chroma_client.create_collection(
                    name="teamsquare_knowledge",
                    embedding_function=ef
                )
                logger.info("✅ Nouvelle collection ChromaDB créée")
                
                # Ajouter des données de base si la collection est vide
                if self.collection.count() == 0:
                    self._add_default_data()
        
        except Exception as e:
            logger.error(f"❌ Erreur lors de la configuration ChromaDB: {e}")
            raise
    
    def _add_default_data(self):
        """Ajouter des données par défaut si la collection est vide"""
        try:
            default_data = [
                {
                    "id": "teamsquare_intro_1",
                    "text": "TeamSquare est une plateforme de collaboration d'équipe innovante qui permet aux équipes de travailler ensemble efficacement.",
                    "metadata": {"source": "default", "category": "introduction"}
                },
                {
                    "id": "teamsquare_features_1",
                    "text": "TeamSquare offre des fonctionnalités de gestion de projet, de communication en temps réel et de partage de documents.",
                    "metadata": {"source": "default", "category": "features"}
                },
                {
                    "id": "teamsquare_security_1",
                    "text": "TeamSquare prend la sécurité au sérieux avec un chiffrement de bout en bout et des contrôles d'accès granulaires.",
                    "metadata": {"source": "default", "category": "security"}
                }
            ]
            
            # Ajouter les données à la collection
            ids = []
            texts = []
            metadatas = []
            
            for item in default_data:
                ids.append(item["id"])
                texts.append(item["text"])
                metadatas.append(item["metadata"])
            
            self.collection.add(
                ids=ids,
                documents=texts,
                metadatas=metadatas
            )
            
            logger.info(f"✅ {len(default_data)} documents par défaut ajoutés à la collection")
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de l'ajout des données par défaut: {e}")
    
    def _setup_llm(self):
        """Configurer le modèle de langage"""
        try:
            if USE_OPENAI:
                # Utiliser OpenAI si disponible
                self.llm = ChatOpenAI(
                    model_name=MODEL_NAME,
                    temperature=0.7,
                    api_key=OPENAI_API_KEY
                )
                logger.info(f"✅ Modèle OpenAI configuré: {MODEL_NAME}")
            else:
                # Fallback vers un modèle local simple
                self._setup_fallback_llm()
        
        except Exception as e:
            logger.error(f"❌ Erreur lors de la configuration du LLM: {e}")
            # Fallback en cas d'erreur
            self._setup_fallback_llm()
    
    def _setup_fallback_llm(self):
        """Configurer un LLM de fallback simple"""
        logger.warning("⚠️ Utilisation du LLM de fallback")
        
        # Créer une classe simple qui simule un LLM
        class FallbackLLM:
            def __init__(self):
                self.responses = {
                    "teamsquare": "TeamSquare est une plateforme de collaboration innovante qui permet aux équipes de travailler ensemble efficacement.",
                    "sécurité": "TeamSquare offre une sécurité de haut niveau avec chiffrement de bout en bout.",
                    "fonctionnalités": "TeamSquare propose gestion de projet, chat en temps réel et partage de fichiers.",
                    "prix": "Contactez notre équipe commerciale pour les tarifs personnalisés.",
                    "support": "Notre support client est disponible 24/7 pour vous aider.",
                    "collaboration": "TeamSquare facilite la collaboration d'équipe avec des outils intégrés.",
                    "projet": "Gérez vos projets efficacement avec les outils de planification de TeamSquare.",
                }
            
            def predict(self, prompt):
                # Recherche simple par mots-clés
                prompt_lower = prompt.lower()
                for keyword, response in self.responses.items():
                    if keyword.lower() in prompt_lower:
                        return response
                
                return "Je suis l'assistant TeamSquare. Je peux vous aider avec des questions sur notre plateforme de collaboration. Que souhaitez-vous savoir ?"
            
            def __call__(self, prompt, *args, **kwargs):
                return {"content": self.predict(prompt)}
        
        self.llm = FallbackLLM()
    
    def _setup_retriever(self):
        """Configurer le retriever et la chaîne QA"""
        try:
            # Pour le moment, utiliser une approche simple
            logger.info("✅ Retriever configuré en mode simple")
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de la configuration du retriever: {e}")
            self.retriever = None
            self.qa_chain = None
    
    async def process_message(self, message: str, session_id: str = None) -> str:
        """Traiter un message utilisateur avec RAG"""
        try:
            # Réinitialiser si nécessaire
            self.initialize()
            
            # Recherche dans ChromaDB
            if self.collection:
                try:
                    # Rechercher dans ChromaDB
                    results = self.collection.query(
                        query_texts=[message],
                        n_results=3
                    )
                    
                    if results and results["documents"] and results["documents"][0]:
                        # Construire une réponse à partir des documents
                        docs = results["documents"][0]
                        context = "\n".join(docs)
                        
                        # Utiliser le LLM pour générer une réponse
                        if hasattr(self.llm, 'predict'):
                            response = self.llm.predict(f"Contexte: {context}\n\nQuestion: {message}")
                        else:
                            response = f"Basé sur nos informations TeamSquare:\n\n{context}"
                        
                        return response
                except Exception as e:
                    logger.error(f"❌ Erreur lors de la recherche dans ChromaDB: {e}")
            
            # Fallback: utiliser directement le LLM
            if self.llm and hasattr(self.llm, 'predict'):
                return self.llm.predict(message)
            
            # Fallback final
            return "Je suis l'assistant TeamSquare. Comment puis-je vous aider avec notre plateforme de collaboration ?"
            
        except Exception as e:
            logger.error(f"❌ Erreur lors du traitement du message: {e}")
            return f"Je suis désolé, j'ai rencontré une erreur technique. Veuillez réessayer."
    
    async def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Traiter une requête générique"""
        try:
            message = request.get("message", "")
            session_id = request.get("session_id")
            
            response = await self.process_message(message, session_id)
            
            return {
                "response": response,
                "status": "success",
                "agent": self.name,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"❌ Erreur lors du traitement de la requête: {e}")
            return {
                "error": str(e),
                "status": "error",
                "agent": self.name,
                "timestamp": datetime.now().isoformat()
            }

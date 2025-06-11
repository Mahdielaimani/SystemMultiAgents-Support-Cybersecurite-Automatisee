"""
Gestionnaire pour la base de données vectorielle ChromaDB.
"""
import logging
import os
from typing import Dict, Any, List, Optional, Union

import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions

from agents.support_agent.bge_embeddings import BGEEmbeddings

logger = logging.getLogger(__name__)

class ChromaManager:
    """
    Gestionnaire pour la base de données vectorielle ChromaDB.
    """
    
    def __init__(self, persist_directory: str, embedding_model: str = "BAAI/bge-large-en-v1.5"):
        """
        Initialise le gestionnaire ChromaDB.
        
        Args:
            persist_directory: Répertoire de persistance pour ChromaDB
            embedding_model: Modèle d'embeddings à utiliser
        """
        self.persist_directory = persist_directory
        self.embedding_model = embedding_model
        self.client = None
        self.embeddings = None
        self._initialize_client()
        self._initialize_embeddings()
    
    def _initialize_client(self):
        """Initialise le client ChromaDB."""
        try:
            # Créer le répertoire de persistance s'il n'existe pas
            os.makedirs(self.persist_directory, exist_ok=True)
            
            # Initialiser le client ChromaDB
            self.client = chromadb.PersistentClient(
                path=self.persist_directory,
                settings=Settings(
                    anonymized_telemetry=False
                )
            )
            
            logger.info(f"ChromaDB client initialized with persist directory: {self.persist_directory}")
        except Exception as e:
            logger.error(f"Error initializing ChromaDB client: {str(e)}")
            raise
    
    def _initialize_embeddings(self):
        """Initialise la fonction d'embeddings."""
        try:
            # Utiliser BGE Embeddings si spécifié
            if "bge" in self.embedding_model.lower():
                self.embeddings = BGEEmbeddings(model_name=self.embedding_model)
                logger.info(f"Using BGE Embeddings model: {self.embedding_model}")
            # Sinon, utiliser OpenAI ou d'autres modèles supportés par ChromaDB
            elif "openai" in self.embedding_model.lower():
                openai_ef = embedding_functions.OpenAIEmbeddingFunction(
                    api_key=os.environ.get("OPENAI_API_KEY", ""),
                    model_name=self.embedding_model
                )
                self.embeddings = openai_ef
                logger.info(f"Using OpenAI Embeddings model: {self.embedding_model}")
            else:
                # Utiliser HuggingFace par défaut
                hf_ef = embedding_functions.HuggingFaceEmbeddingFunction(
                    model_name=self.embedding_model
                )
                self.embeddings = hf_ef
                logger.info(f"Using HuggingFace Embeddings model: {self.embedding_model}")
        except Exception as e:
            logger.error(f"Error initializing embeddings: {str(e)}")
            raise
    
    def get_or_create_collection(self, collection_name: str) -> Any:
        """
        Récupère ou crée une collection ChromaDB.
        
        Args:
            collection_name: Nom de la collection
            
        Returns:
            Collection ChromaDB
        """
        try:
            # Vérifier si la collection existe
            collections = self.client.list_collections()
            collection_exists = any(c.name == collection_name for c in collections)
            
            # Si BGE Embeddings est utilisé, nous devons gérer les embeddings manuellement
            if isinstance(self.embeddings, BGEEmbeddings):
                if collection_exists:
                    collection = self.client.get_collection(name=collection_name)
                else:
                    collection = self.client.create_collection(name=collection_name)
            else:
                # Sinon, utiliser l'embedding function de ChromaDB
                if collection_exists:
                    collection = self.client.get_collection(
                        name=collection_name,
                        embedding_function=self.embeddings
                    )
                else:
                    collection = self.client.create_collection(
                        name=collection_name,
                        embedding_function=self.embeddings
                    )
            
            logger.info(f"Collection retrieved or created: {collection_name}")
            return collection
        except Exception as e:
            logger.error(f"Error getting or creating collection: {str(e)}")
            raise
    
    async def add_documents(self, collection_name: str, documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Ajoute des documents à une collection.
        
        Args:
            collection_name: Nom de la collection
            documents: Liste de documents à ajouter
            
        Returns:
            Résultat de l'opération
        """
        try:
            collection = self.get_or_create_collection(collection_name)
            
            # Préparer les données
            ids = [f"doc_{i}" for i in range(len(documents))]
            texts = [doc["content"] for doc in documents]
            metadatas = [doc["metadata"] for doc in documents]
            
            # Si BGE Embeddings est utilisé, générer les embeddings manuellement
            if isinstance(self.embeddings, BGEEmbeddings):
                embeddings = self.embeddings.embed_documents(texts)
                collection.add(
                    ids=ids,
                    documents=texts,
                    metadatas=metadatas,
                    embeddings=embeddings
                )
            else:
                # Sinon, laisser ChromaDB gérer les embeddings
                collection.add(
                    ids=ids,
                    documents=texts,
                    metadatas=metadatas
                )
            
            logger.info(f"Added {len(documents)} documents to collection {collection_name}")
            return {"success": True, "count": len(documents)}
        except Exception as e:
            logger.error(f"Error adding documents: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def query_collection(self, collection_name: str, query_text: str, n_results: int = 5, 
                              filter_dict: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Interroge une collection pour trouver des documents similaires.
        
        Args:
            collection_name: Nom de la collection
            query_text: Texte de la requête
            n_results: Nombre de résultats à retourner
            filter_dict: Filtre à appliquer sur les métadonnées
            
        Returns:
            Résultats de la requête
        """
        try:
            collection = self.get_or_create_collection(collection_name)
            
            # Si BGE Embeddings est utilisé, générer l'embedding manuellement
            if isinstance(self.embeddings, BGEEmbeddings):
                query_embedding = self.embeddings.embed_query(query_text)
                results = collection.query(
                    query_embeddings=[query_embedding],
                    n_results=n_results,
                    where=filter_dict
                )
            else:
                # Sinon, laisser ChromaDB gérer l'embedding
                results = collection.query(
                    query_texts=[query_text],
                    n_results=n_results,
                    where=filter_dict
                )
            
            # Formater les résultats
            formatted_results = []
            for i in range(len(results["ids"][0])):
                formatted_results.append({
                    "id": results["ids"][0][i],
                    "content": results["documents"][0][i],
                    "metadata": results["metadatas"][0][i],
                    "distance": results["distances"][0][i] if "distances" in results else None
                })
            
            logger.info(f"Query returned {len(formatted_results)} results from collection {collection_name}")
            return {"success": True, "results": formatted_results}
        except Exception as e:
            logger.error(f"Error querying collection: {str(e)}")
            return {"success": False, "error": str(e)}

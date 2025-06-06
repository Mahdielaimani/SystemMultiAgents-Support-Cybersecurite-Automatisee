"""
Module d'ingestion de données pour l'agent de support.
"""
from typing import List, Dict, Any, Optional
import os
import time

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import (
    TextLoader, 
    PyPDFLoader, 
    CSVLoader, 
    UnstructuredMarkdownLoader
)
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings

from config.settings import settings
from config.logging_config import get_logger
from data.vector_db.chroma_manager import ChromaManager

logger = get_logger("support_ingestion")

class SupportKnowledgeBase:
    """
    Classe pour gérer la base de connaissances de l'agent de support.
    """
    
    def __init__(self, collection_name: str = "support_knowledge_base"):
        """
        Initialise la base de connaissances.
        
        Args:
            collection_name: Nom de la collection ChromaDB
        """
        self.collection_name = collection_name
        self.chroma_manager = ChromaManager()
        
        # Vérifier si la collection existe et contient des documents
        count = self.chroma_manager.get_collection_count(collection_name)
        logger.info(f"Collection {collection_name} contient {count} documents")
        
        if count == 0:
            logger.warning(f"La collection {collection_name} est vide. Exécutez le script d'ingestion.")
    
    def search(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """
        Recherche des documents pertinents pour une requête.
        
        Args:
            query: Requête de recherche
            k: Nombre de résultats à retourner
            
        Returns:
            Liste de documents pertinents
        """
        results = self.chroma_manager.search(
            collection_name=self.collection_name,
            query_texts=[query],
            n_results=k
        )
        
        # Retourner les résultats de la première requête (il n'y en a qu'une)
        return results[0] if results else []
    
    def add_document(self, content: str, metadata: Dict[str, Any]) -> bool:
        """
        Ajoute un document à la base de connaissances.
        
        Args:
            content: Contenu du document
            metadata: Métadonnées du document
            
        Returns:
            True si l'ajout a réussi, False sinon
        """
        import hashlib
        
        # Générer un ID unique pour le document
        doc_id = hashlib.md5(content.encode()).hexdigest()
        
        # Formater le document pour ChromaDB
        document = {
            "id": doc_id,
            "text": content,
            "metadata": metadata
        }
        
        # Ajouter le document à ChromaDB
        return self.chroma_manager.add_documents(
            collection_name=self.collection_name,
            documents=[document]
        )
    
    def add_feedback(self, query: str, response: str, feedback: str, is_helpful: bool) -> bool:
        """
        Ajoute un feedback utilisateur à la base de connaissances.
        
        Args:
            query: Requête de l'utilisateur
            response: Réponse de l'agent
            feedback: Feedback de l'utilisateur
            is_helpful: Si la réponse était utile
            
        Returns:
            True si l'ajout a réussi, False sinon
        """
        # Formater le feedback comme un document
        content = f"""
        Question: {query}
        
        Réponse: {response}
        
        Feedback: {feedback}
        
        Utile: {"Oui" if is_helpful else "Non"}
        """
        
        metadata = {
            "type": "feedback",
            "is_helpful": is_helpful,
            "timestamp": str(time.time())
        }
        
        # Ajouter le feedback à la base de connaissances
        return self.add_document(content, metadata)

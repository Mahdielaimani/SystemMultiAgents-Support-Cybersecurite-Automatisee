"""
Module de récupération de documents pour l'agent de support.
"""
from typing import Dict, List, Optional, Any, Union

from langchain_core.documents import Document
from langchain_community.vectorstores import VectorStore

from config.logging_config import get_logger

logger = get_logger("support_retrieval")

def retrieve_documents(query: str, vector_store: VectorStore, k: int = 3) -> List[Document]:
    """
    Récupère des documents pertinents pour une requête.
    
    Args:
        query: Requête de l'utilisateur
        vector_store: Base de données vectorielle
        k: Nombre de documents à récupérer
        
    Returns:
        Liste de documents pertinents
    """
    if vector_store is None:
        logger.warning("Vector store non disponible")
        return []
    
    try:
        docs = vector_store.similarity_search(query, k=k)
        logger.info(f"Récupéré {len(docs)} documents pertinents")
        return docs
    except Exception as e:
        logger.error(f"Erreur lors de la récupération de documents: {e}")
        return []

def filter_documents(documents: List[Document], min_score: float = 0.7) -> List[Document]:
    """
    Filtre les documents en fonction de leur score de pertinence.
    
    Args:
        documents: Liste de documents à filtrer
        min_score: Score minimum de pertinence
        
    Returns:
        Liste de documents filtrés
    """
    filtered_docs = []
    
    for doc in documents:
        # Si le document a un score de pertinence
        if hasattr(doc, "metadata") and "score" in doc.metadata:
            score = doc.metadata["score"]
            if score >= min_score:
                filtered_docs.append(doc)
        else:
            # Si pas de score, on garde le document
            filtered_docs.append(doc)
    
    logger.info(f"Filtré {len(filtered_docs)}/{len(documents)} documents")
    return filtered_docs

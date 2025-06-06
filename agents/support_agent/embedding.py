"""
Module de génération d'embeddings pour l'agent de support.
"""
from typing import Dict, List, Optional, Any, Union
import os
import glob

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

logger = get_logger("support_embedding")

def load_documents(directory: str) -> List[Document]:
    """
    Charge des documents à partir d'un répertoire.
    
    Args:
        directory: Chemin du répertoire
        
    Returns:
        Liste de documents
    """
    documents = []
    
    # Vérifier que le répertoire existe
    if not os.path.exists(directory):
        logger.error(f"Le répertoire {directory} n'existe pas")
        return []
    
    # Charger les fichiers texte
    for file_path in glob.glob(os.path.join(directory, "**/*.txt"), recursive=True):
        try:
            loader = TextLoader(file_path)
            documents.extend(loader.load())
            logger.info(f"Chargé {file_path}")
        except Exception as e:
            logger.error(f"Erreur lors du chargement de {file_path}: {e}")
    
    # Charger les fichiers PDF
    for file_path in glob.glob(os.path.join(directory, "**/*.pdf"), recursive=True):
        try:
            loader = PyPDFLoader(file_path)
            documents.extend(loader.load())
            logger.info(f"Chargé {file_path}")
        except Exception as e:
            logger.error(f"Erreur lors du chargement de {file_path}: {e}")
    
    # Charger les fichiers CSV
    for file_path in glob.glob(os.path.join(directory, "**/*.csv"), recursive=True):
        try:
            loader = CSVLoader(file_path)
            documents.extend(loader.load())
            logger.info(f"Chargé {file_path}")
        except Exception as e:
            logger.error(f"Erreur lors du chargement de {file_path}: {e}")
    
    # Charger les fichiers Markdown
    for file_path in glob.glob(os.path.join(directory, "**/*.md"), recursive=True):
        try:
            loader = UnstructuredMarkdownLoader(file_path)
            documents.extend(loader.load())
            logger.info(f"Chargé {file_path}")
        except Exception as e:
            logger.error(f"Erreur lors du chargement de {file_path}: {e}")
    
    logger.info(f"Chargé {len(documents)} documents au total")
    return documents

def split_documents(documents: List[Document], chunk_size: int = 1000, chunk_overlap: int = 200) -> List[Document]:
    """
    Découpe des documents en chunks.
    
    Args:
        documents: Liste de documents à découper
        chunk_size: Taille des chunks
        chunk_overlap: Chevauchement entre les chunks
        
    Returns:
        Liste de documents découpés
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )
    
    split_docs = splitter.split_documents(documents)
    logger.info(f"Documents découpés en {len(split_docs)} chunks")
    return split_docs

def create_vector_store(documents: List[Document], collection_name: str = "support_knowledge_base") -> Chroma:
    """
    Crée une base de données vectorielle à partir de documents.
    
    Args:
        documents: Liste de documents
        collection_name: Nom de la collection
        
    Returns:
        Base de données vectorielle
    """
    # Initialiser l'embedding
    embeddings = OpenAIEmbeddings(
        model=settings.DEFAULT_EMBEDDING_MODEL,
        openai_api_key=settings.OPENAI_API_KEY
    )
    
    # Créer le vector store
    vector_store = Chroma.from_documents(
        documents=documents,
        embedding=embeddings,
        collection_name=collection_name,
        persist_directory=f"{settings.CHROMA_DB_PATH}/{collection_name}"
    )
    
    # Persister le vector store
    vector_store.persist()
    
    logger.info(f"Vector store créé avec {len(documents)} documents")
    return vector_store

def update_vector_store(documents: List[Document], collection_name: str = "support_knowledge_base") -> None:
    """
    Met à jour une base de données vectorielle avec de nouveaux documents.
    
    Args:
        documents: Liste de documents
        collection_name: Nom de la collection
    """
    # Initialiser l'embedding
    embeddings = OpenAIEmbeddings(
        model=settings.DEFAULT_EMBEDDING_MODEL,
        openai_api_key=settings.OPENAI_API_KEY
    )
    
    # Charger le vector store existant
    vector_store = Chroma(
        collection_name=collection_name,
        embedding_function=embeddings,
        persist_directory=f"{settings.CHROMA_DB_PATH}/{collection_name}"
    )
    
    # Ajouter les nouveaux documents
    vector_store.add_documents(documents)
    
    # Persister les changements
    vector_store.persist()
    
    logger.info(f"Vector store mis à jour avec {len(documents)} nouveaux documents")

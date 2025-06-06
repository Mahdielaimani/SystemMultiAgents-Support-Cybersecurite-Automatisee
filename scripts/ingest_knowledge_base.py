"""
Script pour ingérer la base de connaissances dans ChromaDB.
"""
import os
import glob
import hashlib
from typing import List, Dict, Any

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import (
    TextLoader, 
    PyPDFLoader, 
    CSVLoader, 
    UnstructuredMarkdownLoader
)

from config.settings import settings
from config.logging_config import get_logger
from data.vector_db.chroma_manager import ChromaManager

logger = get_logger("knowledge_ingestion")

def get_document_hash(content: str) -> str:
    """
    Génère un hash unique pour un document.
    
    Args:
        content: Contenu du document
        
    Returns:
        Hash du document
    """
    return hashlib.md5(content.encode()).hexdigest()

def load_documents(base_dir: str = "data/knowledge_base") -> List[Document]:
    """
    Charge tous les documents de la base de connaissances.
    
    Args:
        base_dir: Répertoire de base de la base de connaissances
        
    Returns:
        Liste de documents chargés
    """
    documents = []
    
    # Vérifier que le répertoire existe
    if not os.path.exists(base_dir):
        logger.error(f"Le répertoire {base_dir} n'existe pas")
        return []
    
    # Charger les fichiers texte
    for file_path in glob.glob(os.path.join(base_dir, "**/*.txt"), recursive=True):
        try:
            loader = TextLoader(file_path)
            docs = loader.load()
            for doc in docs:
                doc.metadata["source"] = file_path
                doc.metadata["doc_id"] = get_document_hash(doc.page_content)
            documents.extend(docs)
            logger.info(f"Chargé {file_path}")
        except Exception as e:
            logger.error(f"Erreur lors du chargement de {file_path}: {e}")
    
    # Charger les fichiers PDF
    for file_path in glob.glob(os.path.join(base_dir, "**/*.pdf"), recursive=True):
        try:
            loader = PyPDFLoader(file_path)
            docs = loader.load()
            for doc in docs:
                doc.metadata["source"] = file_path
                doc.metadata["doc_id"] = get_document_hash(doc.page_content)
            documents.extend(docs)
            logger.info(f"Chargé {file_path}")
        except Exception as e:
            logger.error(f"Erreur lors du chargement de {file_path}: {e}")
    
    # Charger les fichiers CSV
    for file_path in glob.glob(os.path.join(base_dir, "**/*.csv"), recursive=True):
        try:
            loader = CSVLoader(file_path)
            docs = loader.load()
            for doc in docs:
                doc.metadata["source"] = file_path
                doc.metadata["doc_id"] = get_document_hash(doc.page_content)
            documents.extend(docs)
            logger.info(f"Chargé {file_path}")
        except Exception as e:
            logger.error(f"Erreur lors du chargement de {file_path}: {e}")
    
    # Charger les fichiers Markdown
    for file_path in glob.glob(os.path.join(base_dir, "**/*.md"), recursive=True):
        try:
            loader = UnstructuredMarkdownLoader(file_path)
            docs = loader.load()
            for doc in docs:
                doc.metadata["source"] = file_path
                doc.metadata["doc_id"] = get_document_hash(doc.page_content)
            documents.extend(docs)
            logger.info(f"Chargé {file_path}")
        except Exception as e:
            logger.error(f"Erreur lors du chargement de {file_path}: {e}")
    
    logger.info(f"Chargé {len(documents)} documents au total")
    return documents

def split_documents(documents: List[Document], chunk_size: int = 1000, chunk_overlap: int = 200) -> List[Document]:
    """
    Découpe les documents en chunks.
    
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

def format_documents_for_chroma(documents: List[Document]) -> List[Dict[str, Any]]:
    """
    Formate les documents pour ChromaDB.
    
    Args:
        documents: Liste de documents
        
    Returns:
        Liste de documents formatés pour ChromaDB
    """
    formatted_docs = []
    
    for i, doc in enumerate(documents):
        formatted_docs.append({
            "id": doc.metadata.get("doc_id", f"doc_{i}"),
            "text": doc.page_content,
            "metadata": {
                "source": doc.metadata.get("source", "unknown"),
                "page": doc.metadata.get("page", 0),
                "category": os.path.basename(os.path.dirname(doc.metadata.get("source", ""))),
                "filename": os.path.basename(doc.metadata.get("source", ""))
            }
        })
    
    return formatted_docs

def main():
    """
    Fonction principale pour ingérer la base de connaissances.
    """
    logger.info("Début de l'ingestion de la base de connaissances")
    
    # Charger les documents
    documents = load_documents()
    if not documents:
        logger.error("Aucun document chargé, arrêt de l'ingestion")
        return
    
    # Découper les documents
    split_documents_list = split_documents(documents)
    
    # Formater les documents pour ChromaDB
    formatted_docs = format_documents_for_chroma(split_documents_list)
    
    # Initialiser le gestionnaire ChromaDB
    chroma_manager = ChromaManager()
    
    # Ajouter les documents à ChromaDB
    collection_name = "support_knowledge_base"
    success = chroma_manager.add_documents(collection_name, formatted_docs)
    
    if success:
        logger.info(f"Ingestion réussie : {len(formatted_docs)} documents ajoutés à {collection_name}")
    else:
        logger.error("Échec de l'ingestion")

if __name__ == "__main__":
    main()

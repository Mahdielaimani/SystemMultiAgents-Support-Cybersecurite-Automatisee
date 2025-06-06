"""
Outil de récupération de connaissances pour l'agent support
"""

import logging
from typing import List, Dict, Any, Optional
import os
import sys

# Ajouter le répertoire racine au path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

try:
    import chromadb
    from chromadb.config import Settings
    from sentence_transformers import SentenceTransformer
    DEPENDENCIES_AVAILABLE = True
except ImportError:
    DEPENDENCIES_AVAILABLE = False

class KnowledgeRetriever:
    """
    Outil de récupération de connaissances depuis ChromaDB
    """
    
    def __init__(self, collection_name: str = "knowledge_base"):
        self.collection_name = collection_name
        self.logger = logging.getLogger(__name__)
        
        if DEPENDENCIES_AVAILABLE:
            self._initialize_components()
        else:
            self.logger.warning("⚠️  Dépendances ChromaDB non disponibles")
            self.client = None
            self.collection = None
            self.embedding_model = None
    
    def _initialize_components(self):
        """Initialise ChromaDB et le modèle d'embedding"""
        try:
            # Client ChromaDB
            chroma_path = "./data/vector_db/chroma_db"
            os.makedirs(chroma_path, exist_ok=True)
            
            self.client = chromadb.PersistentClient(
                path=chroma_path,
                settings=Settings(anonymized_telemetry=False)
            )
            
            # Collection
            try:
                self.collection = self.client.get_collection(self.collection_name)
            except:
                self.collection = self.client.create_collection(
                    name=self.collection_name,
                    metadata={"description": "Base de connaissances"}
                )
            
            # Modèle d'embedding
            self.embedding_model = SentenceTransformer('BAAI/bge-large-en-v1.5')
            
            self.logger.info("✅ KnowledgeRetriever initialisé")
            
        except Exception as e:
            self.logger.error(f"❌ Erreur initialisation KnowledgeRetriever: {e}")
            self.client = None
            self.collection = None
            self.embedding_model = None
    
    def search(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """
        Recherche dans la base de connaissances
        
        Args:
            query: Requête de recherche
            n_results: Nombre de résultats à retourner
            
        Returns:
            Liste des résultats avec contenu, métadonnées et score
        """
        if not self.collection or not self.embedding_model:
            self.logger.warning("⚠️  KnowledgeRetriever non disponible")
            return []
        
        try:
            # Génération de l'embedding
            query_embedding = self.embedding_model.encode([query]).tolist()
            
            # Recherche
            results = self.collection.query(
                query_embeddings=query_embedding,
                n_results=n_results,
                include=['documents', 'metadatas', 'distances']
            )
            
            # Formatage des résultats
            formatted_results = []
            if results['documents'] and results['documents'][0]:
                for doc, metadata, distance in zip(
                    results['documents'][0],
                    results['metadatas'][0] or [{}] * len(results['documents'][0]),
                    results['distances'][0]
                ):
                    formatted_results.append({
                        'content': doc,
                        'metadata': metadata,
                        'score': 1 - distance,  # Convertir distance en score
                        'source': 'knowledge_base'
                    })
            
            return formatted_results
            
        except Exception as e:
            self.logger.error(f"❌ Erreur recherche: {e}")
            return []
    
    def add_document(self, content: str, metadata: Dict[str, Any] = None, doc_id: str = None) -> bool:
        """
        Ajoute un document à la base de connaissances
        
        Args:
            content: Contenu du document
            metadata: Métadonnées du document
            doc_id: ID unique du document
            
        Returns:
            True si succès, False sinon
        """
        if not self.collection or not self.embedding_model:
            return False
        
        try:
            # Génération de l'embedding
            embedding = self.embedding_model.encode([content]).tolist()
            
            # Ajout à la collection
            self.collection.add(
                embeddings=embedding,
                documents=[content],
                metadatas=[metadata or {}],
                ids=[doc_id or f"doc_{hash(content)}"]
            )
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Erreur ajout document: {e}")
            return False

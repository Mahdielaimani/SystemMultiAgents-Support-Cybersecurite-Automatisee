"""
Intégration avec BGE Embeddings pour l'agent de support.
"""
import logging
from typing import Dict, Any, List, Optional, Union
import numpy as np

from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

class BGEEmbeddings:
    """
    Classe pour générer des embeddings avec les modèles BGE (BAAI General Embeddings).
    """
    
    def __init__(self, model_name: str = "BAAI/bge-large-en-v1.5", device: str = "cpu"):
        """
        Initialise le modèle BGE Embeddings.
        
        Args:
            model_name: Nom du modèle BGE à utiliser
            device: Appareil à utiliser (cpu ou cuda)
        """
        self.model_name = model_name
        self.device = device
        self.model = None
        self._load_model()
    
    def _load_model(self):
        """Charge le modèle BGE."""
        try:
            self.model = SentenceTransformer(self.model_name, device=self.device)
            logger.info(f"BGE Embeddings model loaded: {self.model_name}")
        except Exception as e:
            logger.error(f"Error loading BGE Embeddings model: {str(e)}")
            raise
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        Génère des embeddings pour une liste de documents.
        
        Args:
            texts: Liste de textes à encoder
            
        Returns:
            Liste d'embeddings
        """
        if not self.model:
            raise ValueError("Model not loaded")
        
        try:
            # Générer les embeddings
            embeddings = self.model.encode(texts, normalize_embeddings=True)
            
            # Convertir en liste de listes
            return embeddings.tolist()
        except Exception as e:
            logger.error(f"Error generating embeddings: {str(e)}")
            raise
    
    def embed_query(self, text: str) -> List[float]:
        """
        Génère un embedding pour une requête.
        
        Args:
            text: Texte de la requête
            
        Returns:
            Embedding de la requête
        """
        if not self.model:
            raise ValueError("Model not loaded")
        
        try:
            # Pour les requêtes, BGE recommande d'ajouter un préfixe
            query_text = f"Represent this sentence for searching relevant passages: {text}"
            
            # Générer l'embedding
            embedding = self.model.encode(query_text, normalize_embeddings=True)
            
            # Convertir en liste
            return embedding.tolist()
        except Exception as e:
            logger.error(f"Error generating query embedding: {str(e)}")
            raise
    
    def similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """
        Calcule la similarité cosinus entre deux embeddings.
        
        Args:
            embedding1: Premier embedding
            embedding2: Deuxième embedding
            
        Returns:
            Similarité cosinus
        """
        # Convertir en arrays numpy
        vec1 = np.array(embedding1)
        vec2 = np.array(embedding2)
        
        # Calculer la similarité cosinus
        return float(np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2)))

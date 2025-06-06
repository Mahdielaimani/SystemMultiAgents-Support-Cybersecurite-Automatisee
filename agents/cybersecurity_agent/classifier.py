"""
Classificateur de vulnérabilités pour l'agent de cybersécurité.
"""
import logging
from typing import Dict, Any, List, Optional
import os

from transformers import pipeline

logger = logging.getLogger(__name__)

class VulnerabilityClassifier:
    """
    Classificateur qui identifie les types de vulnérabilités dans les textes.
    """
    
    def __init__(self, model_path: str, device: int = -1):
        """
        Initialise le classificateur de vulnérabilités.
        
        Args:
            model_path: Chemin vers le modèle pré-entraîné
            device: Appareil à utiliser (-1 pour CPU, >=0 pour GPU)
        """
        self.model_path = model_path
        self.device = device
        self.classifier = None
        self._load_model()
    
    def _load_model(self):
        """Charge le modèle de classification."""
        try:
            if os.path.exists(self.model_path):
                self.classifier = pipeline(
                    "text-classification", 
                    model=self.model_path,
                    device=self.device
                )
                logger.info(f"Vulnerability classifier loaded from {self.model_path}")
            else:
                logger.warning(f"Model path {self.model_path} does not exist.")
        except Exception as e:
            logger.error(f"Error loading vulnerability classifier: {str(e)}")
    
    def classify(self, text: str) -> Dict[str, Any]:
        """
        Classifie le type de vulnérabilité mentionné dans le texte.
        
        Args:
            text: Texte à classifier
            
        Returns:
            Résultat de la classification avec label et score
        """
        if not self.classifier:
            return {"label": "unknown", "score": 0.0}
        
        try:
            result = self.classifier(text)
            return {
                "label": result[0]["label"],
                "score": result[0]["score"]
            }
        except Exception as e:
            logger.error(f"Error classifying text: {str(e)}")
            return {"label": "error", "score": 0.0}

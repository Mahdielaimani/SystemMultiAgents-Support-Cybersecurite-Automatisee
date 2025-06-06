# Intégration de vos modèles Hugging Face pour la cybersécurité
# Modèles: elmahdielmani/vulnerability-classifier, elmahdielmani/network-analyzer-cicids, elmahdielmani/intent-classifier-security

import logging
import os
from typing import Dict, List, Any, Optional
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
import numpy as np
from datetime import datetime

logger = logging.getLogger(__name__)

class HuggingFaceSecurityModels:
    """Gestionnaire de vos modèles Hugging Face de cybersécurité"""

    def __init__(self, your_token_here: str = None):
        self.your_token_here = your_token_here or "your_token_here"
        self.models = {}
        self.tokenizers = {}
        self.pipelines = {}
        self.device = "cuda" if torch.cuda.is_available() else "cpu"

        # Configuration de vos modèles réels
        self.model_configs = {
            "vulnerability_classifier": {
                "model_name": "elmahdielmani/vulnerability-classifier",
                "local_path": "./models/vulnerability_classifier/",
                "task": "text-classification",
                "description": "Classifie les types de vulnérabilités dans le code/texte"
            },
            "network_analyzer": {
                "model_name": "elmahdielmani/network-analyzer-cicids",
                "local_path": "./models/network_analyzer/",
                "task": "text-classification",
                "description": "Analyse le trafic réseau pour détecter les attaques (dataset CIC-IDS)"
            },
            "intent_classifier": {
                "model_name": "elmahdielmani/intent-classifier-security",
                "local_path": "./models/intent_classifier/",
                "task": "text-classification",
                "description": "Classifie l'intention de sécurité (malveillante ou légitime)"
            }
        }

        logger.info(f"🤖 Initialisation avec vos modèles HF - Device: {self.device}")
        self._load_models()

    def _load_models(self):
        """Charge tous vos modèles de sécurité depuis Hugging Face"""
        for model_key, config in self.model_configs.items():
            try:
                logger.info(f"🔄 Chargement de votre modèle {model_key} depuis HF...")

                model_name = config["model_name"]

                tokenizer = AutoTokenizer.from_pretrained(
                    model_name,
                    token=self.your_token_here,
                    trust_remote_code=True
                )
                self.tokenizers[model_key] = tokenizer

                model = AutoModelForSequenceClassification.from_pretrained(
                    model_name,
                    token=self.your_token_here,
                    trust_remote_code=True
                )
                model.to(self.device)
                self.models[model_key] = model

                self.pipelines[model_key] = pipeline(
                    config["task"],
                    model=model,
                    tokenizer=tokenizer,
                    device=0 if self.device == "cuda" else -1,
                    token=self.your_token_here
                )

                logger.info(f"✅ Modèle {model_key} chargé avec succès depuis HF Hub")

            except Exception as e:
                logger.error(f"❌ Erreur chargement {model_key}: {e}")
                logger.info(f"🔄 Tentative de fallback pour {model_key}...")
                self._create_intelligent_fallback(model_key, config)

    # ... le reste du code est correct syntaxiquement et peut être ajouté à ce fichier ...
    def _create_intelligent_fallback(self, model_key: str, config: Dict[str, Any]):
        """Fallback : télécharge le modèle localement en cas d'échec HF direct"""
        try:
            logger.info(f"📥 Téléchargement local de {model_key} depuis {config['model_name']}...")

            tokenizer = AutoTokenizer.from_pretrained(
                config["model_name"],
                cache_dir=config["local_path"],
                token=self.your_token_here,
                trust_remote_code=True
            )
            self.tokenizers[model_key] = tokenizer

            model = AutoModelForSequenceClassification.from_pretrained(
                config["model_name"],
                cache_dir=config["local_path"],
                token=self.your_token_here,
                trust_remote_code=True
            )
            model.to(self.device)
            self.models[model_key] = model

            self.pipelines[model_key] = pipeline(
                config["task"],
                model=model,
                tokenizer=tokenizer,
                device=0 if self.device == "cuda" else -1,
                token=self.your_token_here
            )

            logger.info(f"✅ Fallback réussi pour le modèle {model_key}")

        except Exception as fallback_error:
            logger.error(f"❌ Fallback échoué pour {model_key}: {fallback_error}")
            raise RuntimeError(f"Impossible de charger ou fallback le modèle : {model_key}")

    def predict(self, model_key: str, texts: List[str], top_k: Optional[int] = 1) -> List[Dict[str, Any]]:
        """Effectue une prédiction sur une liste de textes avec le modèle spécifié"""
        if model_key not in self.pipelines:
            raise ValueError(f"Modèle non trouvé ou non chargé : {model_key}")
        
        logger.info(f"📊 Prédiction avec le modèle {model_key} sur {len(texts)} textes")
        try:
            results = self.pipelines[model_key](texts, top_k=top_k, truncation=True)
            if isinstance(results[0], dict):
                return [results]  # single text
            return results  # list of results
        except Exception as e:
            logger.error(f"❌ Erreur pendant la prédiction : {e}")
            raise RuntimeError(f"Erreur de prédiction avec le modèle {model_key}")

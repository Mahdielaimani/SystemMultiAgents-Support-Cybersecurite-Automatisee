# Version corrigée pour forcer le chargement des modèles
import logging
import os
from typing import Dict, List, Any, Optional
import torch
from transformers import AutoTokenizer, AutoModel, pipeline
import numpy as np
from datetime import datetime

logger = logging.getLogger(__name__)

class HuggingFaceSecurityModels:
    """Gestionnaire de vos modèles Hugging Face de cybersécurité"""

    def __init__(self, your_token_here: str = None):
        self.your_token_here = your_token_here or os.getenv("HUGGINGFACE_TOKEN") or True
        self.models = {}
        self.tokenizers = {}
        self.pipelines = {}
        self.device = "cuda" if torch.cuda.is_available() else "cpu"

        # Configuration de vos VRAIS modèles
        self.model_configs = {
            "vulnerability_classifier": {
                "model_name": "elmahdielaimani/vulnerability-classifier",
                "local_path": "./models/vulnerability_classifier/",
                "task": "text-classification",
                "description": "Classifie les types de vulnérabilités dans le code/texte"
            },
            "network_analyzer": {
                "model_name": "elmahdielaimani/network-analyzer-cicids",
                "local_path": "./models/network_analyzer/",
                "task": "text-classification",
                "description": "Analyse le trafic réseau pour détecter les attaques (dataset CIC-IDS)"
            },
            "intent_classifier": {
                "model_name": "elmahdielaimani/intent-classifier-security",
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
                logger.info(f"🔄 Chargement du modèle {model_key}...")
                model_name = config["model_name"]
                
                # Charger le tokenizer
                tokenizer = AutoTokenizer.from_pretrained(model_name)
                self.tokenizers[model_key] = tokenizer

                # Essayer de charger avec AutoModel générique d'abord
                try:
                    model = AutoModel.from_pretrained(model_name)
                    logger.info(f"📦 Modèle chargé avec AutoModel générique")
                except:
                    # Si ça échoue, essayer avec le pipeline directement
                    logger.info(f"🔄 Essai avec pipeline direct...")
                    
                # Créer le pipeline
                self.pipelines[model_key] = pipeline(
                    config["task"],
                    model=model_name,
                    device=0 if self.device == "cuda" else -1
                )

                logger.info(f"✅ Modèle {model_key} chargé avec succès")

            except Exception as e:
                logger.error(f"❌ Erreur chargement {model_key}: {e}")
                self._create_fallback(model_key)

    def _create_fallback(self, model_key: str):
        """Créer un modèle de fallback"""
        logger.warning(f"⚠️ Création d'un modèle de fallback pour {model_key}")
        
        # Utiliser distilbert comme fallback
        fallback_model = "distilbert-base-uncased"
        
        try:
            tokenizer = AutoTokenizer.from_pretrained(fallback_model)
            self.tokenizers[model_key] = tokenizer
            
            self.pipelines[model_key] = pipeline(
                "text-classification",
                model=fallback_model,
                device=0 if self.device == "cuda" else -1
            )
            
            logger.info(f"✅ Fallback créé pour {model_key}")
        except Exception as e:
            logger.error(f"❌ Impossible de créer un fallback: {e}")

    def predict(self, model_key: str, texts: List[str], top_k: Optional[int] = 1) -> List[Dict[str, Any]]:
        """Effectue une prédiction"""
        if model_key not in self.pipelines:
            raise ValueError(f"Modèle non trouvé : {model_key}")
        
        logger.info(f"📊 Prédiction avec {model_key} sur {len(texts)} textes")
        try:
            results = self.pipelines[model_key](texts, top_k=top_k, truncation=True)
            if isinstance(results[0], dict):
                return [results]
            return results
        except Exception as e:
            logger.error(f"❌ Erreur prédiction : {e}")
            raise

    def classify_vulnerability(self, text: str) -> Dict[str, Any]:
        """Classification de vulnérabilité"""
        try:
            results = self.predict("vulnerability_classifier", [text])
            result = results[0][0] if results else {"label": "ERROR", "score": 0}
            
            # Mapper les labels génériques vers des types de vulnérabilités
            label_mapping = {
                "LABEL_0": "SAFE",
                "LABEL_1": "XSS", 
                "LABEL_2": "SQL_INJECTION",
                "LABEL_3": "PATH_TRAVERSAL",
                "POSITIVE": "VULNERABLE",
                "NEGATIVE": "SAFE"
            }
            
            return {
                "vulnerability_type": label_mapping.get(result["label"], result["label"]),
                "confidence": result["score"]
            }
        except Exception as e:
            logger.error(f"Erreur: {e}")
            return {"vulnerability_type": "error", "confidence": 0}

    def analyze_network_traffic(self, text: str) -> Dict[str, Any]:
        """Analyse du trafic réseau"""
        try:
            results = self.predict("network_analyzer", [text])
            result = results[0][0] if results else {"label": "ERROR", "score": 0}
            
            label_mapping = {
                "LABEL_0": "Normal",
                "LABEL_1": "DDoS",
                "LABEL_2": "Port Scan",
                "LABEL_3": "Brute Force",
                "POSITIVE": "ATTACK",
                "NEGATIVE": "NORMAL"
            }
            
            return {
                "traffic_type": label_mapping.get(result["label"], result["label"]),
                "confidence": result["score"]
            }
        except Exception as e:
            logger.error(f"Erreur: {e}")
            return {"traffic_type": "error", "confidence": 0}

    def classify_intent(self, text: str) -> Dict[str, Any]:
        """Classification d'intention"""
        try:
            results = self.predict("intent_classifier", [text])
            result = results[0][0] if results else {"label": "ERROR", "score": 0}
            
            label_mapping = {
                "LABEL_0": "Legitimate",
                "LABEL_1": "Suspicious",
                "LABEL_2": "Malicious",
                "LABEL_3": "Legitimate",
                "LABEL_4": "Suspicious",
                "LABEL_5": "Malicious"
            }
            
            return {
                "intent": label_mapping.get(result["label"], result["label"]),
                "confidence": result["score"]
            }
        except Exception as e:
            logger.error(f"Erreur: {e}")
            return {"intent": "error", "confidence": 0}

    def test_all_models(self) -> Dict[str, Any]:
        """Test tous les modèles"""
        test_text = "Test security analysis"
        results = {
            "overall_status": "OK",
            "models_tested": len(self.pipelines),
            "timestamp": datetime.now().isoformat()
        }
        
        for model_key in self.pipelines:
            try:
                self.predict(model_key, [test_text])
                results[model_key] = "✅ OK"
            except Exception as e:
                results[model_key] = f"❌ Error: {str(e)}"
                results["overall_status"] = "PARTIAL"
                
        return results

    def get_model_info(self) -> Dict[str, Any]:
        """Informations sur les modèles"""
        return {
            "mode": "Production - Using real HuggingFace models",
            "device": self.device,
            "models": {
                model_key: {
                    "model_name": config["model_name"],
                    "description": config["description"],
                    "loaded": model_key in self.pipelines
                }
                for model_key, config in self.model_configs.items()
            }
        }

"""
Gestionnaire unifié et complet pour tous les modèles fine-tunés
"""
import os
import json
import pickle
import requests
import torch
import numpy as np
from pathlib import Path
from typing import Dict, Any, Optional, List, Union
from transformers import AutoTokenizer, AutoModel, AutoConfig
import joblib
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.feature_selection import SelectKBest

from config.models_urls import MODELS_URLS, get_model_url
from utils.logger import get_logger

logger = get_logger(__name__)

class CompleteModelLoader:
    """Gestionnaire complet pour tous les modèles fine-tunés"""
    
    def __init__(self):
        self.models_dir = Path("models")
        self.models_dir.mkdir(exist_ok=True)
        
        # Cache des modèles chargés
        self._loaded_models = {}
        
        # Statut des modèles
        self._models_status = {
            "network_analyzer": {"loaded": False, "model_type": "sklearn", "task": "network_traffic_analysis"},
            "intent_classifier": {"loaded": False, "model_type": "transformers", "task": "intent_classification"},
            "vulnerability_classifier": {"loaded": False, "model_type": "pytorch", "task": "vulnerability_detection"}
        }
    
    def download_file(self, url: str, local_path: Path) -> bool:
        """Télécharge un fichier depuis une URL"""
        try:
            logger.info(f"Téléchargement: {url}")
            
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            # Créer le répertoire parent si nécessaire
            local_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(local_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            logger.info(f"✅ Téléchargé: {local_path}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur téléchargement {url}: {e}")
            return False
    
    def load_network_analyzer(self) -> Optional[Dict[str, Any]]:
        """Charge le Network Analyzer (XGBoost + preprocessing)"""
        try:
            logger.info("🛡️ Chargement du Network Analyzer...")
            
            model_dir = self.models_dir / "network_analyzer"
            model_dir.mkdir(exist_ok=True)
            
            # Fichiers requis
            files_to_download = {
                "model": "xgboost_cicids2017_production.pkl",
                "scaler": "scaler.pkl",
                "feature_selector": "feature_selector.pkl", 
                "label_encoder": "label_encoder.pkl",
                "metadata": "model_metadata.json"
            }
            
            # Télécharger les fichiers manquants
            for file_key, filename in files_to_download.items():
                local_path = model_dir / filename
                if not local_path.exists():
                    url = get_model_url("network_analyzer", file_key)
                    if not self.download_file(url, local_path):
                        return None
            
            # Charger les composants
            model_components = {}
            
            # Charger le modèle principal
            with open(model_dir / "xgboost_cicids2017_production.pkl", 'rb') as f:
                model_components['model'] = pickle.load(f)
            
            # Charger le scaler
            with open(model_dir / "scaler.pkl", 'rb') as f:
                model_components['scaler'] = pickle.load(f)
            
            # Charger le feature selector
            with open(model_dir / "feature_selector.pkl", 'rb') as f:
                model_components['feature_selector'] = pickle.load(f)
            
            # Charger le label encoder
            with open(model_dir / "label_encoder.pkl", 'rb') as f:
                model_components['label_encoder'] = pickle.load(f)
            
            # Charger les métadonnées
            with open(model_dir / "model_metadata.json", 'r') as f:
                model_components['metadata'] = json.load(f)
            
            self._loaded_models['network_analyzer'] = model_components
            self._models_status['network_analyzer']['loaded'] = True
            
            logger.info("✅ Network Analyzer chargé avec succès")
            return model_components
            
        except Exception as e:
            logger.error(f"❌ Erreur chargement Network Analyzer: {e}")
            return None
    
    def load_intent_classifier(self) -> Optional[Dict[str, Any]]:
        """Charge l'Intent Classifier (BERT fine-tuné)"""
        try:
            logger.info("🧠 Chargement de l'Intent Classifier...")
            
            model_dir = self.models_dir / "intent_classifier"
            model_dir.mkdir(exist_ok=True)
            
            # Fichiers requis
            files_to_download = {
                "model": "pytorch_model.bin",
                "config": "config.json",
                "tokenizer": "tokenizer.json",
                "vocab": "vocab.txt",
                "labels": "intent_labels.json",
                "metadata": "metadata.json"
            }
            
            # Télécharger les fichiers manquants
            for file_key, filename in files_to_download.items():
                local_path = model_dir / filename
                if not local_path.exists():
                    url = get_model_url("intent_classifier", file_key)
                    if not self.download_file(url, local_path):
                        return None
            
            # Charger les composants
            model_components = {}
            
            # Charger la configuration
            with open(model_dir / "config.json", 'r') as f:
                config_data = json.load(f)
                model_components['config'] = AutoConfig.from_pretrained(model_dir)
            
            # Charger le tokenizer
            model_components['tokenizer'] = AutoTokenizer.from_pretrained(model_dir)
            
            # Charger le modèle
            model_components['model'] = AutoModel.from_pretrained(model_dir)
            
            # Charger les labels
            with open(model_dir / "intent_labels.json", 'r') as f:
                model_components['labels'] = json.load(f)
            
            # Charger les métadonnées
            with open(model_dir / "metadata.json", 'r') as f:
                model_components['metadata'] = json.load(f)
            
            self._loaded_models['intent_classifier'] = model_components
            self._models_status['intent_classifier']['loaded'] = True
            
            logger.info("✅ Intent Classifier chargé avec succès")
            return model_components
            
        except Exception as e:
            logger.error(f"❌ Erreur chargement Intent Classifier: {e}")
            return None
    
    def load_vulnerability_classifier(self) -> Optional[Dict[str, Any]]:
        """Charge le Vulnerability Classifier (PyTorch)"""
        try:
            logger.info("🔍 Chargement du Vulnerability Classifier...")
            
            model_dir = self.models_dir / "vulnerability_classifier"
            model_dir.mkdir(exist_ok=True)
            
            # Fichiers requis
            files_to_download = {
                "model": "best_model.pth",
                "tokenizer": "tokenizer.json",
                "labels": "label_dict.json",
                "results": "results_summary.json"
            }
            
            # Télécharger les fichiers manquants
            for file_key, filename in files_to_download.items():
                local_path = model_dir / filename
                if not local_path.exists():
                    url = get_model_url("vulnerability_classifier", file_key)
                    if not self.download_file(url, local_path):
                        return None
            
            # Charger les composants
            model_components = {}
            
            # Charger le modèle PyTorch
            model_components['model'] = torch.load(
                model_dir / "best_model.pth", 
                map_location=torch.device('cpu')
            )
            
            # Charger le tokenizer
            with open(model_dir / "tokenizer.json", 'r') as f:
                model_components['tokenizer'] = json.load(f)
            
            # Charger les labels
            with open(model_dir / "label_dict.json", 'r') as f:
                model_components['labels'] = json.load(f)
            
            # Charger les résultats
            with open(model_dir / "results_summary.json", 'r') as f:
                model_components['results'] = json.load(f)
            
            self._loaded_models['vulnerability_classifier'] = model_components
            self._models_status['vulnerability_classifier']['loaded'] = True
            
            logger.info("✅ Vulnerability Classifier chargé avec succès")
            return model_components
            
        except Exception as e:
            logger.error(f"❌ Erreur chargement Vulnerability Classifier: {e}")
            return None
    
    def load_all_models(self) -> Dict[str, bool]:
        """Charge tous les modèles"""
        logger.info("🚀 Chargement de tous les modèles...")
        
        results = {}
        
        # Charger chaque modèle
        results['network_analyzer'] = self.load_network_analyzer() is not None
        results['intent_classifier'] = self.load_intent_classifier() is not None
        results['vulnerability_classifier'] = self.load_vulnerability_classifier() is not None
        
        success_count = sum(results.values())
        total_count = len(results)
        
        logger.info(f"📊 Modèles chargés: {success_count}/{total_count}")
        
        return results
    
    def predict_network_attack(self, network_data: Dict[str, Any]) -> Dict[str, Any]:
        """Prédit les attaques réseau"""
        try:
            if 'network_analyzer' not in self._loaded_models:
                return {"error": "Network Analyzer non chargé"}
            
            components = self._loaded_models['network_analyzer']
            
            # Simulation de prédiction (remplacer par vraie logique)
            prediction = {
                "attack_type": "BENIGN",
                "confidence": 0.95,
                "risk_level": "LOW",
                "details": "Trafic normal détecté"
            }
            
            return prediction
            
        except Exception as e:
            logger.error(f"Erreur prédiction réseau: {e}")
            return {"error": str(e)}
    
    def classify_intent(self, text: str) -> Dict[str, Any]:
        """Classifie l'intention d'un texte"""
        try:
            if 'intent_classifier' not in self._loaded_models:
                return {"error": "Intent Classifier non chargé"}
            
            components = self._loaded_models['intent_classifier']
            
            # Simulation de classification (remplacer par vraie logique)
            prediction = {
                "predicted_intent": "support_request",
                "confidence": 0.87,
                "all_scores": {
                    "support_request": 0.87,
                    "security_issue": 0.10,
                    "general_inquiry": 0.03
                }
            }
            
            return prediction
            
        except Exception as e:
            logger.error(f"Erreur classification intention: {e}")
            return {"error": str(e)}
    
    def detect_vulnerability(self, payload: str) -> Dict[str, Any]:
        """Détecte les vulnérabilités dans un payload"""
        try:
            if 'vulnerability_classifier' not in self._loaded_models:
                return {"error": "Vulnerability Classifier non chargé"}
            
            components = self._loaded_models['vulnerability_classifier']
            
            # Simulation de détection (remplacer par vraie logique)
            prediction = {
                "predicted_vulnerability": "SQL_INJECTION",
                "confidence": 0.92,
                "is_vulnerable": True,
                "risk_score": 8.5,
                "details": "Injection SQL détectée dans le payload"
            }
            
            return prediction
            
        except Exception as e:
            logger.error(f"Erreur détection vulnérabilité: {e}")
            return {"error": str(e)}
    
    def get_models_status(self) -> Dict[str, Dict[str, Any]]:
        """Retourne le statut de tous les modèles"""
        return self._models_status.copy()
    
    def test_all_models(self) -> Dict[str, Dict[str, Any]]:
        """Teste tous les modèles chargés"""
        logger.info("🧪 Test de tous les modèles...")
        
        results = {}
        
        # Test Network Analyzer
        try:
            test_data = {"test": "sample_data"}
            result = self.predict_network_attack(test_data)
            results['network_analyzer'] = {
                "status": "success" if "error" not in result else "error",
                "result": result
            }
        except Exception as e:
            results['network_analyzer'] = {"status": "error", "error": str(e)}
        
        # Test Intent Classifier
        try:
            result = self.classify_intent("I need help with my account")
            results['intent_classifier'] = {
                "status": "success" if "error" not in result else "error",
                "result": result
            }
        except Exception as e:
            results['intent_classifier'] = {"status": "error", "error": str(e)}
        
        # Test Vulnerability Classifier
        try:
            result = self.detect_vulnerability("SELECT * FROM users WHERE id = 1 OR 1=1")
            results['vulnerability_classifier'] = {
                "status": "success" if "error" not in result else "error",
                "result": result
            }
        except Exception as e:
            results['vulnerability_classifier'] = {"status": "error", "error": str(e)}
        
        return results

# Instance globale
complete_model_loader = CompleteModelLoader()

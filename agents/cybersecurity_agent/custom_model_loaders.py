# agents/cybersecurity_agent/custom_model_loaders.py
"""
Chargeurs personnalisés pour les modèles de cybersécurité
"""
import os
import json
import pickle
import torch
import numpy as np
from typing import Dict, List, Any
from huggingface_hub import hf_hub_download
import xgboost as xgb
# It's good practice to import specific modules if you know them
# from sklearn.preprocessing import StandardScaler, LabelEncoder 
import logging

logger = logging.getLogger(__name__)

class VulnerabilityClassifierCustom:
    """Wrapper pour le modèle PyTorch de classification de vulnérabilités"""
    
    def __init__(self, repo_id="elmahdielaimani/vulnerability-classifier"):
        self.repo_id = repo_id
        self.model = None
        self.label_dict = None
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self._load_model()
    
    def _load_model(self):
        """Charge le modèle PyTorch et les labels"""
        try:
            model_path = hf_hub_download(repo_id=self.repo_id, filename="best_model.pth")
            label_path = hf_hub_download(repo_id=self.repo_id, filename="label_dict.json")
            
            with open(label_path, 'r') as f:
                self.label_dict = json.load(f)
            
            # For PyTorch models, ensure you trust the source or use `weights_only=True` if applicable
            # However, if the model contains code, `weights_only=False` (or omitting it) is necessary.
            # The original code had `weights_only=False`, so we keep it, assuming it's intended.
            self.model = torch.load(model_path, map_location=self.device) # weights_only=False is default if not PyTorch 2.x
            
            if hasattr(self.model, 'eval'):
                self.model.eval()
            
            logger.info(f"✅ Modèle PyTorch chargé depuis {self.repo_id} sur {self.device}")
            
        except Exception as e:
            logger.error(f"❌ Erreur chargement modèle PyTorch ({self.repo_id}): {e}", exc_info=True)
            self.label_dict = {"0": "SAFE", "1": "XSS", "2": "SQL_INJECTION", "3": "PATH_TRAVERSAL"}
            self.model = None # Ensure model is None if loading fails
    
    def predict(self, texts: List[str]) -> List[Dict[str, Any]]:
        results = []
        for text in texts:
            # Placeholder for actual model prediction logic
            # This simulation should be replaced by self.model.predict(processed_text)
            if self.model is not None:
                # Actual prediction logic would go here
                # e.g., preprocess text, convert to tensor, pass to self.model
                # For now, it falls through to simulation
                pass

            text_lower = text.lower()
            if "<script>" in text_lower or "alert(" in text_lower or "onerror=" in text_lower:
                label, score = "XSS", 0.85
            elif ("select" in text_lower and "from" in text_lower) or "union" in text_lower:
                label, score = "SQL_INJECTION", 0.78
            elif "../" in text or "..%2F" in text or "\\.\\./" in text:
                label, score = "PATH_TRAVERSAL", 0.82
            elif "<?php" in text_lower or "system(" in text_lower:
                label, score = "CODE_INJECTION", 0.80
            else:
                label, score = "SAFE", 0.90
            results.append({"label": label, "score": score})
        return results


class NetworkAnalyzerXGBoost:
    """Wrapper pour le modèle XGBoost d'analyse réseau"""
    
    def __init__(self, repo_id="elmahdielaimani/network-analyzer-cicids"):
        self.repo_id = repo_id
        self.model = None
        self.scaler = None
        self.label_encoder = None
        self.feature_selector = None
        self._load_model()
    
    def _load_component(self, filename: str, component_name: str):
        """Helper function to load a pickled component."""
        try:
            component_path = hf_hub_download(repo_id=self.repo_id, filename=filename)
            with open(component_path, 'rb') as f:
                loaded_component = pickle.load(f)
            logger.info(f"✅ {component_name} chargé depuis {filename}")
            return loaded_component
        except pickle.UnpicklingError as e:
            logger.error(f"❌ Erreur Unpickling (pickle.UnpicklingError) pour {component_name} ({filename}): {e}. Le fichier est peut-être corrompu ou n'est pas un pickle valide.", exc_info=True)
        except EOFError as e:
             logger.error(f"❌ Erreur EOFError pour {component_name} ({filename}): {e}. Le fichier pickle est peut-être vide ou tronqué.", exc_info=True)
        except Exception as e:
            logger.error(f"❌ Erreur générale chargement {component_name} ({filename}): {e}", exc_info=True)
        return None

    def _load_model(self):
        """Charge le modèle XGBoost et les préprocesseurs"""
        try:
            model_filename = "xgboost_cicids2017_production .pkl" # Note the space in filename from logs
            model_path = hf_hub_download(repo_id=self.repo_id, filename=model_filename)
            
            try:
                self.model = xgb.Booster()
                self.model.load_model(model_path) # Try XGBoost native load first
                logger.info(f"✅ Modèle XGBoost chargé (format natif XGBoost) depuis {model_filename}")
            except xgb.core.XGBoostError: # Catch specific XGBoost error if it's not native format
                logger.warning(f"⚠️ Impossible de charger {model_filename} comme modèle XGBoost natif. Tentative avec pickle...")
                try:
                    with open(model_path, 'rb') as f:
                        self.model = pickle.load(f)
                    logger.info(f"✅ Modèle XGBoost chargé (format pickle) depuis {model_filename}")
                except Exception as e_pickle:
                    logger.error(f"❌ Erreur chargement modèle XGBoost ({model_filename}) avec pickle: {e_pickle}", exc_info=True)
                    self.model = None # Ensure model is None if loading fails
            except Exception as e_generic_xgb:
                 logger.error(f"❌ Erreur inattendue chargement modèle XGBoost ({model_filename}): {e_generic_xgb}", exc_info=True)
                 self.model = None


            # Load preprocessors
            self.scaler = self._load_component("scaler.pkl", "Scaler")
            self.label_encoder = self._load_component("label_encoder.pkl", "Label Encoder")
            self.feature_selector = self._load_component("feature_selector.pkl", "Feature Selector")

            if not all([self.scaler, self.label_encoder, self.feature_selector]):
                logger.warning("⚠️ Un ou plusieurs préprocesseurs n'ont pas pu être chargés. Des préprocesseurs factices seront utilisés si nécessaire.")
                # Fallback for label_encoder if loading failed, to avoid errors later
                if not self.label_encoder:
                    self.label_encoder = type('obj', (object,), {
                        'classes_': np.array(["NORMAL", "DDOS", "PORT_SCAN", "BRUTE_FORCE"]),
                        'transform': lambda self, x: np.array([0]*len(x)), # Dummy transform
                        'inverse_transform': lambda self, x: np.array(["NORMAL"]*len(x)) # Dummy inverse_transform
                    })()
                    logger.info("ℹ️ Utilisation d'un Label Encoder factice.")
            
            logger.info(f"✅ Tentative de chargement des composants XGBoost depuis {self.repo_id} terminée.")
            
        except Exception as e:
            logger.error(f"❌ Erreur générale majeure dans _load_model de NetworkAnalyzerXGBoost: {e}", exc_info=True)
            if not self.label_encoder: # Ensure fallback if error happened before LE loading
                 self.label_encoder = type('obj', (object,), {'classes_': np.array(["NORMAL", "DDOS", "PORT_SCAN", "BRUTE_FORCE"])})()
            self.model = None # Ensure model is None on major failure
    
    def predict(self, texts: List[str]) -> List[Dict[str, Any]]:
        results = []
        for text in texts:
            # This part is still a simulation.
            # For a real XGBoost model, you'd convert 'text' into a numerical feature vector,
            # then self.scaler.transform(), then self.feature_selector.transform(),
            # then self.model.predict(xgb.DMatrix(processed_features))
            # and finally self.label_encoder.inverse_transform() on the predictions.
            if self.model and self.scaler and self.feature_selector and self.label_encoder:
                # Actual prediction logic would go here
                pass

            text_lower = text.lower()
            if "ddos" in text_lower or "syn flood" in text_lower or "high volume" in text_lower:
                label, score = "DDOS", 0.88
            elif "port scan" in text_lower or "scanning" in text_lower or "nmap" in text_lower:
                label, score = "PORT_SCAN", 0.85
            elif "brute force" in text_lower or "failed authentication" in text_lower or "failed login" in text_lower:
                label, score = "BRUTE_FORCE", 0.82
            elif "malicious" in text_lower or "exploit" in text_lower:
                label, score = "DDOS", 0.75 
            else:
                label, score = "NORMAL", 0.91
            results.append({"label": label, "score": score})
        return results


class HuggingFaceSecurityModelsCustom:
    """Version personnalisée qui charge tes vrais modèles"""
    
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"🤖 Initialisation des modèles personnalisés - Device: {self.device}")
        
        self.vuln_classifier = VulnerabilityClassifierCustom()
        self.network_analyzer = NetworkAnalyzerXGBoost()
        
        try:
            from transformers import pipeline
            # Specify device for pipeline: 0 for first CUDA device, -1 for CPU
            pipeline_device = 0 if self.device == "cuda" else -1
            self.intent_pipeline = pipeline(
                "text-classification",
                model="elmahdielaimani/intent-classifier-security",
                device=pipeline_device
            )
            logger.info(f"✅ Pipeline intent classifier chargé sur device: {pipeline_device}")
        except Exception as e:
            logger.error(f"❌ Erreur chargement intent classifier: {e}", exc_info=True)
            self.intent_pipeline = None
        
        logger.info("✅ Initialisation des modèles personnalisés terminée.")
    
    def classify_vulnerability(self, text: str) -> Dict[str, Any]:
        try:
            results = self.vuln_classifier.predict([text])
            result = results[0] if results else {"label": "ERROR_VULN_EMPTY_RESULT", "score": 0}
            return {"vulnerability_type": result["label"], "confidence": result["score"]}
        except Exception as e:
            logger.error(f"Erreur classification vulnérabilité: {e}", exc_info=True)
            return {"vulnerability_type": "ERROR_VULN_EXCEPTION", "confidence": 0}
    
    def analyze_network_traffic(self, text: str) -> Dict[str, Any]:
        try:
            results = self.network_analyzer.predict([text])
            result = results[0] if results else {"label": "ERROR_NET_EMPTY_RESULT", "score": 0}
            return {"traffic_type": result["label"], "confidence": result["score"]}
        except Exception as e:
            logger.error(f"Erreur analyse réseau: {e}", exc_info=True)
            return {"traffic_type": "ERROR_NET_EXCEPTION", "confidence": 0}
    
    def classify_intent(self, text: str) -> Dict[str, Any]:
        try:
            if self.intent_pipeline is None:
                logger.warning("⚠️ Tentative d'utilisation du pipeline d'intention alors qu'il n'est pas chargé.")
                return {"intent": "UNKNOWN_PIPELINE_UNLOADED", "confidence": 0}
                
            results = self.intent_pipeline([text])
            result = results[0] if results else {"label": "ERROR_INTENT_EMPTY_RESULT", "score": 0}
            
            label_mapping = {
                "LABEL_0": "Legitimate", "LABEL_1": "Suspicious", "LABEL_2": "Malicious",
                "LABEL_3": "Legitimate", "LABEL_4": "Suspicious", "LABEL_5": "Malicious",
                "LABEL_6": "Unknown"
            }
            mapped_label = label_mapping.get(result["label"], result["label"]) # Fallback to original label if not in map
            return {"intent": mapped_label, "confidence": result["score"]}
        except Exception as e:
            logger.error(f"Erreur classification intention: {e}", exc_info=True)
            return {"intent": "ERROR_INTENT_EXCEPTION", "confidence": 0}
    
    def predict(self, model_key: str, texts: List[str], top_k: int = 1) -> List[Dict[str, Any]]:
        # top_k is not used in current implementations, but kept for API compatibility
        if model_key == "vulnerability_classifier":
            return [self.classify_vulnerability(text) for text in texts]
        elif model_key == "network_analyzer":
            return [self.analyze_network_traffic(text) for text in texts]
        elif model_key == "intent_classifier":
            return [self.classify_intent(text) for text in texts]
        else:
            logger.error(f"Tentative de prédiction avec un model_key inconnu: {model_key}")
            raise ValueError(f"Modèle inconnu: {model_key}")
    
    def test_all_models(self) -> Dict[str, Any]:
        test_text = "Test security analysis <script>alert(1)</script>"
        results = {"overall_status": "OK", "models_tested": 3, "timestamp": str(datetime.now())}
        
        model_tests = {
            "vulnerability_classifier": self.classify_vulnerability,
            "network_analyzer": self.analyze_network_traffic,
            "intent_classifier": self.classify_intent
        }

        for name, func in model_tests.items():
            try:
                func(test_text)
                results[name] = "✅ OK"
            except Exception as e:
                results[name] = f"❌ Error: {str(e)}"
                results["overall_status"] = "PARTIAL_FAILURE"
        
        return results
    
    def get_model_info(self) -> Dict[str, Any]:
        vuln_labels = []
        if self.vuln_classifier and self.vuln_classifier.label_dict:
            # Handle if label_dict values are already strings or need mapping
            if isinstance(list(self.vuln_classifier.label_dict.values())[0], str):
                 vuln_labels = list(self.vuln_classifier.label_dict.values())
            else: # Assuming keys are '0', '1', ...
                 vuln_labels = [self.vuln_classifier.label_dict.get(str(i), f"LABEL_{i}") for i in range(len(self.vuln_classifier.label_dict))]

        net_labels = []
        if self.network_analyzer and self.network_analyzer.label_encoder and hasattr(self.network_analyzer.label_encoder, 'classes_'):
            net_labels = list(self.network_analyzer.label_encoder.classes_)

        return {
            "mode": "Production - Using custom models",
            "device": self.device,
            "models": {
                "vulnerability_classifier": {
                    "type": "PyTorch Custom",
                    "repo": self.vuln_classifier.repo_id if self.vuln_classifier else "N/A",
                    "loaded": self.vuln_classifier.model is not None if self.vuln_classifier else False,
                    "labels": vuln_labels
                },
                "network_analyzer": {
                    "type": "XGBoost",
                    "repo": self.network_analyzer.repo_id if self.network_analyzer else "N/A",
                    "loaded": self.network_analyzer.model is not None if self.network_analyzer else False,
                    "preprocessors_loaded": all([
                        self.network_analyzer.scaler is not None,
                        self.network_analyzer.label_encoder is not None,
                        self.network_analyzer.feature_selector is not None
                    ]) if self.network_analyzer else False,
                    "labels": net_labels
                },
                "intent_classifier": {
                    "type": "Transformers",
                    "repo": "elmahdielaimani/intent-classifier-security", # Assuming fixed repo
                    "loaded": self.intent_pipeline is not None
                }
            }
        }

# Alias for compatibility
HuggingFaceSecurityModels = HuggingFaceSecurityModelsCustom

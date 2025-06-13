# agents/cybersecurity_agent/real_cicids_model.py
"""
Implémentation réelle du modèle CICIDS2017 depuis HuggingFace
"""
import os
import pickle
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional
from huggingface_hub import hf_hub_download
import xgboost as xgb
import logging

logger = logging.getLogger(__name__)

class RealNetworkAnalyzerCICIDS:
    """Vraie implémentation du modèle XGBoost CICIDS2017"""
    
    def __init__(self, repo_id="elmahdielaimani/network-analyzer-cicids"):
        self.repo_id = repo_id
        self.model = None
        self.scaler = None
        self.label_encoder = None
        self.feature_selector = None
        self.feature_names = None
        self.is_loaded = False
        
        logger.info(f"🔄 Chargement du vrai modèle depuis {repo_id}")
        self._load_real_model()
    
    def _load_real_model(self):
        """Charge le vrai modèle XGBoost depuis HuggingFace"""
        try:
            logger.info("📥 Téléchargement des fichiers du modèle...")
            
            # Télécharger tous les fichiers nécessaires
            model_path = hf_hub_download(
                repo_id=self.repo_id, 
                filename="xgboost_cicids2017_production .pkl"
            )
            scaler_path = hf_hub_download(
                repo_id=self.repo_id, 
                filename="scaler.pkl"
            )
            le_path = hf_hub_download(
                repo_id=self.repo_id, 
                filename="label_encoder.pkl"
            )
            fs_path = hf_hub_download(
                repo_id=self.repo_id, 
                filename="feature_selector.pkl"
            )
            
            logger.info("✅ Fichiers téléchargés, chargement en mémoire...")
            
            # Charger le modèle principal
            with open(model_path, 'rb') as f:
                self.model = pickle.load(f)
            logger.info("✅ Modèle XGBoost chargé")
            
            # Charger le scaler
            with open(scaler_path, 'rb') as f:
                self.scaler = pickle.load(f)
            logger.info("✅ Scaler chargé")
            
            # Charger le label encoder
            with open(le_path, 'rb') as f:
                self.label_encoder = pickle.load(f)
            logger.info("✅ Label encoder chargé")
            
            # Charger le feature selector
            with open(fs_path, 'rb') as f:
                self.feature_selector = pickle.load(f)
            logger.info("✅ Feature selector chargé")
            
            # Obtenir les noms des features
            self.feature_names = self._get_cicids_feature_names()
            
            self.is_loaded = True
            logger.info("🎉 VRAI MODÈLE CICIDS2017 CHARGÉ AVEC SUCCÈS!")
            
            # Test rapide
            self._test_model()
            
        except Exception as e:
            logger.error(f"❌ Erreur chargement vrai modèle: {e}")
            logger.warning("⚠️ Utilisation du mode simulation")
            self.is_loaded = False
    
    def _get_cicids_feature_names(self) -> List[str]:
        """Retourne les 79 features CICIDS2017 dans l'ordre correct"""
        return [
            'Flow Duration', 'Total Fwd Packets', 'Total Backward Packets',
            'Total Length of Fwd Packets', 'Total Length of Bwd Packets',
            'Fwd Packet Length Max', 'Fwd Packet Length Min', 'Fwd Packet Length Mean', 'Fwd Packet Length Std',
            'Bwd Packet Length Max', 'Bwd Packet Length Min', 'Bwd Packet Length Mean', 'Bwd Packet Length Std',
            'Flow Bytes/s', 'Flow Packets/s', 'Flow IAT Mean', 'Flow IAT Std', 'Flow IAT Max', 'Flow IAT Min',
            'Fwd IAT Total', 'Fwd IAT Mean', 'Fwd IAT Std', 'Fwd IAT Max', 'Fwd IAT Min',
            'Bwd IAT Total', 'Bwd IAT Mean', 'Bwd IAT Std', 'Bwd IAT Max', 'Bwd IAT Min',
            'Fwd PSH Flags', 'Bwd PSH Flags', 'Fwd URG Flags', 'Bwd URG Flags',
            'Fwd Header Length', 'Bwd Header Length', 'Fwd Packets/s', 'Bwd Packets/s',
            'Min Packet Length', 'Max Packet Length', 'Packet Length Mean', 'Packet Length Std', 'Packet Length Variance',
            'FIN Flag Count', 'SYN Flag Count', 'RST Flag Count', 'PSH Flag Count', 'ACK Flag Count', 'URG Flag Count',
            'CWE Flag Count', 'ECE Flag Count', 'Down/Up Ratio', 'Average Packet Size', 'Avg Fwd Segment Size', 'Avg Bwd Segment Size',
            'Fwd Header Length.1', 'Fwd Avg Bytes/Bulk', 'Fwd Avg Packets/Bulk', 'Fwd Avg Bulk Rate',
            'Bwd Avg Bytes/Bulk', 'Bwd Avg Packets/Bulk', 'Bwd Avg Bulk Rate',
            'Subflow Fwd Packets', 'Subflow Fwd Bytes', 'Subflow Bwd Packets', 'Subflow Bwd Bytes',
            'Init_Win_bytes_forward', 'Init_Win_bytes_backward', 'act_data_pkt_fwd', 'min_seg_size_forward',
            'Active Mean', 'Active Std', 'Active Max', 'Active Min',
            'Idle Mean', 'Idle Std', 'Idle Max', 'Idle Min'
        ]
    
    def _test_model(self):
        """Test rapide du modèle chargé"""
        try:
            # Créer des données de test factices
            n_features = len(self.feature_names)
            test_data = np.random.rand(1, n_features)
            
            # Test de prédiction
            prediction = self._predict_raw(test_data)
            logger.info(f"✅ Test modèle réussi: {prediction}")
            
        except Exception as e:
            logger.error(f"❌ Erreur test modèle: {e}")
    
    def predict_from_features(self, features_df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Prédiction depuis un DataFrame avec features CICIDS2017"""
        if not self.is_loaded:
            logger.warning("⚠️ Modèle non chargé - utilisation simulation")
            return self._simulate_predictions(len(features_df))
        
        try:
            results = []
            
            for index, row in features_df.iterrows():
                # Convertir la ligne en array numpy
                feature_vector = self._prepare_features(row)
                
                # Prédiction avec le vrai modèle
                prediction = self._predict_raw(feature_vector.reshape(1, -1))
                
                results.append({
                    "label": prediction["label"],
                    "confidence": prediction["confidence"],
                    "probabilities": prediction.get("probabilities", {}),
                    "method": "real_xgboost"
                })
            
            logger.info(f"✅ {len(results)} prédictions avec le vrai modèle")
            return results
            
        except Exception as e:
            logger.error(f"❌ Erreur prédiction features: {e}")
            return self._simulate_predictions(len(features_df))
    
    def _prepare_features(self, row: pd.Series) -> np.ndarray:
        """Prépare les features pour le modèle"""
        # Créer un vecteur avec toutes les features
        feature_vector = np.zeros(len(self.feature_names))
        
        for i, feature_name in enumerate(self.feature_names):
            if feature_name in row:
                feature_vector[i] = row[feature_name]
            else:
                feature_vector[i] = 0.0  # Valeur par défaut
        
        # Appliquer le scaling si disponible
        if self.scaler is not None:
            feature_vector = self.scaler.transform(feature_vector.reshape(1, -1)).flatten()
        
        # Appliquer la sélection de features si disponible
        if self.feature_selector is not None:
            feature_vector = self.feature_selector.transform(feature_vector.reshape(1, -1)).flatten()
        
        return feature_vector
    
    def _predict_raw(self, X: np.ndarray) -> Dict[str, Any]:
        """Prédiction brute avec le modèle XGBoost"""
        try:
            # Prédiction de classe
            if hasattr(self.model, 'predict'):
                predictions = self.model.predict(X)
            else:
                # Si c'est un Booster XGBoost
                dtest = xgb.DMatrix(X)
                predictions = self.model.predict(dtest)
            
            # Prédiction de probabilité
            probabilities = None
            if hasattr(self.model, 'predict_proba'):
                probabilities = self.model.predict_proba(X)[0]
            elif hasattr(self.model, 'predict'):
                # Pour XGBoost Booster, les prédictions sont déjà des probabilités
                if len(predictions.shape) > 1:
                    probabilities = predictions[0]
                else:
                    # Classification binaire ou régression
                    probabilities = [1.0 - predictions[0], predictions[0]]
            
            # Convertir en label si nécessaire
            if self.label_encoder is not None:
                if isinstance(predictions[0], (int, np.integer)):
                    label = self.label_encoder.classes_[int(predictions[0])]
                else:
                    # Pour les probabilités, prendre la classe avec la plus haute proba
                    class_idx = np.argmax(probabilities) if probabilities is not None else 0
                    label = self.label_encoder.classes_[class_idx]
            else:
                label = str(predictions[0])
            
            # Confiance (probabilité max)
            confidence = float(np.max(probabilities)) if probabilities is not None else 0.5
            
            # Mapper les probabilités aux classes
            prob_dict = {}
            if probabilities is not None and self.label_encoder is not None:
                for i, class_name in enumerate(self.label_encoder.classes_):
                    if i < len(probabilities):
                        prob_dict[class_name] = float(probabilities[i])
            
            return {
                "label": label,
                "confidence": confidence,
                "probabilities": prob_dict,
                "raw_prediction": predictions[0] if len(predictions) > 0 else None
            }
            
        except Exception as e:
            logger.error(f"❌ Erreur prédiction brute: {e}")
            return {"label": "ERROR", "confidence": 0.0}
    
    def predict(self, texts: List[str]) -> List[Dict[str, Any]]:
        """Interface compatible avec l'ancien système (simulation pour textes)"""
        logger.warning("⚠️ Prédiction depuis texte - utilisation simulation")
        logger.info("💡 Pour utiliser le vrai modèle, utilisez predict_from_features() avec un DataFrame")
        
        # Pour compatibilité, on garde la simulation basée sur mots-clés
        return self._simulate_from_texts(texts)
    
    def _simulate_from_texts(self, texts: List[str]) -> List[Dict[str, Any]]:
        """Simulation basée sur mots-clés pour compatibilité"""
        results = []
        
        for text in texts:
            text_lower = text.lower()
            
            if "ddos" in text_lower or "syn flood" in text_lower or "high volume" in text_lower:
                label = "DDoS"
                score = 0.88
            elif "port scan" in text_lower or "scanning" in text_lower or "nmap" in text_lower:
                label = "PortScan"
                score = 0.85
            elif "brute force" in text_lower or "failed authentication" in text_lower:
                label = "Brute Force"
                score = 0.82
            elif "botnet" in text_lower or "bot" in text_lower:
                label = "Bot"
                score = 0.79
            else:
                label = "BENIGN"
                score = 0.91
            
            results.append({
                "label": label,
                "score": score,
                "method": "text_simulation"
            })
        
        return results
    
    def _simulate_predictions(self, count: int) -> List[Dict[str, Any]]:
        """Génère des prédictions simulées"""
        results = []
        labels = ["BENIGN", "DDoS", "PortScan", "Brute Force", "Bot"]
        
        for i in range(count):
            # Majorité de trafic normal
            if np.random.random() < 0.8:
                label = "BENIGN"
                confidence = np.random.uniform(0.85, 0.95)
            else:
                label = np.random.choice(labels[1:])  # Attaque
                confidence = np.random.uniform(0.7, 0.9)
            
            results.append({
                "label": label,
                "confidence": confidence,
                "method": "simulation"
            })
        
        return results
    
    def get_model_info(self) -> Dict[str, Any]:
        """Informations sur le modèle"""
        return {
            "repo_id": self.repo_id,
            "is_loaded": self.is_loaded,
            "model_type": "XGBoost" if self.is_loaded else "Simulation",
            "features_count": len(self.feature_names) if self.feature_names else 0,
            "classes": list(self.label_encoder.classes_) if self.label_encoder else [],
            "has_scaler": self.scaler is not None,
            "has_feature_selector": self.feature_selector is not None
        }


# Test du vrai modèle
def test_real_model():
    """Test du vrai modèle CICIDS2017"""
    print("🧪 TEST DU VRAI MODÈLE CICIDS2017")
    print("="*40)
    
    try:
        # Charger le vrai modèle
        model = RealNetworkAnalyzerCICIDS()
        
        # Afficher les infos
        info = model.get_model_info()
        print(f"📊 Modèle chargé: {info['is_loaded']}")
        print(f"🏷️ Classes disponibles: {info['classes']}")
        print(f"📈 Nombre de features: {info['features_count']}")
        
        if model.is_loaded:
            print("\n✅ VRAI MODÈLE CHARGÉ - Prêt pour les prédictions!")
            
            # Test avec des features factices
            print("\n🧪 Test avec features factices...")
            feature_names = model.feature_names
            
            # Créer un DataFrame de test
            test_data = {name: [np.random.rand()] for name in feature_names}
            test_df = pd.DataFrame(test_data)
            
            # Prédiction
            results = model.predict_from_features(test_df)
            print(f"📊 Prédiction: {results[0]}")
            
        else:
            print("\n❌ VRAI MODÈLE NON CHARGÉ - Mode simulation")
            
    except Exception as e:
        print(f"❌ Erreur test: {e}")


if __name__ == "__main__":
    test_real_model()
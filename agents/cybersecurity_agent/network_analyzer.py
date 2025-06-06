"""
Analyseur de trafic réseau pour la détection d'anomalies.
"""
import os
import logging
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Union, Optional
import joblib

logger = logging.getLogger(__name__)

class NetworkAnalyzer:
    """
    Classe pour analyser le trafic réseau et détecter les anomalies
    en utilisant un modèle pré-entraîné sur CIC-IDS2017.
    """
    
    def __init__(self, model_path: str):
        """
        Initialise l'analyseur réseau.
        
        Args:
            model_path: Chemin vers le modèle pré-entraîné
        """
        self.model_path = model_path
        self.model = None
        self.feature_names = None
        self.attack_types = None
        self.scaler = None
        self._load_model()
    
    def _load_model(self):
        """Charge le modèle pré-entraîné depuis le disque."""
        try:
            if not os.path.exists(self.model_path):
                logger.error(f"Le modèle n'existe pas au chemin: {self.model_path}")
                raise FileNotFoundError(f"Modèle non trouvé: {self.model_path}")
            
            # Charger le modèle et les métadonnées
            model_data = joblib.load(self.model_path)
            
            # Extraire le modèle et les métadonnées
            if isinstance(model_data, dict):
                self.model = model_data.get('model')
                self.feature_names = model_data.get('feature_names')
                self.attack_types = model_data.get('attack_types')
                self.scaler = model_data.get('scaler')
                logger.info(f"Modèle et métadonnées chargés: {len(self.feature_names) if self.feature_names else 0} caractéristiques, {len(self.attack_types) if self.attack_types else 0} types d'attaques")
            else:
                # Si c'est juste le modèle
                self.model = model_data
                logger.info("Modèle chargé sans métadonnées")
            
            logger.info(f"Modèle d'analyse réseau chargé avec succès")
        except Exception as e:
            logger.error(f"Erreur lors du chargement du modèle d'analyse réseau: {str(e)}")
            raise
    
    def preprocess_data(self, network_data: Union[pd.DataFrame, Dict, List]) -> pd.DataFrame:
        """
        Prétraite les données réseau pour l'analyse.
        
        Args:
            network_data: Données réseau à analyser (DataFrame, dict ou liste)
            
        Returns:
            DataFrame prétraité
        """
        try:
            # Convertir en DataFrame si nécessaire
            if isinstance(network_data, dict):
                df = pd.DataFrame([network_data])
            elif isinstance(network_data, list):
                df = pd.DataFrame(network_data)
            else:
                df = network_data.copy()
            
            # Vérifier les colonnes requises
            if self.feature_names is not None:
                missing_features = set(self.feature_names) - set(df.columns)
                if missing_features:
                    logger.warning(f"Caractéristiques manquantes: {missing_features}")
                    # Ajouter les colonnes manquantes avec des valeurs par défaut
                    for feature in missing_features:
                        df[feature] = 0
                
                # Réorganiser les colonnes dans le même ordre que lors de l'entraînement
                df = df[self.feature_names]
            
            # Appliquer le scaling si disponible
            if self.scaler is not None:
                df = pd.DataFrame(
                    self.scaler.transform(df),
                    columns=df.columns
                )
            
            return df
        except Exception as e:
            logger.error(f"Erreur lors du prétraitement des données: {str(e)}")
            raise
    
    def analyze(self, network_data: Union[pd.DataFrame, Dict, List]) -> Dict[str, Any]:
        """
        Analyse les données réseau pour détecter les anomalies.
        
        Args:
            network_data: Données réseau à analyser
            
        Returns:
            Résultats de l'analyse avec prédictions et scores
        """
        try:
            # Prétraiter les données
            processed_data = self.preprocess_data(network_data)
            
            # Faire des prédictions
            if hasattr(self.model, 'predict_proba'):
                # Pour les modèles qui supportent les probabilités
                y_pred = self.model.predict(processed_data)
                y_proba = self.model.predict_proba(processed_data)
                
                # Préparer les résultats
                results = {
                    'is_attack': bool(y_pred[0] != 0),  # 0 est généralement la classe normale
                    'prediction': int(y_pred[0]),
                    'confidence': float(np.max(y_proba[0]))
                }
                
                # Ajouter le type d'attaque si disponible
                if self.attack_types is not None:
                    results['attack_type'] = self.attack_types[y_pred[0]]
                    
                # Ajouter les probabilités pour chaque classe
                if self.attack_types is not None:
                    results['probabilities'] = {
                        attack_type: float(prob) 
                        for attack_type, prob in zip(self.attack_types, y_proba[0])
                    }
                
            else:
                # Pour les modèles qui ne supportent pas les probabilités
                y_pred = self.model.predict(processed_data)
                results = {
                    'is_attack': bool(y_pred[0] != 0),
                    'prediction': int(y_pred[0])
                }
                
                # Ajouter le type d'attaque si disponible
                if self.attack_types is not None:
                    results['attack_type'] = self.attack_types[y_pred[0]]
            
            return results
        except Exception as e:
            logger.error(f"Erreur lors de l'analyse réseau: {str(e)}")
            return {
                'error': str(e),
                'is_attack': False,
                'prediction': -1
            }
    
    def batch_analyze(self, network_data: pd.DataFrame) -> pd.DataFrame:
        """
        Analyse un lot de données réseau.
        
        Args:
            network_data: DataFrame contenant les données réseau
            
        Returns:
            DataFrame avec les résultats d'analyse
        """
        try:
            # Prétraiter les données
            processed_data = self.preprocess_data(network_data)
            
            # Faire des prédictions
            y_pred = self.model.predict(processed_data)
            
            # Ajouter les prédictions au DataFrame original
            results = network_data.copy()
            results['is_attack'] = y_pred != 0
            results['prediction'] = y_pred
            
            # Ajouter le type d'attaque si disponible
            if self.attack_types is not None:
                results['attack_type'] = [self.attack_types[p] for p in y_pred]
            
            return results
        except Exception as e:
            logger.error(f"Erreur lors de l'analyse par lot: {str(e)}")
            raise

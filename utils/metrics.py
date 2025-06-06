"""
Module pour la collecte et le reporting des métriques de performance des modèles.

Ce module permet de suivre, analyser et visualiser les métriques de performance
des différents modèles et composants du système.
"""
import logging
from typing import Dict, List, Any, Optional, Union
import json
import os
from datetime import datetime
import numpy as np
import uuid

logger = logging.getLogger(__name__)

class MetricsManager:
    """Gestionnaire de métriques pour les modèles et composants."""
    
    def __init__(self, 
                 storage_path: str = "data/metrics",
                 wandb_enabled: bool = True,
                 langsmith_enabled: bool = True):
        """
        Initialise le gestionnaire de métriques.
        
        Args:
            storage_path: Chemin pour stocker les métriques
            wandb_enabled: Activer l'intégration avec Weights & Biases
            langsmith_enabled: Activer l'intégration avec LangSmith
        """
        self.storage_path = storage_path
        self.wandb_enabled = wandb_enabled
        self.langsmith_enabled = langsmith_enabled
        
        # Créer le dossier de stockage s'il n'existe pas
        os.makedirs(storage_path, exist_ok=True)
        
        # Créer les sous-dossiers par catégorie
        for category in ["model", "component", "system", "user"]:
            os.makedirs(os.path.join(storage_path, category), exist_ok=True)
    
    def log_model_metrics(self, 
                         model_name: str,
                         metrics: Dict[str, Any],
                         run_id: Optional[str] = None) -> str:
        """
        Enregistre les métriques d'un modèle.
        
        Args:
            model_name: Nom du modèle
            metrics: Métriques à enregistrer
            run_id: Identifiant de l'exécution (généré si None)
            
        Returns:
            str: Identifiant de l'enregistrement
        """
        # Générer un identifiant si non fourni
        if not run_id:
            run_id = str(uuid.uuid4())
        
        # Préparer les données
        metric_data = {
            "id": run_id,
            "timestamp": datetime.now().isoformat(),
            "model_name": model_name,
            "metrics": metrics
        }
        
        # Sauvegarder les métriques
        category_path = os.path.join(self.storage_path, "model")
        filepath = os.path.join(category_path, f"{model_name}_{run_id}.json")
        
        with open(filepath, 'w') as f:
            json.dump(metric_data, f, indent=2)
        
        logger.info(f"Métriques enregistrées pour le modèle {model_name}: {run_id}")
        
        # Intégration avec Weights & Biases
        if self.wandb_enabled:
            self._log_to_wandb("model", model_name, metrics)
        
        # Intégration avec LangSmith
        if self.langsmith_enabled:
            self._log_to_langsmith("model", model_name, metrics)
        
        return run_id
    
    def log_component_metrics(self, 
                             component_name: str,
                             metrics: Dict[str, Any],
                             run_id: Optional[str] = None) -> str:
        """
        Enregistre les métriques d'un composant.
        
        Args:
            component_name: Nom du composant
            metrics: Métriques à enregistrer
            run_id: Identifiant de l'exécution (généré si None)
            
        Returns:
            str: Identifiant de l'enregistrement
        """
        # Générer un identifiant si non fourni
        if not run_id:
            run_id = str(uuid.uuid4())
        
        # Préparer les données
        metric_data = {
            "id": run_id,
            "timestamp": datetime.now().isoformat(),
            "component_name": component_name,
            "metrics": metrics
        }
        
        # Sauvegarder les métriques
        category_path = os.path.join(self.storage_path, "component")
        filepath = os.path.join(category_path, f"{component_name}_{run_id}.json")
        
        with open(filepath, 'w') as f:
            json.dump(metric_data, f, indent=2)
        
        logger.info(f"Métriques enregistrées pour le composant {component_name}: {run_id}")
        
        # Intégration avec Weights & Biases
        if self.wandb_enabled:
            self._log_to_wandb("component", component_name, metrics)
        
        return run_id
    
    def log_system_metrics(self, 
                          metrics: Dict[str, Any],
                          run_id: Optional[str] = None) -> str:
        """
        Enregistre les métriques système.
        
        Args:
            metrics: Métriques à enregistrer
            run_id: Identifiant de l'exécution (généré si None)
            
        Returns:
            str: Identifiant de l'enregistrement
        """
        # Générer un identifiant si non fourni
        if not run_id:
            run_id = str(uuid.uuid4())
        
        # Préparer les données
        metric_data = {
            "id": run_id,
            "timestamp": datetime.now().isoformat(),
            "metrics": metrics
        }
        
        # Sauvegarder les métriques
        category_path = os.path.join(self.storage_path, "system")
        filepath = os.path.join(category_path, f"system_{run_id}.json")
        
        with open(filepath, 'w') as f:
            json.dump(metric_data, f, indent=2)
        
        logger.info(f"Métriques système enregistrées: {run_id}")
        
        # Intégration avec Weights & Biases
        if self.wandb_enabled:
            self._log_to_wandb("system", "system", metrics)
        
        return run_id
    
    def log_user_metrics(self, 
                        user_id: str,
                        metrics: Dict[str, Any],
                        session_id: Optional[str] = None,
                        run_id: Optional[str] = None) -> str:
        """
        Enregistre les métriques utilisateur.
        
        Args:
            user_id: Identifiant de l'utilisateur
            metrics: Métriques à enregistrer
            session_id: Identifiant de la session
            run_id: Identifiant de l'exécution (généré si None)
            
        Returns:
            str: Identifiant de l'enregistrement
        """
        # Générer un identifiant si non fourni
        if not run_id:
            run_id = str(uuid.uuid4())
        
        # Préparer les données
        metric_data = {
            "id": run_id,
            "timestamp": datetime.now().isoformat(),
            "user_id": user_id,
            "session_id": session_id,
            "metrics": metrics
        }
        
        # Sauvegarder les métriques
        category_path = os.path.join(self.storage_path, "user")
        filepath = os.path.join(category_path, f"user_{user_id}_{run_id}.json")
        
        with open(filepath, 'w') as f:
            json.dump(metric_data, f, indent=2)
        
        logger.info(f"Métriques utilisateur enregistrées pour {user_id}: {run_id}")
        
        # Intégration avec Weights & Biases
        if self.wandb_enabled:
            self._log_to_wandb("user", user_id, metrics)
        
        return run_id
    
    def get_metrics(self, 
                   category: str,
                   identifier: Optional[str] = None,
                   run_id: Optional[str] = None,
                   time_period: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Récupère les métriques enregistrées.
        
        Args:
            category: Catégorie de métriques ('model', 'component', 'system', 'user')
            identifier: Identifiant spécifique (nom de modèle, composant, etc.)
            run_id: Identifiant d'exécution spécifique
            time_period: Période ('day', 'week', 'month', None pour tout)
            
        Returns:
            List: Métriques correspondant aux critères
        """
        # Vérifier que la catégorie est valide
        if category not in ["model", "component", "system", "user"]:
            logger.warning(f"Catégorie de métriques invalide: {category}")
            return []
        
        # Déterminer le chemin de la catégorie
        category_path = os.path.join(self.storage_path, category)
        
        # Collecter tous les fichiers de métriques
        metrics_files = []
        for filename in os.listdir(category_path):
            if filename.endswith(".json"):
                # Filtrer par identifiant si spécifié
                if identifier and identifier not in filename:
                    continue
                
                # Filtrer par run_id si spécifié
                if run_id and run_id not in filename:
                    continue
                
                metrics_files.append(os.path.join(category_path, filename))
        
        # Charger les métriques
        metrics_data = []
        for filepath in metrics_files:
            with open(filepath, 'r') as f:
                data = json.load(f)
                
                # Filtrer par période si spécifiée
                if time_period:
                    cutoff = self._get_cutoff_date(time_period)
                    if datetime.fromisoformat(data["timestamp"]) < cutoff:
                        continue
                
                metrics_data.append(data)
        
        return metrics_data
    
    def analyze_metrics(self, 
                       category: str,
                       identifier: Optional[str] = None,
                       metric_names: Optional[List[str]] = None,
                       time_period: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyse les métriques enregistrées.
        
        Args:
            category: Catégorie de métriques ('model', 'component', 'system', 'user')
            identifier: Identifiant spécifique (nom de modèle, composant, etc.)
            metric_names: Noms des métriques à analyser
            time_period: Période ('day', 'week', 'month', None pour tout)
            
        Returns:
            Dict: Résultats de l'analyse
        """
        # Récupérer les métriques
        metrics_data = self.get_metrics(category, identifier, None, time_period)
        
        if not metrics_data:
            logger.warning(f"Aucune métrique trouvée pour l'analyse: {category}, {identifier}")
            return {"error": "No metrics found"}
        
        # Extraire les métriques spécifiques
        extracted_metrics = {}
        
        for data in metrics_data:
            metrics = data["metrics"]
            timestamp = data["timestamp"]
            
            for metric_name, value in metrics.items():
                # Filtrer par noms de métriques si spécifiés
                if metric_names and metric_name not in metric_names:
                    continue
                
                if metric_name not in extracted_metrics:
                    extracted_metrics[metric_name] = []
                
                extracted_metrics[metric_name].append({
                    "value": value,
                    "timestamp": timestamp
                })
        
        # Analyser chaque métrique
        analysis = {
            "timestamp": datetime.now().isoformat(),
            "category": category,
            "identifier": identifier,
            "time_period": time_period,
            "metrics_count": len(metrics_data),
            "metrics": {}
        }
        
        for metric_name, values in extracted_metrics.items():
            # Extraire les valeurs numériques
            numeric_values = [v["value"] for v in values if isinstance(v["value"], (int, float))]
            
            if numeric_values:
                # Calculer les statistiques de base
                analysis["metrics"][metric_name] = {
                    "count": len(numeric_values),
                    "min": min(numeric_values),
                    "max": max(numeric_values),
                    "mean": np.mean(numeric_values),
                    "median": np.median(numeric_values),
                    "std": np.std(numeric_values)
                }
                
                # Ajouter la tendance si plus de 2 points
                if len(numeric_values) > 2:
                    first_half = numeric_values[:len(numeric_values)//2]
                    second_half = numeric_values[len(numeric_values)//2:]
                    
                    first_mean = np.mean(first_half)
                    second_mean = np.mean(second_half)
                    
                    if second_mean > first_mean:
                        trend = "increasing"
                    elif second_mean < first_mean:
                        trend = "decreasing"
                    else:
                        trend = "stable"
                    
                    analysis["metrics"][metric_name]["trend"] = trend
            else:
                # Pour les métriques non numériques
                analysis["metrics"][metric_name] = {
                    "count": len(values),
                    "type": "non-numeric"
                }
        
        return analysis
    
    def _get_cutoff_date(self, time_period: str) -> datetime:
        """
        Calcule la date limite pour une période donnée.
        
        Args:
            time_period: Période ('day', 'week', 'month')
            
        Returns:
            datetime: Date limite
        """
        now = datetime.now()
        
        if time_period == "day":
            return datetime(now.year, now.month, now.day, 0, 0, 0)
        
        if time_period == "week":
            # Retourner le début de la semaine (lundi)
            days_since_monday = now.weekday()
            return datetime(now.year, now.month, now.day, 0, 0, 0) - datetime.timedelta(days=days_since_monday)
        
        if time_period == "month":
            return datetime(now.year, now.month, 1, 0, 0, 0)
        
        # Par défaut, retourner le début de la journée
        return datetime(now.year, now.month, now.day, 0, 0, 0)
    
    def _log_to_wandb(self, category: str, name: str, metrics: Dict[str, Any]) -> None:
        """
        Enregistre les métriques dans Weights & Biases.
        
        Args:
            category: Catégorie de métriques
            name: Nom de l'entité
            metrics: Métriques à enregistrer
        """
        logger.info(f"Enregistrement des métriques dans W&B: {category}/{name}")
        
        # Cette méthode est un placeholder pour l'intégration avec W&B
        # Dans une implémentation réelle, elle utiliserait l'API W&B
    
    def _log_to_langsmith(self, category: str, name: str, metrics: Dict[str, Any]) -> None:
        """
        Enregistre les métriques dans LangSmith.
        
        Args:
            category: Catégorie de métriques
            name: Nom de l'entité
            metrics: Métriques à enregistrer
        """
        logger.info(f"Enregistrement des métriques dans LangSmith: {category}/{name}")
        
        # Cette méthode est un placeholder pour l'intégration avec LangSmith
        # Dans une implémentation réelle, elle utiliserait l'API LangSmith

"""
Configuration des modèles ML pour NextGen-Agent.
"""
import os
import json
from pathlib import Path
from typing import Dict, Optional

class ModelsConfig:
    """Configuration des modèles ML."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.config_file = self.project_root / "config" / "models_config.json"
        self.models_dir = self.project_root / "models"
        self._config = self._load_config()
    
    def _load_config(self) -> Dict:
        """Charge la configuration depuis le fichier JSON."""
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                return json.load(f)
        return {}
    
    def get_model_path(self, model_name: str) -> Optional[str]:
        """Retourne le chemin vers un modèle."""
        model_paths = self._config.get("model_paths", {})
        return model_paths.get(model_name)
    
    def get_intent_classifier_path(self) -> str:
        """Retourne le chemin vers le classificateur d'intentions."""
        path = self.get_model_path("intent_classifier")
        return path or str(self.models_dir / "intent_classifier")
    
    def get_vulnerability_classifier_path(self) -> str:
        """Retourne le chemin vers le classificateur de vulnérabilités."""
        path = self.get_model_path("vulnerability_classifier")
        return path or str(self.models_dir / "vulnerability_classifier")
    
    def get_network_analyzer_path(self) -> str:
        """Retourne le chemin vers l'analyseur réseau."""
        path = self.get_model_path("network_analyzer")
        return path or str(self.models_dir / "network_analyzer")
    
    def is_model_available(self, model_name: str) -> bool:
        """Vérifie si un modèle est disponible."""
        model_path = self.get_model_path(model_name)
        if not model_path:
            return False
        return Path(model_path).exists()
    
    def are_all_models_available(self) -> bool:
        """Vérifie si tous les modèles sont disponibles."""
        required_models = ["intent_classifier", "vulnerability_classifier", "network_analyzer"]
        return all(self.is_model_available(model) for model in required_models)

# Instance globale
models_config = ModelsConfig()

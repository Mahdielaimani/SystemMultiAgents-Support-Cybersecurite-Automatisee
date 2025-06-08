"""
Configuration pour vos modèles Hugging Face
"""

import os

class HuggingFaceConfig:
    # Vos informations HF
    HF_USERNAME = "elmahdielaimani"
    HF_TOKEN = os.getenv("HUGGINGFACE_TOKEN")

    # Vos modèles
    MODELS = {
        "vulnerability_classifier": {
            "model_name": "elmahdielaimani/vulnerability-classifier",
            "description": "Classifie les vulnérabilités de sécurité dans le code",
            "downloads_last_month": "Unknown",
            "license": "apache-2.0"
        },
        "network_analyzer": {
            "model_name": "elmahdielaimani/network-analyzer-cicids",
            "description": "Analyse le trafic réseau pour détecter les attaques (CIC-IDS)",
            "downloads_last_month": "Unknown",
            "license": "apache-2.0"
        },
        "intent_classifier": {
            "model_name": "elmahdielaimani/intent-classifier-security",
            "description": "Classifie l'intention de sécurité des utilisateurs",
            "downloads_last_month": "3",
            "license": "apache-2.0"
        }
    }

    # Configuration générale
    DEVICE = "cuda" if os.system("nvidia-smi > /dev/null 2>&1") == 0 else "cpu"
    MAX_LENGTH = 512
    BATCH_SIZE = 8

    @classmethod
    def get_model_config(cls, model_key: str) -> dict:
        """Récupère la configuration d'un modèle spécifique"""
        return cls.MODELS.get(model_key, {})

    @classmethod
    def get_all_model_names(cls) -> list:
        """Retourne la liste des noms de tous les modèles"""
        return [config["model_name"] for config in cls.MODELS.values()]

"""
Configuration settings for NextGen-Agent
"""
import os
from pathlib import Path
from typing import Dict, Any, Optional

# Base directory
BASE_DIR = Path(__file__).parent.parent

# Environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
HUGGINGFACE_USERNAME = os.getenv("HUGGINGFACE_USERNAME", "elmahdielalimani")
HUGGINGFACE_TOKEN = os.getenv("HUGGINGFACE_TOKEN", "")

# API Configuration
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8000"))
UI_PORT = int(os.getenv("UI_PORT", "3000"))

# Database Configuration
CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "./data/vector_db")
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")

# Model Configuration
MODEL_CACHE_DIR = os.getenv("MODEL_CACHE_DIR", "./models")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "BAAI/bge-large-en-v1.5")

# Security
SECRET_KEY = os.getenv("SECRET_KEY", "your_secret_key_here")
JWT_SECRET = os.getenv("JWT_SECRET", "your_jwt_secret_here")

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_DIR = os.getenv("LOG_DIR", "./logs")

# Development
DEBUG = os.getenv("DEBUG", "true").lower() == "true"
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

# Model URLs
MODELS_CONFIG = {
    "network_analyzer": {
        "username": HUGGINGFACE_USERNAME,
        "repo": "network-analyzer-cicids",
        "files": ["model.pkl", "label_encoder.pkl", "scaler.pkl", "feature_names.pkl", "metadata.json"]
    },
    "intent_classifier": {
        "username": HUGGINGFACE_USERNAME,
        "repo": "intent-classifier-security",
        "files": ["pytorch_model.bin", "config.json", "tokenizer.json", "vocab.txt", "intent_labels.json", "metadata.json"]
    },
    "vulnerability_classifier": {
        "username": HUGGINGFACE_USERNAME,
        "repo": "vulnerability-classifier",
        "files": ["best_model.pth", "tokenizer.json", "label_dict.json", "results_summary.json"]
    }
}

class Settings:
    """Classe de configuration centralisée"""
    
    def __init__(self):
        self.openai_api_key = OPENAI_API_KEY
        self.huggingface_username = HUGGINGFACE_USERNAME
        self.huggingface_token = HUGGINGFACE_TOKEN
        self.api_host = API_HOST
        self.api_port = API_PORT
        self.ui_port = UI_PORT
        self.chroma_persist_dir = CHROMA_PERSIST_DIR
        self.model_cache_dir = MODEL_CACHE_DIR
        self.models_config = MODELS_CONFIG
        self.debug = DEBUG
        self.environment = ENVIRONMENT
        self.secret_key = SECRET_KEY
        self.jwt_secret = JWT_SECRET
        self.log_level = LOG_LEVEL
        self.log_dir = LOG_DIR
        self.base_dir = BASE_DIR
        self.neo4j_uri = NEO4J_URI
        self.neo4j_user = NEO4J_USER
        self.neo4j_password = NEO4J_PASSWORD
        self.embedding_model = EMBEDDING_MODEL
    
    def get_model_config(self, model_name: str) -> Optional[Dict[str, Any]]:
        """Récupère la configuration d'un modèle"""
        return self.models_config.get(model_name)
    
    def is_production(self) -> bool:
        """Vérifie si on est en production"""
        return self.environment == "production"
    
    def validate_config(self) -> Dict[str, bool]:
        """Valide la configuration"""
        return {
            "openai_api_key": bool(self.openai_api_key and self.openai_api_key != ""),
            "huggingface_token": bool(self.huggingface_token and self.huggingface_token != ""),
            "secret_key": bool(self.secret_key and self.secret_key != "your_secret_key_here"),
            "jwt_secret": bool(self.jwt_secret and self.jwt_secret != "your_jwt_secret_here"),
        }

def load_settings() -> Dict[str, Any]:
    """
    Charge les paramètres de configuration.
    Fonction de compatibilité pour main.py
    """
    return {
        "api_port": API_PORT,
        "ui_port": UI_PORT,
        "api_host": API_HOST,
        "debug": DEBUG,
        "environment": ENVIRONMENT,
        "log_level": LOG_LEVEL,
        "openai_api_key": OPENAI_API_KEY,
        "huggingface_token": HUGGINGFACE_TOKEN,
        "huggingface_username": HUGGINGFACE_USERNAME,
        "model_cache_dir": MODEL_CACHE_DIR,
        "chroma_persist_dir": CHROMA_PERSIST_DIR,
        "secret_key": SECRET_KEY,
        "jwt_secret": JWT_SECRET,
        "base_dir": str(BASE_DIR),
        "models_config": MODELS_CONFIG
    }

def get_settings() -> Settings:
    """Retourne l'instance des paramètres"""
    return settings

# Instance globale
settings = Settings()

# Export des variables principales pour compatibilité
__all__ = [
    'settings',
    'load_settings', 
    'get_settings',
    'Settings',
    'OPENAI_API_KEY',
    'HUGGINGFACE_TOKEN',
    'HUGGINGFACE_USERNAME',
    'API_HOST',
    'API_PORT',
    'UI_PORT',
    'DEBUG',
    'ENVIRONMENT',
    'MODELS_CONFIG'
]

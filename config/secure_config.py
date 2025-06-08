# Fichier: config/secure_config.py

import os
from dotenv import load_dotenv

# Charger les variables d'environnement depuis .env
load_dotenv()

class SecureConfig:
    """Configuration sécurisée pour HuggingFace"""
    
    # Ne JAMAIS mettre de tokens en dur dans le code !
    HUGGINGFACE_TOKEN = os.getenv("HUGGINGFACE_TOKEN")
    HUGGINGFACE_USERNAME = os.getenv("HUGGINGFACE_USERNAME", "elmahdielmani")
    
    @classmethod
    def get_token(cls):
        """Récupère le token de manière sécurisée"""
        token = cls.HUGGINGFACE_TOKEN
        if not token:
            # Essayer de récupérer depuis le cache HF
            try:
                from huggingface_hub import HfFolder
                token = HfFolder.get_token()
            except:
                pass
                
        if not token:
            raise ValueError(
                "Token HuggingFace non trouvé ! "
                "Utilisez 'huggingface-cli login' ou définissez HUGGINGFACE_TOKEN dans .env"
            )
        return token
    
    @classmethod
    def validate_config(cls):
        """Vérifie que la configuration est valide"""
        try:
            token = cls.get_token()
            print("✅ Configuration HuggingFace valide")
            return True
        except Exception as e:
            print(f"❌ Erreur de configuration: {e}")
            return False
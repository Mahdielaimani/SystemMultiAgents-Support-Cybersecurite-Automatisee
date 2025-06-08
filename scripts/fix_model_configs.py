"""
Script pour corriger la configuration des modèles sur HuggingFace
"""
from huggingface_hub import HfApi, upload_file, hf_hub_download
import json
import tempfile
import os

def fix_model_config(repo_id):
    """Corrige la configuration d'un modèle"""
    api = HfApi()
    
    print(f"\n🔧 Correction de {repo_id}")
    
    try:
        # Télécharger config actuelle
        config_path = hf_hub_download(repo_id=repo_id, filename="config.json")
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        # Ajouter model_type
        config["model_type"] = "bert"
        config["architectures"] = ["BertForSequenceClassification"]
        
        # Sauvegarder et uploader
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config, f, indent=2)
            temp_path = f.name
        
        api.upload_file(
            path_or_fileobj=temp_path,
            path_in_repo="config.json",
            repo_id=repo_id,
            commit_message="Fix model_type in config"
        )
        
        os.unlink(temp_path)
        print(f"✅ Configuration corrigée pour {repo_id}")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")

# Corriger les deux modèles problématiques
fix_model_config("elmahdielaimani/vulnerability-classifier")
fix_model_config("elmahdielaimani/network-analyzer-cicids")

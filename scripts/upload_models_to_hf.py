"""
Script pour uploader tes modèles entraînés sur HuggingFace
"""

from transformers import AutoModel, AutoTokenizer, AutoModelForSequenceClassification
from huggingface_hub import login
import os

# 1. Se connecter à HuggingFace
login(token="TON_TOKEN_ICI")  # Remplace par ton token

# 2. Fonction pour uploader un modèle
def upload_model_to_hub(
    model_path: str,
    repo_name: str,
    model_type: str = "text-classification"
):
    """
    Upload un modèle local vers HuggingFace Hub
    
    Args:
        model_path: Chemin local vers le modèle
        repo_name: Nom du repo sur HF (ex: "elmahdielmani/vulnerability-classifier")
        model_type: Type de tâche du modèle
    """
    
    print(f"📤 Upload du modèle {repo_name}...")
    
    try:
        # Charger le modèle et tokenizer locaux
        if model_type == "text-classification":
            model = AutoModelForSequenceClassification.from_pretrained(model_path)
        else:
            model = AutoModel.from_pretrained(model_path)
            
        tokenizer = AutoTokenizer.from_pretrained(model_path)
        
        # Uploader vers HuggingFace
        model.push_to_hub(repo_name, private=True)  # private=True pour un repo privé
        tokenizer.push_to_hub(repo_name, private=True)
        
        print(f"✅ Modèle {repo_name} uploadé avec succès!")
        
    except Exception as e:
        print(f"❌ Erreur lors de l'upload: {e}")

# 3. Uploader tes 3 modèles
if __name__ == "__main__":
    # Remplace ces chemins par les vrais chemins de tes modèles
    models_to_upload = [
        {
            "local_path": "./models/vulnerability_classifier_trained/",
            "repo_name": "elmahdielmani/vulnerability-classifier",
            "model_type": "text-classification"
        },
        {
            "local_path": "./models/network_analyzer_trained/",
            "repo_name": "elmahdielmani/network-analyzer-cicids",
            "model_type": "text-classification"
        },
        {
            "local_path": "./models/intent_classifier_trained/",
            "repo_name": "elmahdielmani/intent-classifier-security",
            "model_type": "text-classification"
        }
    ]
    
    for model_info in models_to_upload:
        upload_model_to_hub(
            model_path=model_info["local_path"],
            repo_name=model_info["repo_name"],
            model_type=model_info["model_type"]
        )
    
    print("\n🎉 Tous les modèles ont été traités!")
    print("📝 N'oublie pas de:")
    print("   - Vérifier sur https://huggingface.co/elmahdielmani")
    print("   - Rendre les repos publics si tu veux partager")
    print("   - Ajouter un README.md et une model card")
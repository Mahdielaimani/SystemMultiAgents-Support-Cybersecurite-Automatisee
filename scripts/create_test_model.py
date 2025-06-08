"""
Script pour créer et uploader un modèle de test sur HuggingFace
"""
from transformers import AutoModelForSequenceClassification, AutoTokenizer
from huggingface_hub import HfApi, create_repo
import os

print("🧪 Création d'un modèle de test pour HuggingFace...")

try:
    # Vérifier la connexion
    api = HfApi()
    user_info = api.whoami()
    print(f"✅ Connecté en tant que: {user_info['name']}")
    
    # Utiliser un petit modèle comme base
    base_model = "distilbert-base-uncased"
    print(f"📥 Chargement du modèle de base: {base_model}")
    
    # Créer un modèle pour classification de sécurité (4 classes)
    model = AutoModelForSequenceClassification.from_pretrained(
        base_model, 
        num_labels=4,
        problem_type="single_label_classification"
    )
    tokenizer = AutoTokenizer.from_pretrained(base_model)
    
    # Définir les labels
    labels = ["SAFE", "XSS", "SQL_INJECTION", "PATH_TRAVERSAL"]
    model.config.id2label = {i: label for i, label in enumerate(labels)}
    model.config.label2id = {label: i for i, label in enumerate(labels)}
    
    # Nom du repo de test
    repo_name = "elmahdielaimani/test-vulnerability-classifier"
    
    try:
        # Créer le repo s'il n'existe pas
        create_repo(repo_name, private=True, repo_type="model")
        print(f"✅ Repo créé: {repo_name}")
    except Exception as e:
        print(f"ℹ️ Le repo existe peut-être déjà: {e}")
    
    # Uploader le modèle
    print(f"📤 Upload du modèle vers {repo_name}...")
    model.push_to_hub(repo_name, private=True)
    tokenizer.push_to_hub(repo_name, private=True)
    
    # Créer un README
    readme_content = """---
tags:
- text-classification
- security
- vulnerability-detection
library_name: transformers
---

# Test Vulnerability Classifier

This is a test model for vulnerability classification.

## Labels
- SAFE
- XSS
- SQL_INJECTION
- PATH_TRAVERSAL
"""
    
    # Créer une model card
    card_path = "README.md"
    with open(card_path, "w") as f:
        f.write(readme_content)
    
    api.upload_file(
        path_or_fileobj=card_path,
        path_in_repo="README.md",
        repo_id=repo_name,
        repo_type="model"
    )
    
    print(f"✅ Modèle uploadé avec succès!")
    print(f"🔗 Voir le modèle: https://huggingface.co/{repo_name}")
    
    # Nettoyer
    os.remove(card_path)
    
except Exception as e:
    print(f"❌ Erreur: {e}")
    import traceback
    traceback.print_exc()

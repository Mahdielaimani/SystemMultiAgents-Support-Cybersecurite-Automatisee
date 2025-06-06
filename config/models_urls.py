"""
Configuration complète des URLs des modèles Hugging Face
Tous les modèles fine-tunés par elmahdielalimani
"""

# Username Hugging Face
HUGGING_FACE_USERNAME = "elmahdielalimani"

# Configuration complète des 3 modèles
MODELS_URLS = {
    # 1. Network Analyzer (CICIDS2017) - ✅ UPLOADÉ
    "network_analyzer": {
        "base_url": f"https://huggingface.co/{HUGGING_FACE_USERNAME}/network-analyzer-cicids/resolve/main/",
        "files": {
            "model": "xgboost_cicids2017_production.pkl",
            "scaler": "scaler.pkl", 
            "feature_selector": "feature_selector.pkl",
            "label_encoder": "label_encoder.pkl",
            "metadata": "model_metadata.json"
        },
        "model_type": "sklearn",
        "task": "network_traffic_analysis"
    },
    
    # 2. Intent Classifier - ✅ UPLOADÉ
    "intent_classifier": {
        "base_url": f"https://huggingface.co/{HUGGING_FACE_USERNAME}/intent-classifier-security/resolve/main/",
        "files": {
            "model": "pytorch_model.bin",
            "config": "config.json",
            "tokenizer": "tokenizer.json",
            "vocab": "vocab.txt",
            "labels": "intent_labels.json",
            "metadata": "metadata.json"
        },
        "model_type": "transformers",
        "task": "intent_classification"
    },
    
    # 3. Vulnerability Classifier - ✅ UPLOADÉ  
    "vulnerability_classifier": {
        "base_url": f"https://huggingface.co/{HUGGING_FACE_USERNAME}/vulnerability-classifier/resolve/main/",
        "files": {
            "model": "best_model.pth",
            "tokenizer": "tokenizer.json", 
            "labels": "label_dict.json",
            "results": "results_summary.json"
        },
        "model_type": "pytorch",
        "task": "vulnerability_detection"
    }
}

# Fonctions utilitaires
def get_model_url(model_name: str, file_key: str) -> str:
    """Génère l'URL complète pour un fichier de modèle"""
    if model_name not in MODELS_URLS:
        raise ValueError(f"Modèle {model_name} non trouvé")
    
    model_config = MODELS_URLS[model_name]
    if file_key not in model_config["files"]:
        raise ValueError(f"Fichier {file_key} non trouvé pour {model_name}")
    
    return model_config["base_url"] + model_config["files"][file_key]

def get_all_model_urls() -> dict:
    """Retourne toutes les URLs des modèles"""
    all_urls = {}
    for model_name, config in MODELS_URLS.items():
        all_urls[model_name] = {}
        for file_key, filename in config["files"].items():
            all_urls[model_name][file_key] = get_model_url(model_name, file_key)
    return all_urls

def validate_models_config() -> bool:
    """Valide la configuration des modèles"""
    try:
        for model_name in MODELS_URLS.keys():
            for file_key in MODELS_URLS[model_name]["files"].keys():
                url = get_model_url(model_name, file_key)
                print(f"✅ {model_name}.{file_key}: {url}")
        return True
    except Exception as e:
        print(f"❌ Erreur validation: {e}")
        return False

# URLs directes pour usage rapide
NETWORK_ANALYZER_URLS = {
    "model": get_model_url("network_analyzer", "model"),
    "scaler": get_model_url("network_analyzer", "scaler"),
    "feature_selector": get_model_url("network_analyzer", "feature_selector"),
    "label_encoder": get_model_url("network_analyzer", "label_encoder"),
    "metadata": get_model_url("network_analyzer", "metadata")
}

INTENT_CLASSIFIER_URLS = {
    "model": get_model_url("intent_classifier", "model"),
    "config": get_model_url("intent_classifier", "config"),
    "tokenizer": get_model_url("intent_classifier", "tokenizer"),
    "vocab": get_model_url("intent_classifier", "vocab"),
    "labels": get_model_url("intent_classifier", "labels"),
    "metadata": get_model_url("intent_classifier", "metadata")
}

VULNERABILITY_CLASSIFIER_URLS = {
    "model": get_model_url("vulnerability_classifier", "model"),
    "tokenizer": get_model_url("vulnerability_classifier", "tokenizer"),
    "labels": get_model_url("vulnerability_classifier", "labels"),
    "results": get_model_url("vulnerability_classifier", "results")
}

print("✅ Configuration complète des 3 modèles chargée")
print(f"🔗 Network Analyzer: {len(NETWORK_ANALYZER_URLS)} fichiers")
print(f"🔗 Intent Classifier: {len(INTENT_CLASSIFIER_URLS)} fichiers")
print(f"🔗 Vulnerability Classifier: {len(VULNERABILITY_CLASSIFIER_URLS)} fichiers")

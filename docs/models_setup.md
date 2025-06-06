# Configuration des Modèles ML

## 📋 Modèles Requis

Le système NextGen-Agent nécessite 3 modèles ML entraînés :

### 1. Classificateur d'Intentions
- **Fichier**: `models/intent_classifier/intent_classifier.pkl`
- **Usage**: Routage des requêtes vers les agents appropriés
- **Classes**: `support_question`, `security_question`, `pentest_request`, `network_analysis`

### 2. Classificateur de Vulnérabilités  
- **Fichier**: `models/vulnerability_classifier/vulnerability_classifier.pkl`
- **Usage**: Classification des types de vulnérabilités
- **Classes**: `sql_injection`, `xss`, `csrf`, `rce`, etc.

### 3. Analyseur Réseau (CICIDS2017)
- **Fichier**: `models/network_analyzer/network_analyzer.pkl`
- **Usage**: Détection d'anomalies dans le trafic réseau
- **Classes**: `BENIGN`, `DDoS`, `PortScan`, `Bot`, etc.

## 🚀 Instructions de Déploiement

### Étape 1: Entraîner les Modèles sur Kaggle

1. **Créer les notebooks Kaggle** :
   - `vulnerability_classifier_training.py`
   - `network_analyzer_training.py` 
   - `intent_classifier_training.py`

2. **Exécuter les notebooks** sur Kaggle avec GPU activé

3. **Publier les modèles** comme datasets Kaggle privés

### Étape 2: Télécharger les Modèles

\`\`\`bash
# Configurer les credentials Kaggle
mkdir -p ~/.kaggle
# Placer votre kaggle.json dans ~/.kaggle/

# Télécharger les modèles
python scripts/download_models_from_kaggle.py
\`\`\`

### Étape 3: Vérifier l'Installation

\`\`\`bash
# Vérifier que les modèles sont présents
ls -la models/
├── intent_classifier/
│   ├── intent_classifier.pkl
│   └── intent_dict.json
├── vulnerability_classifier/
│   ├── vulnerability_classifier.pkl
│   └── label_dict.json
└── network_analyzer/
    ├── network_analyzer.pkl
    └── attack_types.json
\`\`\`

## ⚙️ Configuration

Mettre à jour `config/settings.py` avec les chemins des modèles :

\`\`\`python
MODELS = {
    "intent_classifier_path": "models/intent_classifier/intent_classifier.pkl",
    "vulnerability_classifier_path": "models/vulnerability_classifier/vulnerability_classifier.pkl", 
    "network_analyzer_path": "models/network_analyzer/network_analyzer.pkl"
}
\`\`\`

## 🧪 Test des Modèles

\`\`\`python
from utils.model_loader import ModelLoader

# Tester le chargement des modèles
loader = ModelLoader()

# Test classificateur d'intentions
intent, confidence = loader.predict_intent("Scannez mon site web")
print(f"Intent: {intent}, Confidence: {confidence}")

# Test classificateur de vulnérabilités  
vuln, confidence = loader.predict_vulnerability("SQL injection detected")
print(f"Vulnerability: {vuln}, Confidence: {confidence}")

"""
Validateur pour vérifier l'intégrité des modèles.
"""
import os
import logging
from pathlib import Path
from typing import Dict, List, Tuple
import joblib
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

logger = logging.getLogger(__name__)

class ModelValidator:
    """Classe pour valider l'intégrité des modèles."""
    
    def __init__(self, models_dir: str):
        self.models_dir = Path(models_dir)
    
    def validate_intent_classifier(self) -> Tuple[bool, str]:
        """Valide le classificateur d'intentions."""
        model_path = self.models_dir / "intent_classifier"
        
        if not model_path.exists():
            return False, f"Répertoire {model_path} non trouvé"
        
        try:
            # Vérifier les fichiers requis
            required_files = ["config.json", "pytorch_model.bin", "tokenizer.json"]
            missing_files = []
            
            for file_name in required_files:
                if not (model_path / file_name).exists():
                    missing_files.append(file_name)
            
            if missing_files:
                return False, f"Fichiers manquants: {missing_files}"
            
            # Tester le chargement
            tokenizer = AutoTokenizer.from_pretrained(str(model_path))
            model = AutoModelForSequenceClassification.from_pretrained(str(model_path))
            
            # Test rapide
            test_text = "Bonjour, j'ai besoin d'aide"
            inputs = tokenizer(test_text, return_tensors="pt")
            with torch.no_grad():
                outputs = model(**inputs)
            
            return True, "Classificateur d'intentions validé avec succès"
            
        except Exception as e:
            return False, f"Erreur lors de la validation: {str(e)}"
    
    def validate_vulnerability_classifier(self) -> Tuple[bool, str]:
        """Valide le classificateur de vulnérabilités."""
        model_path = self.models_dir / "vulnerability_classifier"
        
        if not model_path.exists():
            return False, f"Répertoire {model_path} non trouvé"
        
        try:
            # Vérifier les fichiers requis
            required_files = ["config.json", "pytorch_model.bin", "tokenizer.json"]
            missing_files = []
            
            for file_name in required_files:
                if not (model_path / file_name).exists():
                    missing_files.append(file_name)
            
            if missing_files:
                return False, f"Fichiers manquants: {missing_files}"
            
            # Tester le chargement
            tokenizer = AutoTokenizer.from_pretrained(str(model_path))
            model = AutoModelForSequenceClassification.from_pretrained(str(model_path))
            
            # Test rapide
            test_text = "SQL injection vulnerability detected"
            inputs = tokenizer(test_text, return_tensors="pt")
            with torch.no_grad():
                outputs = model(**inputs)
            
            return True, "Classificateur de vulnérabilités validé avec succès"
            
        except Exception as e:
            return False, f"Erreur lors de la validation: {str(e)}"
    
    def validate_network_analyzer(self) -> Tuple[bool, str]:
        """Valide l'analyseur réseau."""
        model_path = self.models_dir / "network_analyzer"
        
        if not model_path.exists():
            return False, f"Répertoire {model_path} non trouvé"
        
        try:
            # Chercher le fichier du modèle
            model_files = list(model_path.glob("*.pkl")) + list(model_path.glob("*.joblib"))
            
            if not model_files:
                return False, "Aucun fichier de modèle trouvé (.pkl ou .joblib)"
            
            # Tester le chargement
            model_file = model_files[0]
            model_data = joblib.load(model_file)
            
            # Vérifier la structure
            if isinstance(model_data, dict):
                required_keys = ["model", "feature_names"]
                missing_keys = [key for key in required_keys if key not in model_data]
                if missing_keys:
                    return False, f"Clés manquantes dans le modèle: {missing_keys}"
            
            return True, "Analyseur réseau validé avec succès"
            
        except Exception as e:
            return False, f"Erreur lors de la validation: {str(e)}"
    
    def validate_all_models(self) -> Dict[str, Tuple[bool, str]]:
        """Valide tous les modèles."""
        results = {}
        
        # Valider chaque modèle
        results["intent_classifier"] = self.validate_intent_classifier()
        results["vulnerability_classifier"] = self.validate_vulnerability_classifier()
        results["network_analyzer"] = self.validate_network_analyzer()
        
        return results
    
    def print_validation_report(self):
        """Affiche un rapport de validation."""
        print("\n🔍 Rapport de validation des modèles")
        print("=" * 50)
        
        results = self.validate_all_models()
        
        for model_name, (is_valid, message) in results.items():
            status = "✅" if is_valid else "❌"
            print(f"{status} {model_name}: {message}")
        
        # Résumé
        valid_count = sum(1 for is_valid, _ in results.values() if is_valid)
        total_count = len(results)
        
        print(f"\n📊 Résumé: {valid_count}/{total_count} modèles valides")
        
        if valid_count == total_count:
            print("🎉 Tous les modèles sont valides!")
        else:
            print("⚠️ Certains modèles nécessitent une attention.")
        
        return valid_count == total_count

if __name__ == "__main__":
    import sys
    
    models_dir = sys.argv[1] if len(sys.argv) > 1 else "models"
    validator = ModelValidator(models_dir)
    validator.print_validation_report()

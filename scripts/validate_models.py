#!/usr/bin/env python3
"""
Script de validation des modèles et du système.
"""
import os
import sys
import json
import time
import traceback
from pathlib import Path
from typing import Dict, Any, List, Tuple

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_colored(message: str, color: str = Colors.WHITE):
    """Affiche un message coloré."""
    print(f"{color}{message}{Colors.END}")

class SystemValidator:
    """Validateur du système NextGen-Agent."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.config_file = self.project_root / "config" / "models_config.json"
        self.results: List[Tuple[str, bool, str]] = []
    
    def load_config(self) -> Dict[str, Any]:
        """Charge la configuration des modèles."""
        try:
            with open(self.config_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print_colored("❌ Configuration des modèles non trouvée", Colors.RED)
            return {}
        except json.JSONDecodeError as e:
            print_colored(f"❌ Erreur dans la configuration: {e}", Colors.RED)
            return {}
    
    def test_python_imports(self) -> bool:
        """Teste les imports Python critiques."""
        print_colored("🐍 Test des imports Python...", Colors.BLUE)
        
        critical_modules = [
            ("fastapi", "Framework web"),
            ("uvicorn", "Serveur ASGI"),
            ("langchain", "Framework LangChain"),
            ("openai", "Client OpenAI"),
            ("transformers", "Transformers Hugging Face"),
            ("sentence_transformers", "Sentence Transformers"),
            ("chromadb", "Base de données vectorielle"),
            ("sklearn", "Scikit-learn"),
            ("pandas", "Manipulation de données"),
            ("numpy", "Calcul numérique")
        ]
        
        failed_imports = []
        
        for module, description in critical_modules:
            try:
                __import__(module)
                print_colored(f"  ✅ {module} ({description})", Colors.GREEN)
            except ImportError as e:
                print_colored(f"  ❌ {module} ({description}): {e}", Colors.RED)
                failed_imports.append(module)
        
        success = len(failed_imports) == 0
        self.results.append(("Imports Python", success, f"{len(failed_imports)} échecs" if failed_imports else "Tous OK"))
        
        return success
    
    def test_models(self) -> bool:
        """Teste le chargement des modèles."""
        print_colored("🤖 Test des modèles IA...", Colors.BLUE)
        
        config = self.load_config()
        models = config.get("models", {})
        
        if not models:
            print_colored("  ⚠️ Aucun modèle configuré", Colors.YELLOW)
            self.results.append(("Modèles IA", False, "Aucun modèle"))
            return False
        
        failed_models = []
        
        for model_name, model_info in models.items():
            try:
                model_path = Path(model_info["path"])
                model_type = model_info["type"]
                
                if not model_path.exists():
                    print_colored(f"  ❌ {model_name}: fichier manquant", Colors.RED)
                    failed_models.append(model_name)
                    continue
                
                # Test de chargement selon le type
                if model_type == "sklearn":
                    import joblib
                    model = joblib.load(model_path)
                    print_colored(f"  ✅ {model_name} (sklearn)", Colors.GREEN)
                    
                elif model_type == "sentence_transformer":
                    from sentence_transformers import SentenceTransformer
                    model = SentenceTransformer(str(model_path))
                    
                    # Test d'encodage
                    test_text = "Test d'encodage"
                    embedding = model.encode(test_text)
                    print_colored(f"  ✅ {model_name} (sentence-transformer, dim={len(embedding)})", Colors.GREEN)
                    
                else:
                    print_colored(f"  ⚠️ {model_name}: type non reconnu ({model_type})", Colors.YELLOW)
                
            except Exception as e:
                print_colored(f"  ❌ {model_name}: {str(e)}", Colors.RED)
                failed_models.append(model_name)
        
        success = len(failed_models) == 0
        self.results.append(("Modèles IA", success, f"{len(failed_models)} échecs" if failed_models else "Tous OK"))
        
        return success
    
    def test_environment_variables(self) -> bool:
        """Teste les variables d'environnement."""
        print_colored("🔧 Test des variables d'environnement...", Colors.BLUE)
        
        required_vars = [
            ("OPENAI_API_KEY", "Clé API OpenAI", True),
            ("API_PORT", "Port API", False),
            ("UI_PORT", "Port UI", False),
            ("ENVIRONMENT", "Environnement", False)
        ]
        
        missing_critical = []
        missing_optional = []
        
        for var_name, description, is_critical in required_vars:
            value = os.getenv(var_name)
            
            if not value or value.startswith("your_"):
                if is_critical:
                    print_colored(f"  ❌ {var_name} ({description}): manquant", Colors.RED)
                    missing_critical.append(var_name)
                else:
                    print_colored(f"  ⚠️ {var_name} ({description}): manquant", Colors.YELLOW)
                    missing_optional.append(var_name)
            else:
                print_colored(f"  ✅ {var_name} ({description})", Colors.GREEN)
        
        success = len(missing_critical) == 0
        status = f"{len(missing_critical)} critiques manquantes" if missing_critical else "OK"
        self.results.append(("Variables d'environnement", success, status))
        
        return success
    
    def test_directories(self) -> bool:
        """Teste la structure des répertoires."""
        print_colored("📁 Test de la structure des répertoires...", Colors.BLUE)
        
        required_dirs = [
            "config",
            "models", 
            "data",
            "data/chroma_db",
            "logs",
            "scripts"
        ]
        
        missing_dirs = []
        
        for dir_name in required_dirs:
            dir_path = self.project_root / dir_name
            if dir_path.exists():
                print_colored(f"  ✅ {dir_name}/", Colors.GREEN)
            else:
                print_colored(f"  ❌ {dir_name}/: manquant", Colors.RED)
                missing_dirs.append(dir_name)
        
        success = len(missing_dirs) == 0
        self.results.append(("Structure répertoires", success, f"{len(missing_dirs)} manquants" if missing_dirs else "OK"))
        
        return success
    
    def test_core_components(self) -> bool:
        """Teste les composants principaux."""
        print_colored("⚙️ Test des composants principaux...", Colors.BLUE)
        
        try:
            # Test du routeur
            sys.path.insert(0, str(self.project_root))
            
            from core.router import Router
            router = Router()
            print_colored("  ✅ Routeur principal", Colors.GREEN)
            
            # Test du gestionnaire de mémoire
            from core.memory import MemoryManager
            memory = MemoryManager()
            print_colored("  ✅ Gestionnaire de mémoire", Colors.GREEN)
            
            # Test de l'agent de support
            from agents.support_agent.agent import SupportAgent
            support_agent = SupportAgent()
            print_colored("  ✅ Agent de support", Colors.GREEN)
            
            self.results.append(("Composants principaux", True, "Tous OK"))
            return True
            
        except Exception as e:
            print_colored(f"  ❌ Erreur: {str(e)}", Colors.RED)
            self.results.append(("Composants principaux", False, str(e)))
            return False
    
    def test_api_endpoints(self) -> bool:
        """Teste les endpoints API (simulation)."""
        print_colored("🔌 Test des endpoints API...", Colors.BLUE)
        
        try:
            # Import du serveur API
            from api.server import app
            print_colored("  ✅ Serveur API importé", Colors.GREEN)
            
            # Test de création d'une instance FastAPI
            from fastapi.testclient import TestClient
            client = TestClient(app)
            print_colored("  ✅ Client de test créé", Colors.GREEN)
            
            self.results.append(("Endpoints API", True, "OK"))
            return True
            
        except Exception as e:
            print_colored(f"  ❌ Erreur API: {str(e)}", Colors.RED)
            self.results.append(("Endpoints API", False, str(e)))
            return False
    
    def run_full_validation(self) -> bool:
        """Lance la validation complète."""
        print_colored("🔍 Validation complète du système NextGen-Agent", Colors.BOLD + Colors.CYAN)
        print_colored("=" * 60, Colors.CYAN)
        
        start_time = time.time()
        
        # Tests à exécuter
        tests = [
            ("Imports Python", self.test_python_imports),
            ("Variables d'environnement", self.test_environment_variables),
            ("Structure répertoires", self.test_directories),
            ("Modèles IA", self.test_models),
            ("Composants principaux", self.test_core_components),
            ("Endpoints API", self.test_api_endpoints)
        ]
        
        passed_tests = 0
        
        for test_name, test_func in tests:
            print_colored(f"\n🧪 {test_name}...", Colors.BLUE)
            try:
                if test_func():
                    passed_tests += 1
            except Exception as e:
                print_colored(f"❌ Erreur inattendue dans {test_name}: {e}", Colors.RED)
                traceback.print_exc()
        
        # Résumé
        elapsed_time = time.time() - start_time
        print_colored(f"\n📊 Résumé de la validation", Colors.BOLD + Colors.CYAN)
        print_colored("=" * 40, Colors.CYAN)
        
        for test_name, success, details in self.results:
            status = "✅ PASS" if success else "❌ FAIL"
            print_colored(f"{status} {test_name}: {details}", Colors.GREEN if success else Colors.RED)
        
        print_colored(f"\n⏱️ Temps d'exécution: {elapsed_time:.2f}s", Colors.BLUE)
        print_colored(f"📈 Tests réussis: {passed_tests}/{len(tests)}", Colors.BOLD)
        
        if passed_tests == len(tests):
            print_colored("\n🎉 Système validé avec succès!", Colors.BOLD + Colors.GREEN)
            print_colored("🚀 Prêt pour le démarrage: python scripts/start_system.py", Colors.CYAN)
            
            # Créer un fichier de statut
            with open(self.project_root / ".validation_complete", "w") as f:
                f.write(f"System validation completed successfully\nTests passed: {passed_tests}/{len(tests)}\n")
            
            return True
        else:
            print_colored(f"\n⚠️ Validation incomplète ({len(tests) - passed_tests} échecs)", Colors.YELLOW)
            print_colored("Le système peut fonctionner avec des fonctionnalités limitées", Colors.YELLOW)
            return False

def main():
    """Point d'entrée principal."""
    validator = SystemValidator()
    success = validator.run_full_validation()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()

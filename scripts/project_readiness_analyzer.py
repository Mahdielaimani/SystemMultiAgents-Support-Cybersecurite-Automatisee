#!/usr/bin/env python3
"""
Analyseur de préparation complète du projet NextGen-Agent
"""
import os
import sys
import ast
import json
import importlib.util
from pathlib import Path
from typing import Dict, List, Tuple, Any

class ProjectReadinessAnalyzer:
    """Analyseur complet de la préparation du projet"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.issues = []
        self.warnings = []
        self.missing_files = []
        self.import_errors = []
        
    def analyze_file_structure(self) -> Dict[str, Any]:
        """Analyse la structure des fichiers"""
        print("📁 Analyse de la structure des fichiers...")
        
        # Fichiers critiques requis
        critical_files = {
            "api/server.py": "Serveur API principal",
            "app/page.tsx": "Page principale frontend",
            "app/layout.tsx": "Layout principal",
            "package.json": "Configuration Node.js",
            "requirements.txt": "Dépendances Python",
            "config/models_urls.py": "Configuration des modèles",
            "utils/complete_model_loader.py": "Chargeur de modèles",
            "scripts/start_system.py": "Script de démarrage",
            ".env": "Variables d'environnement"
        }
        
        # Vérifier les fichiers critiques
        missing_critical = []
        for file_path, description in critical_files.items():
            full_path = self.project_root / file_path
            if not full_path.exists():
                missing_critical.append((file_path, description))
                print(f"❌ CRITIQUE: {file_path} - {description}")
            else:
                print(f"✅ {file_path}")
        
        if missing_critical:
            self.issues.extend(missing_critical)
        
        return {
            "critical_files_missing": len(missing_critical),
            "total_critical": len(critical_files)
        }
    
    def analyze_python_imports(self) -> Dict[str, Any]:
        """Analyse les imports Python"""
        print("\n🐍 Analyse des imports Python...")
        
        python_files = list(self.project_root.rglob("*.py"))
        import_issues = []
        
        for py_file in python_files:
            if "venv" in str(py_file) or "__pycache__" in str(py_file):
                continue
                
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Parser le fichier Python
                try:
                    tree = ast.parse(content)
                    
                    # Extraire les imports
                    for node in ast.walk(tree):
                        if isinstance(node, ast.Import):
                            for alias in node.names:
                                self._check_import(alias.name, py_file)
                        elif isinstance(node, ast.ImportFrom):
                            if node.module:
                                self._check_import(node.module, py_file)
                
                except SyntaxError as e:
                    import_issues.append(f"Erreur de syntaxe dans {py_file}: {e}")
                    
            except Exception as e:
                import_issues.append(f"Erreur lecture {py_file}: {e}")
        
        if import_issues:
            self.import_errors.extend(import_issues)
            for issue in import_issues:
                print(f"❌ {issue}")
        
        return {"import_errors": len(import_issues)}
    
    def _check_import(self, module_name: str, file_path: Path):
        """Vérifie si un module peut être importé"""
        # Ignorer les imports relatifs et standards
        if module_name.startswith('.') or module_name in ['os', 'sys', 'json', 'pathlib']:
            return
        
        try:
            importlib.import_module(module_name)
        except ImportError:
            # Vérifier si c'est un module local
            if not self._is_local_module(module_name):
                self.import_errors.append(f"Module manquant: {module_name} dans {file_path}")
    
    def _is_local_module(self, module_name: str) -> bool:
        """Vérifie si c'est un module local du projet"""
        local_modules = ['config', 'utils', 'agents', 'core', 'scripts']
        return any(module_name.startswith(local) for local in local_modules)
    
    def analyze_api_server(self) -> Dict[str, Any]:
        """Analyse le serveur API"""
        print("\n🔌 Analyse du serveur API...")
        
        api_file = self.project_root / "api" / "server.py"
        if not api_file.exists():
            self.issues.append(("api/server.py", "Serveur API manquant"))
            return {"status": "missing"}
        
        try:
            with open(api_file, 'r') as f:
                content = f.read()
            
            # Vérifier les éléments critiques
            required_elements = [
                "FastAPI",
                "app = FastAPI",
                "@app.get",
                "@app.post",
                "uvicorn"
            ]
            
            missing_elements = []
            for element in required_elements:
                if element not in content:
                    missing_elements.append(element)
            
            if missing_elements:
                self.issues.append(("API Server", f"Éléments manquants: {missing_elements}"))
                print(f"❌ Éléments manquants dans l'API: {missing_elements}")
            else:
                print("✅ Serveur API correctement configuré")
            
            return {
                "status": "ok" if not missing_elements else "incomplete",
                "missing_elements": missing_elements
            }
            
        except Exception as e:
            self.issues.append(("API Server", f"Erreur d'analyse: {e}"))
            return {"status": "error", "error": str(e)}
    
    def analyze_frontend(self) -> Dict[str, Any]:
        """Analyse le frontend Next.js"""
        print("\n⚛️ Analyse du frontend Next.js...")
        
        package_json = self.project_root / "package.json"
        if not package_json.exists():
            self.issues.append(("package.json", "Configuration Node.js manquante"))
            return {"status": "missing"}
        
        try:
            with open(package_json, 'r') as f:
                package_data = json.load(f)
            
            # Vérifier les dépendances critiques
            required_deps = ["next", "react", "react-dom"]
            dependencies = package_data.get("dependencies", {})
            
            missing_deps = [dep for dep in required_deps if dep not in dependencies]
            
            if missing_deps:
                self.issues.append(("Frontend", f"Dépendances manquantes: {missing_deps}"))
                print(f"❌ Dépendances manquantes: {missing_deps}")
            else:
                print("✅ Dépendances frontend OK")
            
            # Vérifier les scripts
            scripts = package_data.get("scripts", {})
            required_scripts = ["dev", "build", "start"]
            missing_scripts = [script for script in required_scripts if script not in scripts]
            
            if missing_scripts:
                self.warnings.append(f"Scripts manquants: {missing_scripts}")
                print(f"⚠️ Scripts manquants: {missing_scripts}")
            
            return {
                "status": "ok" if not missing_deps else "incomplete",
                "missing_dependencies": missing_deps,
                "missing_scripts": missing_scripts
            }
            
        except Exception as e:
            self.issues.append(("Frontend", f"Erreur d'analyse: {e}"))
            return {"status": "error", "error": str(e)}
    
    def analyze_models_configuration(self) -> Dict[str, Any]:
        """Analyse la configuration des modèles"""
        print("\n🤖 Analyse de la configuration des modèles...")
        
        models_config = self.project_root / "config" / "models_urls.py"
        if not models_config.exists():
            self.issues.append(("config/models_urls.py", "Configuration des modèles manquante"))
            return {"status": "missing"}
        
        try:
            # Importer et vérifier la configuration
            sys.path.insert(0, str(self.project_root))
            from config.models_urls import MODELS_URLS, HUGGING_FACE_USERNAME
            
            # Vérifier que tous les modèles sont configurés
            expected_models = ["network_analyzer", "intent_classifier", "vulnerability_classifier"]
            configured_models = list(MODELS_URLS.keys())
            
            missing_models = [model for model in expected_models if model not in configured_models]
            
            if missing_models:
                self.issues.append(("Models Config", f"Modèles manquants: {missing_models}"))
                print(f"❌ Modèles manquants: {missing_models}")
            else:
                print("✅ Tous les modèles configurés")
            
            # Vérifier le nom d'utilisateur
            if HUGGING_FACE_USERNAME != "elmahdielalimani":
                self.warnings.append(f"Username HF: {HUGGING_FACE_USERNAME} (attendu: elmahdielalimani)")
            
            return {
                "status": "ok" if not missing_models else "incomplete",
                "configured_models": len(configured_models),
                "missing_models": missing_models,
                "username": HUGGING_FACE_USERNAME
            }
            
        except Exception as e:
            self.issues.append(("Models Config", f"Erreur d'import: {e}"))
            return {"status": "error", "error": str(e)}
    
    def analyze_environment_variables(self) -> Dict[str, Any]:
        """Analyse les variables d'environnement"""
        print("\n🔧 Analyse des variables d'environnement...")
        
        env_file = self.project_root / ".env"
        if not env_file.exists():
            self.issues.append((".env", "Fichier .env manquant"))
            return {"status": "missing"}
        
        try:
            # Charger les variables d'environnement
            from dotenv import load_dotenv
            load_dotenv(env_file)
            
            # Variables critiques
            critical_vars = [
                "OPENAI_API_KEY",
                "HUGGINGFACE_USERNAME",
                "HUGGINGFACE_TOKEN"
            ]
            
            missing_vars = []
            for var in critical_vars:
                value = os.getenv(var)
                if not value or value.startswith("your_"):
                    missing_vars.append(var)
                    print(f"❌ {var}: Non configuré")
                else:
                    print(f"✅ {var}: Configuré")
            
            if missing_vars:
                self.issues.append(("Environment", f"Variables manquantes: {missing_vars}"))
            
            return {
                "status": "ok" if not missing_vars else "incomplete",
                "missing_variables": missing_vars
            }
            
        except Exception as e:
            self.issues.append(("Environment", f"Erreur d'analyse: {e}"))
            return {"status": "error", "error": str(e)}
    
    def check_dependencies(self) -> Dict[str, Any]:
        """Vérifie les dépendances Python"""
        print("\n📦 Vérification des dépendances Python...")
        
        requirements_file = self.project_root / "requirements.txt"
        if not requirements_file.exists():
            self.issues.append(("requirements.txt", "Fichier requirements.txt manquant"))
            return {"status": "missing"}
        
        try:
            with open(requirements_file, 'r') as f:
                requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]
            
            # Dépendances critiques
            critical_deps = [
                "fastapi", "uvicorn", "openai", "transformers", 
                "torch", "scikit-learn", "pandas", "numpy", 
                "requests", "python-dotenv"
            ]
            
            missing_deps = []
            for dep in critical_deps:
                try:
                    __import__(dep.replace("-", "_"))
                    print(f"✅ {dep}")
                except ImportError:
                    missing_deps.append(dep)
                    print(f"❌ {dep}: Non installé")
            
            if missing_deps:
                self.issues.append(("Dependencies", f"Packages manquants: {missing_deps}"))
            
            return {
                "status": "ok" if not missing_deps else "incomplete",
                "missing_packages": missing_deps,
                "total_requirements": len(requirements)
            }
            
        except Exception as e:
            self.issues.append(("Dependencies", f"Erreur d'analyse: {e}"))
            return {"status": "error", "error": str(e)}
    
    def generate_readiness_report(self) -> Dict[str, Any]:
        """Génère le rapport de préparation complet"""
        print("\n" + "="*60)
        print("📊 RAPPORT DE PRÉPARATION NEXTGEN-AGENT")
        print("="*60)
        
        # Exécuter toutes les analyses
        analyses = {
            "file_structure": self.analyze_file_structure(),
            "python_imports": self.analyze_python_imports(),
            "api_server": self.analyze_api_server(),
            "frontend": self.analyze_frontend(),
            "models_config": self.analyze_models_configuration(),
            "environment": self.analyze_environment_variables(),
            "dependencies": self.check_dependencies()
        }
        
        # Calculer le score de préparation
        total_checks = len(analyses)
        passed_checks = sum(1 for result in analyses.values() if result.get("status") == "ok")
        readiness_score = (passed_checks / total_checks) * 100
        
        # Résumé final
        print(f"\n🎯 SCORE DE PRÉPARATION: {readiness_score:.1f}%")
        print(f"✅ Vérifications réussies: {passed_checks}/{total_checks}")
        
        if self.issues:
            print(f"\n❌ PROBLÈMES CRITIQUES ({len(self.issues)}):")
            for issue, description in self.issues:
                print(f"  • {issue}: {description}")
        
        if self.warnings:
            print(f"\n⚠️ AVERTISSEMENTS ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"  • {warning}")
        
        # Déterminer si le projet est prêt
        is_ready = readiness_score >= 90 and len(self.issues) == 0
        
        print(f"\n{'🎉 PROJET PRÊT À DÉMARRER!' if is_ready else '🔧 CONFIGURATION REQUISE'}")
        
        if is_ready:
            print("\n🚀 Commandes pour démarrer:")
            print("  1. python scripts/setup_complete_models.py")
            print("  2. python scripts/start_system.py")
        else:
            print("\n📋 Actions requises:")
            print("  1. Corriger les problèmes critiques listés ci-dessus")
            print("  2. Installer les dépendances manquantes")
            print("  3. Configurer les variables d'environnement")
            print("  4. Relancer cette analyse")
        
        return {
            "readiness_score": readiness_score,
            "is_ready": is_ready,
            "passed_checks": passed_checks,
            "total_checks": total_checks,
            "critical_issues": len(self.issues),
            "warnings": len(self.warnings),
            "analyses": analyses
        }

def main():
    """Point d'entrée principal"""
    analyzer = ProjectReadinessAnalyzer()
    report = analyzer.generate_readiness_report()
    
    # Sauvegarder le rapport
    report_file = Path(__file__).parent.parent / "readiness_report.json"
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2, default=str)
    
    print(f"\n📄 Rapport sauvegardé: {report_file}")
    
    sys.exit(0 if report["is_ready"] else 1)

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Analyse complète et approfondie du projet NextGen-Agent
Vérification de tous les composants pour déterminer la préparation réelle
"""

import os
import sys
import ast
import json
import importlib
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional
import re

class ComprehensiveProjectAnalyzer:
    """Analyseur complet et méthodique du projet"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.critical_issues = []
        self.warnings = []
        self.missing_files = []
        self.broken_imports = []
        self.config_issues = []
        
        print("🔍 ANALYSE COMPLÈTE DU PROJET NEXTGEN-AGENT")
        print("=" * 60)
    
    def analyze_file_structure(self) -> Dict[str, Any]:
        """Analyse détaillée de la structure des fichiers"""
        print("\n📁 1. ANALYSE DE LA STRUCTURE DES FICHIERS")
        print("-" * 50)
        
        # Fichiers absolument critiques
        critical_files = {
            # Backend Python
            "api/server.py": "Serveur API FastAPI principal",
            "main.py": "Point d'entrée principal Python",
            "requirements.txt": "Dépendances Python",
            
            # Frontend Next.js
            "app/page.tsx": "Page principale Next.js",
            "app/layout.tsx": "Layout principal Next.js", 
            "package.json": "Configuration Node.js",
            
            # Configuration
            "config/models_urls.py": "URLs des modèles Hugging Face",
            "config/settings.py": "Configuration générale",
            ".env": "Variables d'environnement",
            
            # Agents
            "agents/support_agent/agent.py": "Agent de support",
            "agents/cybersecurity_agent/agent.py": "Agent cybersécurité",
            "agents/base_agent.py": "Classe de base des agents",
            
            # Core
            "core/router.py": "Routeur principal",
            "core/memory.py": "Gestionnaire de mémoire",
            "core/system.py": "Système central",
            
            # Utils
            "utils/complete_model_loader.py": "Chargeur de modèles",
            "utils/logger.py": "Système de logging",
            
            # Scripts
            "scripts/start_system.py": "Script de démarrage",
            "scripts/test_all_models.py": "Tests des modèles"
        }
        
        missing_critical = []
        existing_files = []
        
        for file_path, description in critical_files.items():
            full_path = self.project_root / file_path
            if not full_path.exists():
                missing_critical.append((file_path, description))
                print(f"❌ MANQUANT: {file_path} - {description}")
            else:
                existing_files.append(file_path)
                print(f"✅ {file_path}")
        
        # Fichiers optionnels mais recommandés
        optional_files = {
            "docker-compose.yml": "Configuration Docker",
            "Dockerfile": "Image Docker",
            "README.md": "Documentation",
            ".gitignore": "Fichiers à ignorer Git"
        }
        
        missing_optional = []
        for file_path, description in optional_files.items():
            full_path = self.project_root / file_path
            if not full_path.exists():
                missing_optional.append((file_path, description))
                print(f"⚠️ OPTIONNEL: {file_path} - {description}")
            else:
                print(f"✅ {file_path}")
        
        if missing_critical:
            self.critical_issues.extend(missing_critical)
        
        if missing_optional:
            self.warnings.extend([f"Fichier optionnel manquant: {f[0]}" for f in missing_optional])
        
        return {
            "critical_missing": len(missing_critical),
            "total_critical": len(critical_files),
            "optional_missing": len(missing_optional),
            "existing_files": existing_files
        }
    
    def analyze_python_syntax_and_imports(self) -> Dict[str, Any]:
        """Analyse de la syntaxe Python et des imports"""
        print("\n🐍 2. ANALYSE SYNTAXE PYTHON ET IMPORTS")
        print("-" * 50)
        
        python_files = []
        syntax_errors = []
        import_errors = []
        
        # Trouver tous les fichiers Python
        for py_file in self.project_root.rglob("*.py"):
            if any(exclude in str(py_file) for exclude in ["venv", "__pycache__", ".git", "node_modules"]):
                continue
            python_files.append(py_file)
        
        print(f"📊 Fichiers Python trouvés: {len(python_files)}")
        
        for py_file in python_files:
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Vérifier la syntaxe
                try:
                    ast.parse(content)
                    print(f"✅ Syntaxe OK: {py_file.relative_to(self.project_root)}")
                except SyntaxError as e:
                    syntax_errors.append((str(py_file.relative_to(self.project_root)), str(e)))
                    print(f"❌ ERREUR SYNTAXE: {py_file.relative_to(self.project_root)} - {e}")
                
                # Analyser les imports
                try:
                    tree = ast.parse(content)
                    for node in ast.walk(tree):
                        if isinstance(node, ast.Import):
                            for alias in node.names:
                                self._check_import_availability(alias.name, py_file)
                        elif isinstance(node, ast.ImportFrom):
                            if node.module:
                                self._check_import_availability(node.module, py_file)
                except:
                    pass
                    
            except Exception as e:
                syntax_errors.append((str(py_file.relative_to(self.project_root)), f"Erreur lecture: {e}"))
        
        if syntax_errors:
            self.critical_issues.extend(syntax_errors)
        
        return {
            "total_python_files": len(python_files),
            "syntax_errors": len(syntax_errors),
            "import_errors": len(self.broken_imports)
        }
    
    def _check_import_availability(self, module_name: str, file_path: Path):
        """Vérifie la disponibilité d'un module"""
        # Ignorer les imports standards et relatifs
        standard_modules = {
            'os', 'sys', 'json', 'pathlib', 'typing', 'datetime', 'time', 
            'logging', 'asyncio', 'threading', 'subprocess', 'uuid', 're',
            'collections', 'itertools', 'functools', 'operator', 'math'
        }
        
        if (module_name.startswith('.') or 
            module_name in standard_modules or 
            module_name.split('.')[0] in standard_modules):
            return
        
        # Vérifier les modules tiers
        try:
            importlib.import_module(module_name.split('.')[0])
        except ImportError:
            # Vérifier si c'est un module local
            if not self._is_local_module(module_name):
                error_msg = f"Module non disponible: {module_name} dans {file_path.relative_to(self.project_root)}"
                if error_msg not in self.broken_imports:
                    self.broken_imports.append(error_msg)
    
    def _is_local_module(self, module_name: str) -> bool:
        """Vérifie si c'est un module local du projet"""
        local_prefixes = ['config', 'utils', 'agents', 'core', 'scripts', 'data']
        return any(module_name.startswith(prefix) for prefix in local_prefixes)
    
    def analyze_dependencies(self) -> Dict[str, Any]:
        """Analyse des dépendances Python et Node.js"""
        print("\n📦 3. ANALYSE DES DÉPENDANCES")
        print("-" * 50)
        
        # Dépendances Python
        python_deps_status = self._check_python_dependencies()
        
        # Dépendances Node.js
        nodejs_deps_status = self._check_nodejs_dependencies()
        
        return {
            "python": python_deps_status,
            "nodejs": nodejs_deps_status
        }
    
    def _check_python_dependencies(self) -> Dict[str, Any]:
        """Vérifie les dépendances Python"""
        print("🐍 Dépendances Python:")
        
        requirements_file = self.project_root / "requirements.txt"
        if not requirements_file.exists():
            self.critical_issues.append(("requirements.txt", "Fichier manquant"))
            return {"status": "missing", "file_exists": False}
        
        try:
            with open(requirements_file, 'r') as f:
                requirements = [line.strip().split('==')[0].split('>=')[0].split('<=')[0] 
                              for line in f if line.strip() and not line.startswith('#')]
            
            # Dépendances critiques pour le projet
            critical_deps = [
                'fastapi', 'uvicorn', 'pydantic', 'python-multipart',
                'openai', 'transformers', 'torch', 'scikit-learn',
                'pandas', 'numpy', 'requests', 'python-dotenv',
                'chromadb', 'langchain', 'langsmith'
            ]
            
            missing_deps = []
            available_deps = []
            
            for dep in critical_deps:
                try:
                    __import__(dep.replace('-', '_'))
                    available_deps.append(dep)
                    print(f"✅ {dep}")
                except ImportError:
                    missing_deps.append(dep)
                    print(f"❌ {dep} - NON INSTALLÉ")
            
            if missing_deps:
                self.critical_issues.append(("Python Dependencies", f"Packages manquants: {missing_deps}"))
            
            return {
                "status": "ok" if not missing_deps else "incomplete",
                "file_exists": True,
                "total_requirements": len(requirements),
                "critical_available": len(available_deps),
                "critical_missing": len(missing_deps),
                "missing_packages": missing_deps
            }
            
        except Exception as e:
            self.critical_issues.append(("Python Dependencies", f"Erreur: {e}"))
            return {"status": "error", "error": str(e)}
    
    def _check_nodejs_dependencies(self) -> Dict[str, Any]:
        """Vérifie les dépendances Node.js"""
        print("\n⚛️ Dépendances Node.js:")
        
        package_json = self.project_root / "package.json"
        if not package_json.exists():
            self.critical_issues.append(("package.json", "Fichier manquant"))
            return {"status": "missing", "file_exists": False}
        
        try:
            with open(package_json, 'r') as f:
                package_data = json.load(f)
            
            dependencies = package_data.get("dependencies", {})
            dev_dependencies = package_data.get("devDependencies", {})
            
            # Dépendances critiques Next.js
            critical_deps = ["next", "react", "react-dom"]
            missing_deps = [dep for dep in critical_deps if dep not in dependencies]
            
            # Vérifier node_modules
            node_modules = self.project_root / "node_modules"
            node_modules_exists = node_modules.exists()
            
            for dep in critical_deps:
                if dep in dependencies:
                    print(f"✅ {dep} - {dependencies[dep]}")
                else:
                    print(f"❌ {dep} - MANQUANT")
            
            if missing_deps:
                self.critical_issues.append(("Node.js Dependencies", f"Packages manquants: {missing_deps}"))
            
            if not node_modules_exists:
                self.warnings.append("node_modules manquant - exécuter 'npm install'")
                print("⚠️ node_modules manquant - exécuter 'npm install'")
            
            return {
                "status": "ok" if not missing_deps else "incomplete",
                "file_exists": True,
                "node_modules_exists": node_modules_exists,
                "total_dependencies": len(dependencies),
                "missing_critical": missing_deps,
                "has_scripts": "scripts" in package_data
            }
            
        except Exception as e:
            self.critical_issues.append(("Node.js Dependencies", f"Erreur: {e}"))
            return {"status": "error", "error": str(e)}
    
    def analyze_configuration(self) -> Dict[str, Any]:
        """Analyse de la configuration du projet"""
        print("\n⚙️ 4. ANALYSE DE LA CONFIGURATION")
        print("-" * 50)
        
        config_status = {}
        
        # Variables d'environnement
        config_status["environment"] = self._check_environment_variables()
        
        # Configuration des modèles
        config_status["models"] = self._check_models_configuration()
        
        # Configuration générale
        config_status["settings"] = self._check_general_settings()
        
        return config_status
    
    def _check_environment_variables(self) -> Dict[str, Any]:
        """Vérifie les variables d'environnement"""
        print("🔧 Variables d'environnement:")
        
        env_file = self.project_root / ".env"
        if not env_file.exists():
            self.critical_issues.append((".env", "Fichier .env manquant"))
            print("❌ Fichier .env manquant")
            return {"status": "missing"}
        
        try:
            # Charger les variables
            env_vars = {}
            with open(env_file, 'r') as f:
                for line in f:
                    if '=' in line and not line.startswith('#'):
                        key, value = line.strip().split('=', 1)
                        env_vars[key] = value
            
            # Variables critiques
            critical_vars = {
                "OPENAI_API_KEY": "Clé API OpenAI",
                "HUGGINGFACE_USERNAME": "Nom d'utilisateur Hugging Face", 
                "HUGGINGFACE_TOKEN": "Token Hugging Face",
                "API_PORT": "Port de l'API",
                "UI_PORT": "Port du frontend"
            }
            
            missing_vars = []
            configured_vars = []
            
            for var, description in critical_vars.items():
                if var in env_vars and env_vars[var] and not env_vars[var].startswith("your_"):
                    configured_vars.append(var)
                    print(f"✅ {var}: Configuré")
                else:
                    missing_vars.append((var, description))
                    print(f"❌ {var}: {description} - NON CONFIGURÉ")
            
            if missing_vars:
                self.critical_issues.extend(missing_vars)
            
            return {
                "status": "ok" if not missing_vars else "incomplete",
                "file_exists": True,
                "total_vars": len(env_vars),
                "configured_critical": len(configured_vars),
                "missing_critical": len(missing_vars)
            }
            
        except Exception as e:
            self.critical_issues.append(("Environment Variables", f"Erreur: {e}"))
            return {"status": "error", "error": str(e)}
    
    def _check_models_configuration(self) -> Dict[str, Any]:
        """Vérifie la configuration des modèles"""
        print("\n🤖 Configuration des modèles:")
        
        models_config_file = self.project_root / "config" / "models_urls.py"
        if not models_config_file.exists():
            self.critical_issues.append(("config/models_urls.py", "Configuration des modèles manquante"))
            print("❌ config/models_urls.py manquant")
            return {"status": "missing"}
        
        try:
            # Importer la configuration
            sys.path.insert(0, str(self.project_root))
            from config.models_urls import MODELS_URLS, HUGGING_FACE_USERNAME
            
            expected_models = ["network_analyzer", "intent_classifier", "vulnerability_classifier"]
            configured_models = list(MODELS_URLS.keys())
            
            missing_models = [model for model in expected_models if model not in configured_models]
            
            for model in expected_models:
                if model in configured_models:
                    print(f"✅ {model}: Configuré")
                    # Vérifier les fichiers du modèle
                    model_files = MODELS_URLS[model].get("files", {})
                    print(f"   📁 Fichiers: {len(model_files)}")
                else:
                    print(f"❌ {model}: MANQUANT")
            
            if missing_models:
                self.critical_issues.append(("Models Configuration", f"Modèles manquants: {missing_models}"))
            
            print(f"👤 Username HF: {HUGGING_FACE_USERNAME}")
            
            return {
                "status": "ok" if not missing_models else "incomplete",
                "file_exists": True,
                "configured_models": len(configured_models),
                "missing_models": missing_models,
                "username": HUGGING_FACE_USERNAME
            }
            
        except Exception as e:
            self.critical_issues.append(("Models Configuration", f"Erreur d'import: {e}"))
            print(f"❌ Erreur d'import: {e}")
            return {"status": "error", "error": str(e)}
    
    def _check_general_settings(self) -> Dict[str, Any]:
        """Vérifie la configuration générale"""
        print("\n⚙️ Configuration générale:")
        
        settings_file = self.project_root / "config" / "settings.py"
        if not settings_file.exists():
            self.warnings.append("config/settings.py manquant")
            print("⚠️ config/settings.py manquant")
            return {"status": "missing", "severity": "warning"}
        
        try:
            # Vérifier que le fichier peut être importé
            sys.path.insert(0, str(self.project_root))
            import config.settings
            print("✅ Configuration générale importable")
            
            return {"status": "ok", "file_exists": True}
            
        except Exception as e:
            self.warnings.append(f"Erreur import settings: {e}")
            print(f"⚠️ Erreur import: {e}")
            return {"status": "error", "error": str(e), "severity": "warning"}
    
    def analyze_agents_implementation(self) -> Dict[str, Any]:
        """Analyse de l'implémentation des agents"""
        print("\n🤖 5. ANALYSE DES AGENTS")
        print("-" * 50)
        
        agents_status = {}
        
        # Agent de base
        agents_status["base_agent"] = self._check_base_agent()
        
        # Agent de support
        agents_status["support_agent"] = self._check_support_agent()
        
        # Agent de cybersécurité
        agents_status["cybersecurity_agent"] = self._check_cybersecurity_agent()
        
        return agents_status
    
    def _check_base_agent(self) -> Dict[str, Any]:
        """Vérifie l'agent de base"""
        print("🔧 Agent de base:")
        
        base_agent_file = self.project_root / "agents" / "base_agent.py"
        if not base_agent_file.exists():
            self.critical_issues.append(("agents/base_agent.py", "Classe de base manquante"))
            print("❌ agents/base_agent.py manquant")
            return {"status": "missing"}
        
        try:
            with open(base_agent_file, 'r') as f:
                content = f.read()
            
            # Vérifier les éléments essentiels
            required_elements = ["class BaseAgent", "def __init__", "async def process"]
            missing_elements = [elem for elem in required_elements if elem not in content]
            
            if missing_elements:
                self.critical_issues.append(("BaseAgent", f"Éléments manquants: {missing_elements}"))
                print(f"❌ Éléments manquants: {missing_elements}")
                return {"status": "incomplete", "missing_elements": missing_elements}
            
            print("✅ BaseAgent correctement défini")
            return {"status": "ok"}
            
        except Exception as e:
            self.critical_issues.append(("BaseAgent", f"Erreur: {e}"))
            return {"status": "error", "error": str(e)}
    
    def _check_support_agent(self) -> Dict[str, Any]:
        """Vérifie l'agent de support"""
        print("\n🎧 Agent de support:")
        
        support_agent_file = self.project_root / "agents" / "support_agent" / "agent.py"
        if not support_agent_file.exists():
            self.critical_issues.append(("agents/support_agent/agent.py", "Agent de support manquant"))
            print("❌ agents/support_agent/agent.py manquant")
            return {"status": "missing"}
        
        try:
            with open(support_agent_file, 'r') as f:
                content = f.read()
            
            # Vérifier la classe et les méthodes
            required_elements = [
                "class SupportAgent",
                "async def process_message",
                "async def process_request"
            ]
            
            missing_elements = []
            for elem in required_elements:
                if elem not in content:
                    missing_elements.append(elem)
            
            # Vérifier les imports
            import_issues = []
            if "from agents.base_agent import BaseAgent" not in content:
                import_issues.append("Import BaseAgent manquant")
            
            if missing_elements or import_issues:
                issues = missing_elements + import_issues
                self.critical_issues.append(("SupportAgent", f"Problèmes: {issues}"))
                print(f"❌ Problèmes: {issues}")
                return {"status": "incomplete", "issues": issues}
            
            print("✅ SupportAgent correctement implémenté")
            return {"status": "ok"}
            
        except Exception as e:
            self.critical_issues.append(("SupportAgent", f"Erreur: {e}"))
            return {"status": "error", "error": str(e)}
    
    def _check_cybersecurity_agent(self) -> Dict[str, Any]:
        """Vérifie l'agent de cybersécurité"""
        print("\n🛡️ Agent de cybersécurité:")
        
        cyber_agent_file = self.project_root / "agents" / "cybersecurity_agent" / "agent.py"
        if not cyber_agent_file.exists():
            self.critical_issues.append(("agents/cybersecurity_agent/agent.py", "Agent cybersécurité manquant"))
            print("❌ agents/cybersecurity_agent/agent.py manquant")
            return {"status": "missing"}
        
        try:
            with open(cyber_agent_file, 'r') as f:
                content = f.read()
            
            # Vérifier la classe et les méthodes
            required_elements = [
                "class CybersecurityAgent",
                "async def scan_url",
                "async def process_request"
            ]
            
            missing_elements = []
            for elem in required_elements:
                if elem not in content:
                    missing_elements.append(elem)
            
            if missing_elements:
                self.critical_issues.append(("CybersecurityAgent", f"Éléments manquants: {missing_elements}"))
                print(f"❌ Éléments manquants: {missing_elements}")
                return {"status": "incomplete", "missing_elements": missing_elements}
            
            print("✅ CybersecurityAgent correctement implémenté")
            return {"status": "ok"}
            
        except Exception as e:
            self.critical_issues.append(("CybersecurityAgent", f"Erreur: {e}"))
            return {"status": "error", "error": str(e)}
    
    def analyze_api_server(self) -> Dict[str, Any]:
        """Analyse du serveur API"""
        print("\n🔌 6. ANALYSE DU SERVEUR API")
        print("-" * 50)
        
        api_file = self.project_root / "api" / "server.py"
        if not api_file.exists():
            self.critical_issues.append(("api/server.py", "Serveur API manquant"))
            print("❌ api/server.py manquant")
            return {"status": "missing"}
        
        try:
            with open(api_file, 'r') as f:
                content = f.read()
            
            # Éléments critiques pour FastAPI
            required_elements = {
                "from fastapi import FastAPI": "Import FastAPI",
                "app = FastAPI": "Instance FastAPI",
                "@app.get": "Endpoints GET",
                "@app.post": "Endpoints POST",
                "uvicorn": "Serveur ASGI"
            }
            
            missing_elements = []
            for element, description in required_elements.items():
                if element not in content:
                    missing_elements.append((element, description))
                else:
                    print(f"✅ {description}")
            
            # Vérifier les endpoints critiques
            critical_endpoints = ["/health", "/chat", "/security/scan"]
            missing_endpoints = []
            
            for endpoint in critical_endpoints:
                if endpoint not in content:
                    missing_endpoints.append(endpoint)
                else:
                    print(f"✅ Endpoint: {endpoint}")
            
            if missing_elements:
                self.critical_issues.extend(missing_elements)
                print(f"❌ Éléments manquants: {[e[0] for e in missing_elements]}")
            
            if missing_endpoints:
                self.warnings.extend([f"Endpoint manquant: {ep}" for ep in missing_endpoints])
                print(f"⚠️ Endpoints manquants: {missing_endpoints}")
            
            return {
                "status": "ok" if not missing_elements else "incomplete",
                "missing_elements": len(missing_elements),
                "missing_endpoints": len(missing_endpoints),
                "file_exists": True
            }
            
        except Exception as e:
            self.critical_issues.append(("API Server", f"Erreur: {e}"))
            return {"status": "error", "error": str(e)}
    
    def analyze_frontend(self) -> Dict[str, Any]:
        """Analyse du frontend Next.js"""
        print("\n⚛️ 7. ANALYSE DU FRONTEND NEXT.JS")
        print("-" * 50)
        
        # Vérifier les fichiers Next.js critiques
        nextjs_files = {
            "app/page.tsx": "Page principale",
            "app/layout.tsx": "Layout principal",
            "package.json": "Configuration Node.js",
            "next.config.mjs": "Configuration Next.js",
            "tailwind.config.ts": "Configuration Tailwind"
        }
        
        missing_files = []
        for file_path, description in nextjs_files.items():
            full_path = self.project_root / file_path
            if not full_path.exists():
                missing_files.append((file_path, description))
                print(f"❌ {file_path} - {description}")
            else:
                print(f"✅ {file_path}")
        
        # Vérifier package.json en détail
        package_status = self._analyze_package_json()
        
        if missing_files:
            self.critical_issues.extend(missing_files)
        
        return {
            "status": "ok" if not missing_files else "incomplete",
            "missing_files": len(missing_files),
            "package_json": package_status
        }
    
    def _analyze_package_json(self) -> Dict[str, Any]:
        """Analyse détaillée du package.json"""
        package_json = self.project_root / "package.json"
        if not package_json.exists():
            return {"status": "missing"}
        
        try:
            with open(package_json, 'r') as f:
                package_data = json.load(f)
            
            # Scripts requis
            required_scripts = ["dev", "build", "start"]
            scripts = package_data.get("scripts", {})
            missing_scripts = [script for script in required_scripts if script not in scripts]
            
            # Dépendances critiques
            dependencies = package_data.get("dependencies", {})
            required_deps = ["next", "react", "react-dom"]
            missing_deps = [dep for dep in required_deps if dep not in dependencies]
            
            for script in required_scripts:
                if script in scripts:
                    print(f"✅ Script: {script}")
                else:
                    print(f"❌ Script manquant: {script}")
            
            if missing_scripts:
                self.warnings.extend([f"Script manquant: {script}" for script in missing_scripts])
            
            if missing_deps:
                self.critical_issues.extend([(f"Dependency: {dep}", "Dépendance critique") for dep in missing_deps])
            
            return {
                "status": "ok" if not missing_deps else "incomplete",
                "missing_scripts": missing_scripts,
                "missing_dependencies": missing_deps
            }
            
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def analyze_startup_scripts(self) -> Dict[str, Any]:
        """Analyse des scripts de démarrage"""
        print("\n🚀 8. ANALYSE DES SCRIPTS DE DÉMARRAGE")
        print("-" * 50)
        
        startup_scripts = {
            "scripts/start_system.py": "Script de démarrage principal",
            "scripts/setup_complete_models.py": "Configuration des modèles",
            "scripts/test_all_models.py": "Tests des modèles"
        }
        
        missing_scripts = []
        script_status = {}
        
        for script_path, description in startup_scripts.items():
            full_path = self.project_root / script_path
            if not full_path.exists():
                missing_scripts.append((script_path, description))
                print(f"❌ {script_path} - {description}")
                script_status[script_path] = {"status": "missing"}
            else:
                print(f"✅ {script_path}")
                # Vérifier que le script est exécutable
                try:
                    with open(full_path, 'r') as f:
                        content = f.read()
                    
                    if "if __name__ == '__main__':" in content:
                        script_status[script_path] = {"status": "ok", "executable": True}
                    else:
                        script_status[script_path] = {"status": "warning", "executable": False}
                        self.warnings.append(f"{script_path} non exécutable directement")
                        
                except Exception as e:
                    script_status[script_path] = {"status": "error", "error": str(e)}
        
        if missing_scripts:
            self.critical_issues.extend(missing_scripts)
        
        return {
            "status": "ok" if not missing_scripts else "incomplete",
            "missing_scripts": len(missing_scripts),
            "script_details": script_status
        }
    
    def generate_final_report(self) -> Dict[str, Any]:
        """Génère le rapport final complet"""
        print("\n" + "=" * 80)
        print("📊 RAPPORT FINAL D'ANALYSE COMPLÈTE")
        print("=" * 80)
        
        # Exécuter toutes les analyses
        analyses = {
            "file_structure": self.analyze_file_structure(),
            "python_syntax": self.analyze_python_syntax_and_imports(),
            "dependencies": self.analyze_dependencies(),
            "configuration": self.analyze_configuration(),
            "agents": self.analyze_agents_implementation(),
            "api_server": self.analyze_api_server(),
            "frontend": self.analyze_frontend(),
            "startup_scripts": self.analyze_startup_scripts()
        }
        
        # Calculer les scores
        total_analyses = len(analyses)
        successful_analyses = sum(1 for analysis in analyses.values() 
                                if analysis.get("status") == "ok")
        
        readiness_percentage = (successful_analyses / total_analyses) * 100
        
        # Déterminer si le projet est prêt
        critical_issues_count = len(self.critical_issues)
        warnings_count = len(self.warnings)
        
        is_ready = (readiness_percentage >= 85 and critical_issues_count == 0)
        
        # Affichage du résumé
        print(f"\n🎯 SCORE DE PRÉPARATION: {readiness_percentage:.1f}%")
        print(f"✅ Analyses réussies: {successful_analyses}/{total_analyses}")
        print(f"❌ Problèmes critiques: {critical_issues_count}")
        print(f"⚠️ Avertissements: {warnings_count}")
        
        # Détails des problèmes critiques
        if self.critical_issues:
            print(f"\n❌ PROBLÈMES CRITIQUES À RÉSOUDRE ({critical_issues_count}):")
            for i, (issue, description) in enumerate(self.critical_issues[:10], 1):
                print(f"  {i}. {issue}: {description}")
            if critical_issues_count > 10:
                print(f"  ... et {critical_issues_count - 10} autres problèmes")
        
        # Avertissements
        if self.warnings:
            print(f"\n⚠️ AVERTISSEMENTS ({warnings_count}):")
            for i, warning in enumerate(self.warnings[:5], 1):
                print(f"  {i}. {warning}")
            if warnings_count > 5:
                print(f"  ... et {warnings_count - 5} autres avertissements")
        
        # Verdict final
        print(f"\n{'🎉 PROJET PRÊT À DÉMARRER!' if is_ready else '🔧 CONFIGURATION REQUISE'}")
        
        if is_ready:
            print("\n🚀 COMMANDES POUR DÉMARRER:")
            print("  1. pip install -r requirements.txt")
            print("  2. npm install")
            print("  3. python scripts/setup_complete_models.py")
            print("  4. python scripts/start_system.py")
        else:
            print("\n📋 ACTIONS REQUISES:")
            print("  1. Corriger tous les problèmes critiques listés")
            print("  2. Installer les dépendances manquantes")
            print("  3. Configurer les variables d'environnement")
            print("  4. Compléter les fichiers manquants")
            print("  5. Relancer cette analyse")
        
        # Sauvegarder le rapport
        report = {
            "readiness_percentage": readiness_percentage,
            "is_ready": is_ready,
            "successful_analyses": successful_analyses,
            "total_analyses": total_analyses,
            "critical_issues_count": critical_issues_count,
            "warnings_count": warnings_count,
            "critical_issues": self.critical_issues,
            "warnings": self.warnings,
            "detailed_analyses": analyses,
            "timestamp": str(Path(__file__).stat().st_mtime)
        }
        
        report_file = self.project_root / "comprehensive_analysis_report.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"\n📄 Rapport détaillé sauvegardé: {report_file}")
        
        return report

def main():
    """Point d'entrée principal"""
    analyzer = ComprehensiveProjectAnalyzer()
    report = analyzer.generate_final_report()
    
    # Code de sortie basé sur la préparation
    exit_code = 0 if report["is_ready"] else 1
    sys.exit(exit_code)

if __name__ == "__main__":
    main()

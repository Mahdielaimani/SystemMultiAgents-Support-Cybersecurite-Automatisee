#!/usr/bin/env python3
"""
Script de nettoyage du projet NextGen-Agent
Supprime les fichiers inutiles et optimise la structure
"""

import os
import shutil
import glob
from pathlib import Path

def cleanup_project():
    """Nettoie le projet en supprimant les fichiers inutiles"""
    
    print("🧹 NETTOYAGE DU PROJET NEXTGEN-AGENT")
    print("=" * 50)
    
    # Dossier racine du projet
    project_root = Path(__file__).parent.parent
    
    # Fichiers et dossiers à supprimer
    cleanup_patterns = [
        # Fichiers temporaires Python
        "**/__pycache__",
        "**/*.pyc",
        "**/*.pyo",
        "**/*.pyd",
        "**/.pytest_cache",
        
        # Fichiers de backup
        "**/*~",
        "**/*.bak",
        "**/*.backup",
        
        # Logs anciens
        "**/*.log",
        "logs/*",
        
        # Données temporaires
        "temp/*",
        "tmp/*",
        "cache/*",
        
        # Scripts de test obsolètes (garder les principaux)
        "scripts/test_*",
        "scripts/debug_*",
        "scripts/fix_*",
        "scripts/diagnose_*",
        "scripts/analyze_*",
        "scripts/enhance_*",
        "scripts/restart_*",
        "scripts/emergency_*",
        "scripts/force_*",
        "scripts/auto_*",
        "scripts/quick_*",
        "scripts/final_*",
        "scripts/simple_*",
        "scripts/verify_*",
        "scripts/check_*",
        "scripts/setup_*",
        "scripts/install_*",
        "scripts/create_*",
        "scripts/show_*",
        "scripts/explain_*",
        "scripts/monitor_*",
        "scripts/optimize_*",
        "scripts/run_*",
        "scripts/start_*",
        "scripts/integrate_*",
        "scripts/scrape_*",
        "scripts/use_*",
        
        # Fichiers de configuration temporaires
        "*.tmp",
        "*.temp",
        
        # Données de test
        "test_data/*",
        "scraped_data/*",
    ]
    
    # Fichiers à garder absolument
    keep_files = [
        "scripts/ingest_knowledge_base.py",
        "scripts/ingest_all_data.py",
        "main.py",
        "setup.py",
        "requirements.txt",
        "README.md",
        ".env",
        ".env.example"
    ]
    
    deleted_count = 0
    
    for pattern in cleanup_patterns:
        for path in glob.glob(str(project_root / pattern), recursive=True):
            path_obj = Path(path)
            
            # Vérifier si le fichier doit être gardé
            relative_path = path_obj.relative_to(project_root)
            if str(relative_path) in keep_files:
                continue
                
            try:
                if path_obj.is_file():
                    path_obj.unlink()
                    print(f"🗑️  Supprimé: {relative_path}")
                    deleted_count += 1
                elif path_obj.is_dir():
                    shutil.rmtree(path_obj)
                    print(f"📁 Dossier supprimé: {relative_path}")
                    deleted_count += 1
            except Exception as e:
                print(f"❌ Erreur lors de la suppression de {relative_path}: {e}")
    
    # Créer les dossiers nécessaires
    essential_dirs = [
        "data/vector_db",
        "data/graph_db", 
        "data/knowledge_base",
        "logs",
        "agents/support_agent/tools",
        "agents/cybersecurity_agent",
        "core",
        "utils"
    ]
    
    for dir_path in essential_dirs:
        full_path = project_root / dir_path
        full_path.mkdir(parents=True, exist_ok=True)
        
        # Créer __init__.py si nécessaire
        if "agents" in dir_path or "core" in dir_path or "utils" in dir_path:
            init_file = full_path / "__init__.py"
            if not init_file.exists():
                init_file.touch()
    
    print(f"\n✅ NETTOYAGE TERMINÉ!")
    print(f"📊 {deleted_count} fichiers/dossiers supprimés")
    print(f"🏗️  Structure du projet optimisée")
    
    # Afficher la structure finale
    print("\n📁 STRUCTURE FINALE:")
    show_tree(project_root, max_depth=2)

def show_tree(path, prefix="", max_depth=3, current_depth=0):
    """Affiche l'arborescence du projet"""
    if current_depth >= max_depth:
        return
        
    items = sorted(path.iterdir(), key=lambda x: (x.is_file(), x.name))
    
    for i, item in enumerate(items):
        if item.name.startswith('.'):
            continue
            
        is_last = i == len(items) - 1
        current_prefix = "└── " if is_last else "├── "
        print(f"{prefix}{current_prefix}{item.name}")
        
        if item.is_dir() and current_depth < max_depth - 1:
            extension = "    " if is_last else "│   "
            show_tree(item, prefix + extension, max_depth, current_depth + 1)

if __name__ == "__main__":
    cleanup_project()

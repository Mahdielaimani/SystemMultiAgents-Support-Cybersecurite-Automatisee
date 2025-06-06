#!/usr/bin/env python3
"""
Script de nettoyage automatique de la structure du projet NextGen-Agent
Supprime les fichiers inutiles et organise la structure
"""

import os
import shutil
import glob
from pathlib import Path
import json

class ProjectCleaner:
    """Nettoyeur de projet automatique"""
    
    def __init__(self):
        self.project_root = Path(".")
        self.deleted_files = []
        self.moved_files = []
        self.errors = []
        
    def clean_backup_files(self):
        """Supprime tous les fichiers de sauvegarde"""
        print("🧹 Nettoyage des fichiers de sauvegarde...")
        
        backup_patterns = [
            "**/*.bak",
            "**/*.bak2", 
            "**/*.bak.*",
            "**/*.syntax_backup",
            "**/agent.py.bak.*",
            "**/server.py.bak.*"
        ]
        
        for pattern in backup_patterns:
            for file_path in self.project_root.glob(pattern):
                try:
                    file_path.unlink()
                    self.deleted_files.append(str(file_path))
                    print(f"  ❌ Supprimé: {file_path}")
                except Exception as e:
                    self.errors.append(f"Erreur suppression {file_path}: {e}")
    
    def clean_chroma_duplicates(self):
        """Consolide les bases de données ChromaDB"""
        print("🗄️ Consolidation des bases ChromaDB...")
        
        # Garder seulement ./data/vector_db/chroma_db/
        chroma_dirs_to_remove = [
            "./chroma_db",
            "./data/chroma_db"
        ]
        
        target_dir = Path("./data/vector_db/chroma_db")
        target_dir.mkdir(parents=True, exist_ok=True)
        
        for chroma_dir in chroma_dirs_to_remove:
            chroma_path = Path(chroma_dir)
            if chroma_path.exists():
                try:
                    # Copier les données importantes si nécessaire
                    if (chroma_path / "chroma.sqlite3").exists():
                        print(f"  📋 Sauvegarde de {chroma_dir}/chroma.sqlite3")
                        shutil.copy2(
                            chroma_path / "chroma.sqlite3",
                            target_dir / f"backup_{chroma_path.name}.sqlite3"
                        )
                    
                    shutil.rmtree(chroma_path)
                    self.deleted_files.append(str(chroma_path))
                    print(f"  ❌ Supprimé: {chroma_path}")
                except Exception as e:
                    self.errors.append(f"Erreur suppression {chroma_path}: {e}")
    
    def clean_temporary_files(self):
        """Supprime les fichiers temporaires"""
        print("🗑️ Nettoyage des fichiers temporaires...")
        
        temp_files = [
            "comprehensive_analysis_report.json",
            "component_verification_results.json", 
            "guardian_report_*.json",
            "health_report.json",
            "kaggle_models_test_results.json",
            "analyze_structure.py"
        ]
        
        for pattern in temp_files:
            for file_path in self.project_root.glob(pattern):
                try:
                    file_path.unlink()
                    self.deleted_files.append(str(file_path))
                    print(f"  ❌ Supprimé: {file_path}")
                except Exception as e:
                    self.errors.append(f"Erreur suppression {file_path}: {e}")
    
    def clean_ui_structure(self):
        """Organise la structure UI"""
        print("⚛️ Organisation de la structure UI...")
        
        # Supprimer ./ui/src/ car on utilise ./components/
        ui_src_path = Path("./ui/src")
        if ui_src_path.exists():
            try:
                shutil.rmtree(ui_src_path)
                self.deleted_files.append(str(ui_src_path))
                print(f"  ❌ Supprimé: {ui_src_path} (redondant avec ./components/)")
            except Exception as e:
                self.errors.append(f"Erreur suppression {ui_src_path}: {e}")
        
        # Supprimer le dossier ui/ vide
        ui_path = Path("./ui")
        if ui_path.exists() and not any(ui_path.iterdir()):
            try:
                ui_path.rmdir()
                self.deleted_files.append(str(ui_path))
                print(f"  ❌ Supprimé: {ui_path} (vide)")
            except Exception as e:
                self.errors.append(f"Erreur suppression {ui_path}: {e}")
    
    def clean_next_cache(self):
        """Nettoie le cache Next.js"""
        print("🔄 Nettoyage du cache Next.js...")
        
        next_cache = Path("./.next")
        if next_cache.exists():
            try:
                shutil.rmtree(next_cache)
                self.deleted_files.append(str(next_cache))
                print(f"  ❌ Supprimé: {next_cache} (cache)")
            except Exception as e:
                self.errors.append(f"Erreur suppression {next_cache}: {e}")
    
    def organize_env_files(self):
        """Organise les fichiers d'environnement"""
        print("🔧 Organisation des fichiers d'environnement...")
        
        # Garder seulement .env et .env.example
        env_files_to_check = [".env.local"]
        
        for env_file in env_files_to_check:
            env_path = Path(env_file)
            if env_path.exists():
                # Vérifier si le contenu est différent de .env
                try:
                    with open(env_path, 'r') as f:
                        content = f.read()
                    
                    if not content.strip() or content == open('.env', 'r').read():
                        env_path.unlink()
                        self.deleted_files.append(str(env_path))
                        print(f"  ❌ Supprimé: {env_path} (redondant)")
                except Exception as e:
                    print(f"  ⚠️ Vérification manuelle requise pour {env_path}")
    
    def clean_duplicate_components(self):
        """Supprime les composants dupliqués"""
        print("🎨 Nettoyage des composants dupliqués...")
        
        # Identifier les composants similaires
        component_files = list(Path("./components").glob("*.tsx"))
        
        duplicates_to_remove = [
            "chat-interface.tsx",  # Garder ai-enhanced-chat-interface.tsx
            "modern-chat-interface.tsx",  # Garder ai-enhanced-chat-interface.tsx
            "animated-guardian-robot.tsx",  # Garder autonomous-guardian-robot.tsx
        ]
        
        for duplicate in duplicates_to_remove:
            duplicate_path = Path(f"./components/{duplicate}")
            if duplicate_path.exists():
                try:
                    duplicate_path.unlink()
                    self.deleted_files.append(str(duplicate_path))
                    print(f"  ❌ Supprimé: {duplicate_path} (doublon)")
                except Exception as e:
                    self.errors.append(f"Erreur suppression {duplicate_path}: {e}")
    
    def create_cleanup_report(self):
        """Crée un rapport de nettoyage"""
        report = {
            "timestamp": "2025-05-31",
            "deleted_files": self.deleted_files,
            "moved_files": self.moved_files,
            "errors": self.errors,
            "summary": {
                "total_deleted": len(self.deleted_files),
                "total_moved": len(self.moved_files),
                "total_errors": len(self.errors)
            }
        }
        
        with open("cleanup_report.json", "w") as f:
            json.dump(report, f, indent=2)
        
        print(f"\n📊 RAPPORT DE NETTOYAGE:")
        print(f"  ❌ Fichiers supprimés: {len(self.deleted_files)}")
        print(f"  📁 Fichiers déplacés: {len(self.moved_files)}")
        print(f"  ⚠️ Erreurs: {len(self.errors)}")
        
        if self.errors:
            print(f"\n⚠️ ERREURS:")
            for error in self.errors:
                print(f"  - {error}")
    
    def run_cleanup(self):
        """Exécute le nettoyage complet"""
        print("🚀 DÉBUT DU NETTOYAGE DU PROJET")
        print("=" * 50)
        
        self.clean_backup_files()
        self.clean_chroma_duplicates()
        self.clean_temporary_files()
        self.clean_ui_structure()
        self.clean_next_cache()
        self.organize_env_files()
        self.clean_duplicate_components()
        
        self.create_cleanup_report()
        
        print("\n✅ NETTOYAGE TERMINÉ!")
        print("=" * 50)

def main():
    """Point d'entrée principal"""
    cleaner = ProjectCleaner()
    cleaner.run_cleanup()

if __name__ == "__main__":
    main()

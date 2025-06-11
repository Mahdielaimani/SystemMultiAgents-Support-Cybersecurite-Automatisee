#!/usr/bin/env python3
"""
Script pour nettoyer toutes les données en cache et réinitialiser le système
Supprime les conversations, alertes, sessions et réinitialise l'état
"""
import os
import json
import shutil
from pathlib import Path
from datetime import datetime

class SystemCleaner:
    def __init__(self):
        self.cleaned_items = []
        self.errors = []
        
    def print_banner(self):
        """Affiche le banner"""
        print(f"""
╔══════════════════════════════════════════════════════════════════════════╗
║                    🧹 NETTOYAGE SYSTÈME COMPLET 🧹                        ║
║                                                                          ║
║  Suppression du cache, conversations, alertes et réinitialisation        ║
║                                                                          ║
╚══════════════════════════════════════════════════════════════════════════╝

Démarré le: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
""")

    def clean_memory_files(self):
        """Nettoie les fichiers de mémoire conversationnelle"""
        print("\n📁 Nettoyage des fichiers de mémoire...")
        
        memory_paths = [
            "data/memory/conversations.json",
            "data/memory/agent_memory.json",
            "data/memory/"
        ]
        
        for path in memory_paths:
            try:
                if os.path.isfile(path):
                    # Sauvegarder avant suppression
                    backup_path = f"{path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                    shutil.copy2(path, backup_path)
                    
                    # Remplacer par un fichier vide
                    with open(path, 'w') as f:
                        json.dump({}, f)
                    
                    print(f"   ✅ Nettoyé: {path}")
                    print(f"      → Sauvegarde: {backup_path}")
                    self.cleaned_items.append(path)
                    
                elif os.path.isdir(path):
                    # Nettoyer tous les fichiers JSON dans le dossier
                    json_files = list(Path(path).glob("*.json"))
                    for json_file in json_files:
                        if "backup" not in str(json_file):
                            backup_path = f"{json_file}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                            shutil.copy2(json_file, backup_path)
                            
                            with open(json_file, 'w') as f:
                                json.dump({}, f)
                            
                            print(f"   ✅ Nettoyé: {json_file}")
                            self.cleaned_items.append(str(json_file))
                            
            except Exception as e:
                print(f"   ❌ Erreur pour {path}: {e}")
                self.errors.append(f"{path}: {e}")

    def clean_vector_db(self):
        """Nettoie la base de données vectorielle ChromaDB"""
        print("\n🗄️ Nettoyage de ChromaDB...")
        
        chroma_paths = [
            "data/vector_db/chroma_db",
            "./data/vector_db/chroma_db",
            "data/vector_db"
        ]
        
        for path in chroma_paths:
            try:
                if os.path.exists(path):
                    # Créer une sauvegarde
                    backup_path = f"{path}_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                    if os.path.isdir(path):
                        shutil.copytree(path, backup_path)
                        
                        # Supprimer le contenu mais garder le dossier
                        for item in os.listdir(path):
                            item_path = os.path.join(path, item)
                            if os.path.isfile(item_path):
                                os.remove(item_path)
                            elif os.path.isdir(item_path) and "backup" not in item:
                                shutil.rmtree(item_path)
                        
                        print(f"   ✅ Nettoyé: {path}")
                        print(f"      → Sauvegarde: {backup_path}")
                        self.cleaned_items.append(path)
                        
            except Exception as e:
                print(f"   ❌ Erreur pour {path}: {e}")
                self.errors.append(f"{path}: {e}")

    def clean_api_state(self):
        """Crée un fichier pour réinitialiser l'état de l'API"""
        print("\n🔄 Création du fichier de réinitialisation API...")
        
        reset_state = {
            "reset_requested": True,
            "timestamp": datetime.now().isoformat(),
            "reset_items": [
                "security_alerts",
                "user_activities", 
                "system_state",
                "active_sessions"
            ]
        }
        
        try:
            os.makedirs("data/temp", exist_ok=True)
            reset_file = "data/temp/reset_state.json"
            
            with open(reset_file, 'w') as f:
                json.dump(reset_state, f, indent=2)
            
            print(f"   ✅ Fichier de reset créé: {reset_file}")
            self.cleaned_items.append(reset_file)
            
        except Exception as e:
            print(f"   ❌ Erreur création fichier reset: {e}")
            self.errors.append(f"reset_state: {e}")

    def clean_logs(self):
        """Nettoie les fichiers de logs"""
        print("\n📝 Nettoyage des logs...")
        
        log_patterns = [
            "logs/*.log",
            "*.log",
            "api_server.log"
        ]
        
        for pattern in log_patterns:
            try:
                log_files = list(Path(".").glob(pattern))
                for log_file in log_files:
                    if os.path.exists(log_file):
                        # Sauvegarder
                        backup_path = f"{log_file}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                        shutil.copy2(log_file, backup_path)
                        
                        # Vider le fichier
                        open(log_file, 'w').close()
                        
                        print(f"   ✅ Vidé: {log_file}")
                        self.cleaned_items.append(str(log_file))
                        
            except Exception as e:
                print(f"   ❌ Erreur pour {pattern}: {e}")
                self.errors.append(f"{pattern}: {e}")

    def create_reset_script(self):
        """Crée un script Python pour réinitialiser l'état au démarrage de l'API"""
        print("\n🔧 Création du script de réinitialisation...")
        
        reset_script = '''# api/reset_on_startup.py
"""Script temporaire pour réinitialiser l'état au démarrage"""
import os

def reset_shared_state():
    """Réinitialise l'état partagé"""
    try:
        from api.shared_state import system_state, security_alerts, user_activities, active_sessions
        
        # Réinitialiser l'état système
        system_state.clear()
        system_state.update({
            "blocked": False,
            "threat_level": "safe",
            "block_reason": None,
            "last_block_time": None,
            "active_sessions": {},
            "total_threats_detected": 0,
            "last_scan": None,
            "active_threats": []
        })
        
        # Vider les listes
        security_alerts.clear()
        user_activities.clear()
        active_sessions.clear()
        
        print("✅ État système réinitialisé")
        
        # Supprimer ce script après utilisation
        if os.path.exists(__file__):
            os.remove(__file__)
            print("✅ Script de reset auto-supprimé")
            
    except Exception as e:
        print(f"❌ Erreur reset: {e}")

# Exécuter au chargement du module
reset_shared_state()
'''
        
        try:
            with open("api/reset_on_startup.py", 'w') as f:
                f.write(reset_script)
            
            print(f"   ✅ Script de reset créé: api/reset_on_startup.py")
            print(f"      → Ce script s'auto-supprimera après exécution")
            self.cleaned_items.append("api/reset_on_startup.py")
            
        except Exception as e:
            print(f"   ❌ Erreur création script: {e}")
            self.errors.append(f"reset_script: {e}")

    def clean_temp_files(self):
        """Nettoie les fichiers temporaires"""
        print("\n🗑️ Nettoyage des fichiers temporaires...")
        
        temp_patterns = [
            "**/__pycache__",
            "**/*.pyc",
            "**/.DS_Store",
            "**/Thumbs.db",
            "data/temp/*"
        ]
        
        for pattern in temp_patterns:
            try:
                items = list(Path(".").glob(pattern))
                for item in items:
                    if item.is_file():
                        item.unlink()
                        print(f"   ✅ Supprimé: {item}")
                    elif item.is_dir():
                        shutil.rmtree(item)
                        print(f"   ✅ Supprimé: {item}/")
                    self.cleaned_items.append(str(item))
                    
            except Exception as e:
                print(f"   ⚠️ Erreur pour {pattern}: {e}")

    def show_summary(self):
        """Affiche le résumé du nettoyage"""
        print(f"\n{'='*70}")
        print("📊 RÉSUMÉ DU NETTOYAGE")
        print(f"{'='*70}")
        
        print(f"\n✅ Éléments nettoyés: {len(self.cleaned_items)}")
        if self.errors:
            print(f"❌ Erreurs rencontrées: {len(self.errors)}")
            for error in self.errors[:5]:  # Afficher max 5 erreurs
                print(f"   - {error}")
        
        print(f"\n🎯 PROCHAINES ÉTAPES:")
        print("1. Ajouter cette ligne au début de api/server.py:")
        print("   ```python")
        print("   try:")
        print("       from api.reset_on_startup import reset_shared_state")
        print("   except:")
        print("       pass")
        print("   ```")
        print("\n2. Redémarrer les services:")
        print("   ```bash")
        print("   python scripts/launch_all_services.py")
        print("   ```")
        print("\n3. Le système sera complètement réinitialisé!")
        
        print(f"\n💡 CONSEIL: Les sauvegardes sont créées avec le suffixe .backup_YYYYMMDD_HHMMSS")

def main():
    """Fonction principale"""
    cleaner = SystemCleaner()
    
    # Afficher le banner
    cleaner.print_banner()
    
    # Confirmation
    print("\n⚠️  ATTENTION: Ce script va nettoyer toutes les données en cache!")
    print("   Des sauvegardes seront créées automatiquement.")
    
    response = input("\n❓ Voulez-vous continuer ? (oui/non): ").strip().lower()
    
    if response not in ['oui', 'o', 'yes', 'y']:
        print("\n❌ Nettoyage annulé.")
        return
    
    print("\n🚀 Démarrage du nettoyage...")
    
    try:
        # Exécuter le nettoyage
        cleaner.clean_memory_files()
        cleaner.clean_vector_db()
        cleaner.clean_api_state()
        cleaner.clean_logs()
        cleaner.create_reset_script()
        cleaner.clean_temp_files()
        
        # Afficher le résumé
        cleaner.show_summary()
        
        print(f"\n✅ NETTOYAGE TERMINÉ!")
        
    except KeyboardInterrupt:
        print("\n\n🛑 Nettoyage interrompu par l'utilisateur")
    except Exception as e:
        print(f"\n❌ Erreur critique: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
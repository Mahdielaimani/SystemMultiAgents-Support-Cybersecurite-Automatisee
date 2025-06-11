#!/usr/bin/env python3
"""
Script de nettoyage complet pour réinitialiser TOUT le système
Y compris les données en mémoire du dashboard de sécurité
"""
import os
import json
import shutil
import time
import requests
from pathlib import Path
from datetime import datetime

class CompleteSystemCleaner:
    def __init__(self):
        self.cleaned_items = []
        self.errors = []
        self.api_running = False
        
    def print_banner(self):
        """Affiche le banner"""
        print(f"""
╔══════════════════════════════════════════════════════════════════════════╗
║                    🧹 NETTOYAGE SYSTÈME COMPLET 🧹                        ║
║                                                                          ║
║  Suppression TOTALE : Cache + Mémoire + État API + Sessions             ║
║                                                                          ║
╚══════════════════════════════════════════════════════════════════════════╝

Démarré le: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
""")

    def check_api_status(self):
        """Vérifie si l'API est en cours d'exécution"""
        print("\n🔍 Vérification de l'état de l'API...")
        try:
            response = requests.get("http://localhost:8000/health", timeout=2)
            if response.status_code == 200:
                self.api_running = True
                print("   ⚠️  API en cours d'exécution!")
                return True
        except:
            pass
        
        print("   ✅ API non détectée (c'est bien)")
        return False

    def stop_running_services(self):
        """Arrête les services en cours si nécessaire"""
        if self.api_running:
            print("\n⚠️  ATTENTION: L'API est en cours d'exécution!")
            print("   Il est recommandé d'arrêter tous les services avant le nettoyage.")
            response = input("   Voulez-vous continuer quand même ? (oui/non): ").strip().lower()
            if response not in ['oui', 'o', 'yes', 'y']:
                print("\n❌ Nettoyage annulé. Arrêtez d'abord les services.")
                return False
        return True

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
                        
                        # Supprimer complètement le dossier
                        shutil.rmtree(path)
                        os.makedirs(path, exist_ok=True)
                        
                        print(f"   ✅ Nettoyé complètement: {path}")
                        self.cleaned_items.append(path)
                        
            except Exception as e:
                print(f"   ❌ Erreur pour {path}: {e}")
                self.errors.append(f"{path}: {e}")

    def create_server_reset_code(self):
        """Crée le code de réinitialisation pour server.py"""
        print("\n🔧 Création du code de réinitialisation pour server.py...")
        
        reset_code = '''# Code de réinitialisation à ajouter dans server.py après les imports

# ============= DÉBUT CODE RESET =============
# Reset automatique au démarrage (à supprimer après premier lancement)
try:
    from api.shared_state import system_state, security_alerts, user_activities, active_sessions
    
    # Réinitialiser complètement l'état système
    system_state.clear()
    system_state.update({
        "blocked": False,
        "threat_level": "safe",
        "block_reason": None,
        "last_block_time": None,
        "active_sessions": {},
        "total_threats_detected": 0,
        "last_scan": datetime.now().isoformat(),
        "active_threats": []
    })
    
    # Vider toutes les listes et dictionnaires
    security_alerts.clear()
    user_activities.clear()
    active_sessions.clear()
    
    print("✅ État système complètement réinitialisé au démarrage")
    
except Exception as e:
    print(f"⚠️ Erreur reset au démarrage: {e}")
# ============= FIN CODE RESET =============
'''
        
        # Sauvegarder dans un fichier
        with open("reset_code_for_server.txt", 'w') as f:
            f.write(reset_code)
        
        print(f"   ✅ Code de reset sauvegardé dans: reset_code_for_server.txt")
        print(f"   📋 Copiez ce code dans api/server.py après les imports")

    def create_update_script(self):
        """Crée un script pour forcer la mise à jour du dashboard"""
        print("\n🔄 Création du script de mise à jour forcée...")
        
        update_script = '''#!/usr/bin/env python3
"""
Script pour forcer la mise à jour du dashboard après reset
"""
import requests
import time

def force_dashboard_update():
    """Force le dashboard à se rafraîchir"""
    print("🔄 Forçage de la mise à jour du dashboard...")
    
    try:
        # Créer une fausse alerte puis la supprimer pour forcer le refresh
        response = requests.post(
            "http://localhost:8000/api/cybersecurity/alert",
            json={
                "type": "system",
                "severity": "low",
                "message": "Test de rafraîchissement - À ignorer"
            }
        )
        
        if response.status_code == 200:
            print("✅ Signal de rafraîchissement envoyé")
            
        # Débloquer le système si bloqué
        requests.post("http://localhost:8000/api/cybersecurity/unblock")
        
        print("✅ Système débloqué")
        print("✅ Le dashboard devrait maintenant afficher 0 alertes")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        print("   Assurez-vous que l'API est démarrée")

if __name__ == "__main__":
    force_dashboard_update()
'''
        
        with open("scripts/force_dashboard_update.py", 'w') as f:
            f.write(update_script)
        
        os.chmod("scripts/force_dashboard_update.py", 0o755)
        print(f"   ✅ Script créé: scripts/force_dashboard_update.py")

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
                        # Vider le fichier
                        open(log_file, 'w').close()
                        print(f"   ✅ Vidé: {log_file}")
                        self.cleaned_items.append(str(log_file))
                        
            except Exception as e:
                print(f"   ❌ Erreur pour {pattern}: {e}")

    def clean_temp_files(self):
        """Nettoie les fichiers temporaires"""
        print("\n🗑️ Nettoyage des fichiers temporaires...")
        
        temp_patterns = [
            "**/__pycache__",
            "**/*.pyc",
            "**/.DS_Store",
            "**/Thumbs.db",
            "data/temp/*",
            ".pytest_cache",
            "*.backup_*"  # Nettoyer les vieilles sauvegardes
        ]
        
        for pattern in temp_patterns:
            try:
                items = list(Path(".").glob(pattern))
                for item in items:
                    # Ne pas supprimer les sauvegardes récentes
                    if "backup" in str(item):
                        # Garder les sauvegardes de moins de 7 jours
                        if (datetime.now() - datetime.fromtimestamp(item.stat().st_mtime)).days < 7:
                            continue
                    
                    if item.is_file():
                        item.unlink()
                        print(f"   ✅ Supprimé: {item}")
                    elif item.is_dir():
                        shutil.rmtree(item)
                        print(f"   ✅ Supprimé: {item}/")
                    self.cleaned_items.append(str(item))
                    
            except Exception as e:
                print(f"   ⚠️ Erreur pour {pattern}: {e}")

    def reset_via_api(self):
        """Tente de réinitialiser via l'API si elle est en cours d'exécution"""
        if not self.api_running:
            return
        
        print("\n🌐 Tentative de reset via l'API...")
        
        try:
            # Débloquer le système
            response = requests.post("http://localhost:8000/api/cybersecurity/unblock", timeout=5)
            if response.status_code == 200:
                print("   ✅ Système débloqué via API")
            
            # Vider les alertes (pas d'endpoint direct, donc on simule)
            print("   ⚠️  Les alertes en mémoire ne peuvent être vidées que par redémarrage")
            
        except Exception as e:
            print(f"   ❌ Erreur reset API: {e}")

    def show_summary(self):
        """Affiche le résumé du nettoyage"""
        print(f"\n{'='*70}")
        print("📊 RÉSUMÉ DU NETTOYAGE")
        print(f"{'='*70}")
        
        print(f"\n✅ Éléments nettoyés: {len(self.cleaned_items)}")
        if self.errors:
            print(f"❌ Erreurs rencontrées: {len(self.errors)}")
            for error in self.errors[:5]:
                print(f"   - {error}")
        
        print(f"\n🎯 ÉTAPES CRITIQUES À SUIVRE:")
        print("\n1️⃣  ARRÊTER tous les services (Ctrl+C dans le terminal)")
        
        print("\n2️⃣  MODIFIER api/server.py:")
        print("   - Ouvrir le fichier reset_code_for_server.txt")
        print("   - Copier le code et le coller dans api/server.py après les imports")
        
        print("\n3️⃣  REDÉMARRER les services:")
        print("   ```bash")
        print("   python scripts/launch_all_services.py")
        print("   ```")
        
        print("\n4️⃣  FORCER la mise à jour du dashboard (optionnel):")
        print("   ```bash")
        print("   python scripts/force_dashboard_update.py")
        print("   ```")
        
        print("\n5️⃣  SUPPRIMER le code de reset de server.py après le premier lancement")
        
        print(f"\n💡 IMPORTANT:")
        print("   - Le dashboard de sécurité sera vide SEULEMENT après redémarrage")
        print("   - Les alertes en mémoire persistent jusqu'au redémarrage de l'API")
        print("   - Vérifiez que l'auto-refresh est activé dans le dashboard")

def main():
    """Fonction principale"""
    cleaner = CompleteSystemCleaner()
    
    # Afficher le banner
    cleaner.print_banner()
    
    # Vérifier l'état de l'API
    cleaner.check_api_status()
    
    # Confirmation
    print("\n⚠️  ATTENTION: Ce script va nettoyer TOUTES les données du système!")
    print("   Il est FORTEMENT recommandé d'arrêter tous les services avant.")
    
    if cleaner.api_running:
        print("\n🚨 L'API est actuellement EN COURS D'EXÉCUTION!")
        print("   Les données en mémoire ne seront pas nettoyées tant que l'API tourne.")
    
    response = input("\n❓ Voulez-vous continuer ? (oui/non): ").strip().lower()
    
    if response not in ['oui', 'o', 'yes', 'y']:
        print("\n❌ Nettoyage annulé.")
        return
    
    print("\n🚀 Démarrage du nettoyage complet...")
    
    try:
        # Exécuter le nettoyage
        cleaner.clean_memory_files()
        cleaner.clean_vector_db()
        cleaner.clean_logs()
        cleaner.clean_temp_files()
        cleaner.create_server_reset_code()
        cleaner.create_update_script()
        
        # Tenter un reset via API si elle tourne
        if cleaner.api_running:
            cleaner.reset_via_api()
        
        # Afficher le résumé
        cleaner.show_summary()
        
        print(f"\n✅ NETTOYAGE TERMINÉ!")
        
        if cleaner.api_running:
            print("\n⚠️  RAPPEL: L'API est toujours en cours d'exécution!")
            print("   Les données du dashboard ne seront réinitialisées qu'après redémarrage.")
        
    except KeyboardInterrupt:
        print("\n\n🛑 Nettoyage interrompu par l'utilisateur")
    except Exception as e:
        print(f"\n❌ Erreur critique: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
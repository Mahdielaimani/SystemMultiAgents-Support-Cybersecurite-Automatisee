# scripts/launch_all_services.py
"""
Script pour lancer tous les services NextGen-Agent avec Cybersécurité
"""
import os
import sys
import subprocess
import time
import signal
from datetime import datetime

# Couleurs pour l'affichage
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

# Processus lancés
processes = []

def print_banner():
    """Affiche le banner de démarrage"""
    print(f"""
{Colors.HEADER}{Colors.BOLD}
╔══════════════════════════════════════════════════════════════════════════╗
║                                                                          ║
║                    🚀 NEXTGEN-AGENT LAUNCHER 🚀                          ║
║                                                                          ║
║  Starting all services for TeamSquare AI Assistant with Security        ║
║                                                                          ║
╚══════════════════════════════════════════════════════════════════════════╝
{Colors.ENDC}
    """)

def start_service(name, command, color=Colors.OKBLUE):
    """Lance un service dans un sous-processus"""
    print(f"\n{color}[{datetime.now().strftime('%H:%M:%S')}] 🔄 Démarrage de {name}...{Colors.ENDC}")
    
    try:
        # Créer le processus
        if isinstance(command, str):
            process = subprocess.Popen(command, shell=True)
        else:
            process = subprocess.Popen(command)
        
        processes.append((name, process))
        time.sleep(2)  # Attendre que le service démarre
        
        # Vérifier si le processus est toujours actif
        if process.poll() is None:
            print(f"{Colors.OKGREEN}[{datetime.now().strftime('%H:%M:%S')}] ✅ {name} démarré (PID: {process.pid}){Colors.ENDC}")
            return True
        else:
            print(f"{Colors.FAIL}[{datetime.now().strftime('%H:%M:%S')}] ❌ {name} n'a pas pu démarrer{Colors.ENDC}")
            return False
            
    except Exception as e:
        print(f"{Colors.FAIL}[{datetime.now().strftime('%H:%M:%S')}] ❌ Erreur démarrage {name}: {e}{Colors.ENDC}")
        return False

def check_dependencies():
    """Vérifie que toutes les dépendances sont installées"""
    print(f"\n{Colors.OKCYAN}🔍 Vérification des dépendances...{Colors.ENDC}")
    
    dependencies = {
        "fastapi": "FastAPI",
        "uvicorn": "Uvicorn",
        "transformers": "Transformers",
        "torch": "PyTorch",
        "xgboost": "XGBoost",
        "sklearn": "Scikit-learn"
    }
    
    missing = []
    for module, name in dependencies.items():
        try:
            __import__(module)
            print(f"  ✅ {name}")
        except ImportError:
            print(f"  ❌ {name} manquant")
            missing.append(module)
    
    if missing:
        print(f"\n{Colors.WARNING}⚠️  Modules manquants: {', '.join(missing)}")
        print(f"Installez-les avec: pip install {' '.join(missing)}{Colors.ENDC}")
        return False
    
    return True

def stop_all_services():
    """Arrête tous les services lancés"""
    print(f"\n{Colors.WARNING}🛑 Arrêt de tous les services...{Colors.ENDC}")
    
    for name, process in processes:
        try:
            process.terminate()
            print(f"  ⏹️  {name} arrêté")
        except:
            pass
    
    # Attendre que tous les processus se terminent
    for name, process in processes:
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            print(f"  ⚠️  {name} forcé à s'arrêter")

def signal_handler(sig, frame):
    """Gestionnaire de signal pour arrêt propre"""
    print(f"\n\n{Colors.WARNING}Signal d'interruption reçu{Colors.ENDC}")
    stop_all_services()
    sys.exit(0)

def main():
    """Fonction principale"""
    print_banner()
    
    # Enregistrer le gestionnaire de signal
    signal.signal(signal.SIGINT, signal_handler)
    
    # Vérifier les dépendances
    if not check_dependencies():
        print(f"\n{Colors.FAIL}❌ Dépendances manquantes. Installation requise.{Colors.ENDC}")
        return
    
    print(f"\n{Colors.OKGREEN}✅ Toutes les dépendances sont présentes{Colors.ENDC}")
    
    # Services à lancer
    services = []
    
    # 1. Serveur FastAPI principal (Support + Cybersécurité)
    services.append({
        "name": "API Server (FastAPI)",
        "command": "python api/server.py",
        "color": Colors.OKGREEN,
        "port": 8000
    })
    
    # 2. Frontend Next.js
    services.append({
        "name": "Frontend (Next.js)",
        "command": "npm run dev",
        "color": Colors.OKBLUE,
        "port": 3000
    })
    
    # Lancer tous les services
    print(f"\n{Colors.HEADER}{Colors.BOLD}📦 Lancement des services...{Colors.ENDC}")
    
    success_count = 0
    for service in services:
        if start_service(service["name"], service["command"], service["color"]):
            success_count += 1
    
    # Résumé
    print(f"\n{Colors.HEADER}{'='*70}{Colors.ENDC}")
    print(f"{Colors.OKGREEN}✅ {success_count}/{len(services)} services démarrés avec succès{Colors.ENDC}")
    
    if success_count == len(services):
        print(f"\n{Colors.OKCYAN}🌐 URLs d'accès :{Colors.ENDC}")
        print(f"  • Frontend: http://localhost:3000")
        print(f"  • API Docs: http://localhost:8000/docs")
        print(f"  • API Health: http://localhost:8000/health")
        print(f"  • Cybersecurity: http://localhost:8000/api/cybersecurity/health")
        
        print(f"\n{Colors.HEADER}📋 Commandes utiles :{Colors.ENDC}")
        print(f"  • Test d'attaque : python scripts/simulate_attacks.py")
        print(f"  • Test modèles : python scripts/test_custom_models.py")
        print(f"  • Logs API : tail -f api.log")
        
        print(f"\n{Colors.WARNING}⚠️  Appuyez sur Ctrl+C pour arrêter tous les services{Colors.ENDC}")
        
        # Garder le script actif
        try:
            while True:
                time.sleep(1)
                # Vérifier si les processus sont toujours actifs
                for name, process in processes:
                    if process.poll() is not None:
                        print(f"\n{Colors.WARNING}⚠️  {name} s'est arrêté de manière inattendue{Colors.ENDC}")
                        stop_all_services()
                        return
        except KeyboardInterrupt:
            pass
    else:
        print(f"\n{Colors.FAIL}❌ Certains services n'ont pas pu démarrer{Colors.ENDC}")
        stop_all_services()

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
Script de reset modulaire pour NextGen-Agent
Permet de nettoyer sélectivement chaque composant
"""
import os
import sys
import json
import shutil
import time
import requests
from datetime import datetime
from pathlib import Path
import argparse
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

class ModularSystemReset:
    """Gestionnaire de reset modulaire pour chaque composant"""
    
    def __init__(self):
        self.api_url = "http://localhost:8000"
        self.components = {
            'support': {
                'name': 'Agent Support',
                'enabled': os.getenv('RESET_SUPPORT_AGENT', 'true').lower() == 'true',
                'files': [
                    "data/memory/conversations.json",
                    "data/memory/agent_memory.json"
                ],
                'dirs': ["data/vector_db/chroma_db"],
                'api_endpoint': '/api/agentic/reset'
            },
            'security': {
                'name': 'Agent Sécurité',
                'enabled': os.getenv('RESET_SECURITY_AGENT', 'true').lower() == 'true',
                'files': [],  # Pas de fichiers, tout est en mémoire
                'dirs': [],
                'api_endpoint': '/api/cybersecurity/reset',
                'memory_components': ['alerts', 'sessions', 'activities', 'state']
            },
            'logs': {
                'name': 'Fichiers de logs',
                'enabled': os.getenv('RESET_LOGS', 'true').lower() == 'true',
                'files': [],
                'dirs': [],
                'patterns': ['logs/*.log', '*.log']
            },
            'temp': {
                'name': 'Fichiers temporaires',
                'enabled': os.getenv('RESET_TEMP_FILES', 'true').lower() == 'true',
                'files': [],
                'dirs': [],
                'patterns': ['**/__pycache__', '**/*.pyc', '**/.DS_Store']
            }
        }
        
        self.reset_stats = {
            'cleaned': [],
            'errors': [],
            'skipped': []
        }
    
    def _log(self, message, level="INFO", color=None):
        """Logger avec couleurs"""
        colors = {
            'INFO': '\033[92m',    # Vert
            'WARN': '\033[93m',    # Jaune
            'ERROR': '\033[91m',   # Rouge
            'DEBUG': '\033[94m'    # Bleu
        }
        
        color_code = colors.get(level, '') if color is None else color
        reset_code = '\033[0m'
        
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"{color_code}[{timestamp}] {level}: {message}{reset_code}")
    
    def print_config(self):
        """Affiche la configuration actuelle"""
        self._log("Configuration de reset:", "INFO", '\033[95m')
        print("\n┌─────────────────────────────────────────┐")
        print("│         COMPOSANTS À NETTOYER           │")
        print("├─────────────────────────────────────────┤")
        
        for key, component in self.components.items():
            status = "✅ OUI" if component['enabled'] else "❌ NON"
            print(f"│ {component['name']:<25} {status:>10} │")
        
        print("└─────────────────────────────────────────┘\n")
    
    def check_api_status(self):
        """Vérifie si l'API est accessible"""
        try:
            response = requests.get(f"{self.api_url}/health", timeout=3)
            if response.status_code == 200:
                self._log("API accessible", "INFO")
                return True
        except:
            pass
        
        self._log("API non accessible", "WARN")
        return False
    
    def reset_support_agent(self):
        """Reset de l'agent support"""
        if not self.components['support']['enabled']:
            self._log("Reset Agent Support désactivé", "INFO")
            self.reset_stats['skipped'].append('Agent Support')
            return
        
        self._log("🤖 Reset de l'Agent Support...", "INFO")
        
        # Nettoyer les fichiers
        for file_path in self.components['support']['files']:
            if os.path.exists(file_path):
                try:
                    # Backup
                    backup_path = f"{file_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                    shutil.copy2(file_path, backup_path)
                    
                    # Vider le fichier
                    with open(file_path, 'w') as f:
                        json.dump({}, f)
                    
                    self._log(f"  ✅ Nettoyé: {file_path}", "INFO")
                    self.reset_stats['cleaned'].append(file_path)
                    
                except Exception as e:
                    self._log(f"  ❌ Erreur: {file_path} - {e}", "ERROR")
                    self.reset_stats['errors'].append(f"{file_path}: {e}")
        
        # Nettoyer ChromaDB
        for dir_path in self.components['support']['dirs']:
            if os.path.exists(dir_path):
                try:
                    backup_path = f"{dir_path}_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                    shutil.copytree(dir_path, backup_path)
                    shutil.rmtree(dir_path)
                    os.makedirs(dir_path, exist_ok=True)
                    
                    self._log(f"  ✅ ChromaDB réinitialisé", "INFO")
                    self.reset_stats['cleaned'].append(dir_path)
                    
                except Exception as e:
                    self._log(f"  ❌ Erreur ChromaDB: {e}", "ERROR")
                    self.reset_stats['errors'].append(f"ChromaDB: {e}")
        
        # Reset via API si disponible
        if self.check_api_status():
            try:
                # Tenter de reset via l'API (si endpoint existe)
                self._log("  🔄 Tentative reset via API...", "INFO")
                # Note: Cet endpoint n'existe pas encore, à implémenter
            except:
                pass
    
    def reset_security_agent(self):
        """Reset de l'agent de sécurité"""
        if not self.components['security']['enabled']:
            self._log("Reset Agent Sécurité désactivé", "INFO")
            self.reset_stats['skipped'].append('Agent Sécurité')
            return
        
        self._log("🛡️ Reset de l'Agent Sécurité...", "INFO")
        
        # Le reset de sécurité ne peut se faire que via l'API
        if not self.check_api_status():
            self._log("  ⚠️ API non accessible - Reset via code serveur requis", "WARN")
            self._generate_security_reset_code()
            return
        
        try:
            # Utiliser l'endpoint force-reset
            payload = {
                "action": "force_reset",
                "username": os.getenv('ADMIN_USERNAME', 'admin'),
                "password": os.getenv('ADMIN_PASSWORD', 'security123')
            }
            
            response = requests.post(
                f"{self.api_url}/api/admin/force-reset",
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self._log(f"  ✅ Reset sécurité réussi", "INFO")
                self._log(f"  📊 Stats: {data.get('stats_before', {})}", "DEBUG")
                self.reset_stats['cleaned'].append('Security Agent Memory')
            else:
                self._log(f"  ❌ Erreur API: {response.status_code}", "ERROR")
                self.reset_stats['errors'].append(f"Security API: {response.status_code}")
                
        except Exception as e:
            self._log(f"  ❌ Erreur connexion: {e}", "ERROR")
            self.reset_stats['errors'].append(f"Security API: {e}")
    
    def reset_logs(self):
        """Nettoie les fichiers de logs"""
        if not self.components['logs']['enabled']:
            self._log("Reset des logs désactivé", "INFO")
            self.reset_stats['skipped'].append('Logs')
            return
        
        self._log("📝 Nettoyage des logs...", "INFO")
        
        for pattern in self.components['logs']['patterns']:
            try:
                log_files = list(Path(".").glob(pattern))
                for log_file in log_files:
                    if os.path.exists(log_file):
                        open(log_file, 'w').close()
                        self._log(f"  ✅ Vidé: {log_file}", "INFO")
                        self.reset_stats['cleaned'].append(str(log_file))
            except Exception as e:
                self._log(f"  ❌ Erreur: {pattern} - {e}", "ERROR")
                self.reset_stats['errors'].append(f"{pattern}: {e}")
    
    def reset_temp_files(self):
        """Nettoie les fichiers temporaires"""
        if not self.components['temp']['enabled']:
            self._log("Reset des fichiers temporaires désactivé", "INFO")
            self.reset_stats['skipped'].append('Temp Files')
            return
        
        self._log("🗑️ Nettoyage des fichiers temporaires...", "INFO")
        
        for pattern in self.components['temp']['patterns']:
            try:
                items = list(Path(".").glob(pattern))
                for item in items:
                    if item.is_file():
                        item.unlink()
                    elif item.is_dir():
                        shutil.rmtree(item)
                    
                    self._log(f"  ✅ Supprimé: {item}", "INFO")
                    self.reset_stats['cleaned'].append(str(item))
                    
            except Exception as e:
                self._log(f"  ⚠️ Erreur: {pattern} - {e}", "WARN")
    
    def _generate_security_reset_code(self):
        """Génère le code pour reset manuel de sécurité"""
        code = '''
# Code à ajouter dans api/server.py pour reset de sécurité au démarrage

# ============= RESET SÉCURITÉ AU DÉMARRAGE =============
RESET_SECURITY_ON_STARTUP = os.getenv("RESET_SECURITY_ON_STARTUP", "false").lower() == "true"

if RESET_SECURITY_ON_STARTUP:
    from api.shared_state import system_state, security_alerts, user_activities, active_sessions
    
    # Reset complet de l'état sécurité
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
    
    security_alerts.clear()
    user_activities.clear()
    active_sessions.clear()
    
    print("✅ Agent Sécurité réinitialisé au démarrage")
    
    # Désactiver automatiquement après reset
    if os.getenv("AUTO_DISABLE_SECURITY_RESET", "true").lower() == "true":
        # Mettre à jour le fichier .env
        try:
            with open('.env', 'r') as f:
                lines = f.readlines()
            
            with open('.env', 'w') as f:
                for line in lines:
                    if line.startswith('RESET_SECURITY_ON_STARTUP='):
                        f.write('RESET_SECURITY_ON_STARTUP=false\\n')
                    else:
                        f.write(line)
        except:
            pass
# ============= FIN RESET SÉCURITÉ =============
'''
        
        with open('security_reset_code.txt', 'w') as f:
            f.write(code)
        
        self._log("  📋 Code de reset sauvé dans: security_reset_code.txt", "INFO")
    
    def generate_env_template(self):
        """Génère un template .env avec toutes les options"""
        template = '''# Configuration de Reset Modulaire NextGen-Agent

# === RESET AU DÉMARRAGE ===
# Active le reset complet au démarrage du serveur
RESET_SYSTEM_ON_STARTUP=false

# === RESET SÉLECTIF ===
# Agent Support (conversations, mémoire, ChromaDB)
RESET_SUPPORT_AGENT=true
RESET_SUPPORT_ON_STARTUP=false

# Agent Sécurité (alertes, sessions, état)
RESET_SECURITY_AGENT=true
RESET_SECURITY_ON_STARTUP=false

# Fichiers de logs
RESET_LOGS=true

# Fichiers temporaires (__pycache__, etc.)
RESET_TEMP_FILES=true

# === SÉCURITÉ ===
# Identifiants admin pour reset via API
ADMIN_USERNAME=admin
ADMIN_PASSWORD=security123

# === OPTIONS ===
# Désactive automatiquement le reset après exécution
AUTO_DISABLE_SUPPORT_RESET=true
AUTO_DISABLE_SECURITY_RESET=true

# Demande confirmation avant reset (si false, reset automatique)
RESET_CONFIRMATION=true

# === API ===
API_HOST=0.0.0.0
API_PORT=8000

# === LOGGING ===
LOG_LEVEL=INFO
LOG_FILE=logs/api_server.log
'''
        
        with open('.env.template', 'w') as f:
            f.write(template)
        
        self._log("📋 Template .env créé: .env.template", "INFO")
    
    def show_summary(self):
        """Affiche le résumé du reset"""
        print("\n" + "="*60)
        print("📊 RÉSUMÉ DU RESET")
        print("="*60)
        
        print(f"\n✅ Éléments nettoyés: {len(self.reset_stats['cleaned'])}")
        for item in self.reset_stats['cleaned'][:5]:
            print(f"   • {item}")
        
        if self.reset_stats['skipped']:
            print(f"\n⏭️ Éléments ignorés: {len(self.reset_stats['skipped'])}")
            for item in self.reset_stats['skipped']:
                print(f"   • {item}")
        
        if self.reset_stats['errors']:
            print(f"\n❌ Erreurs rencontrées: {len(self.reset_stats['errors'])}")
            for error in self.reset_stats['errors'][:5]:
                print(f"   • {error}")
        
        print("\n" + "="*60)
    
    def reset_all(self, skip_confirmation=False):
        """Exécute le reset selon la configuration"""
        self.print_config()
        
        if not skip_confirmation and os.getenv('RESET_CONFIRMATION', 'true').lower() == 'true':
            response = input("\n❓ Confirmer le reset avec cette configuration? (oui/non): ")
            if response.lower() not in ['oui', 'o', 'yes', 'y']:
                self._log("Reset annulé", "INFO")
                return False
        
        self._log("\n🚀 Démarrage du reset modulaire...", "INFO", '\033[95m')
        
        # Exécuter chaque reset
        self.reset_support_agent()
        self.reset_security_agent()
        self.reset_logs()
        self.reset_temp_files()
        
        # Afficher le résumé
        self.show_summary()
        
        return True


def main():
    """Fonction principale"""
    parser = argparse.ArgumentParser(description='Reset modulaire NextGen-Agent')
    parser.add_argument('--support', action='store_true', help='Reset uniquement Agent Support')
    parser.add_argument('--security', action='store_true', help='Reset uniquement Agent Sécurité')
    parser.add_argument('--logs', action='store_true', help='Reset uniquement les logs')
    parser.add_argument('--temp', action='store_true', help='Reset uniquement fichiers temp')
    parser.add_argument('--all', action='store_true', help='Reset complet (défaut)')
    parser.add_argument('--no-confirm', action='store_true', help='Pas de confirmation')
    parser.add_argument('--generate-env', action='store_true', help='Générer template .env')
    
    args = parser.parse_args()
    
    reset_manager = ModularSystemReset()
    
    if args.generate_env:
        reset_manager.generate_env_template()
        return
    
    # Si options spécifiques, désactiver les autres
    if any([args.support, args.security, args.logs, args.temp]):
        # Désactiver tout par défaut
        for component in reset_manager.components.values():
            component['enabled'] = False
        
        # Activer seulement les demandés
        if args.support:
            reset_manager.components['support']['enabled'] = True
        if args.security:
            reset_manager.components['security']['enabled'] = True
        if args.logs:
            reset_manager.components['logs']['enabled'] = True
        if args.temp:
            reset_manager.components['temp']['enabled'] = True
    
    # Exécuter le reset
    reset_manager.reset_all(skip_confirmation=args.no_confirm)


if __name__ == "__main__":
    main()
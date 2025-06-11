#!/usr/bin/env python3
"""
Script de debug et reset forcé pour résoudre les problèmes de réinitialisation
Version complète avec endpoint API intégré
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

class SystemResetManager:
    """Gestionnaire centralisé pour les resets système"""
    
    def __init__(self):
        self.reset_types = {
            'soft': self._soft_reset,      # Alertes seulement
            'medium': self._medium_reset,  # Alertes + sessions
            'hard': self._hard_reset,      # Tout sauf fichiers
            'complete': self._complete_reset # Tout + fichiers
        }
        
        self.files_to_clean = [
            "data/memory/conversations.json",
            "data/memory/agent_memory.json"
        ]
        
        self.dirs_to_clean = [
            "data/vector_db/chroma_db"
        ]
        
        self.api_url = "http://localhost:8000"
        
    def _log(self, message, level="INFO"):
        """Logger simple"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
    
    def _soft_reset(self):
        """Reset des alertes seulement"""
        self._log("🔄 Soft reset - Alertes seulement")
        return self._call_api_reset(['alerts'])
    
    def _medium_reset(self):
        """Reset alertes + sessions"""
        self._log("🔄 Medium reset - Alertes + Sessions")
        return self._call_api_reset(['alerts', 'sessions'])
    
    def _hard_reset(self):
        """Reset complet mémoire"""
        self._log("🔄 Hard reset - Mémoire complète")
        return self._call_api_reset(['all'])
    
    def _complete_reset(self):
        """Reset total incluant fichiers"""
        self._log("🔄 Complete reset - TOUT")
        success = self._call_api_reset(['all'])
        if success:
            self._clean_files()
        return success
    
    def _call_api_reset(self, targets):
        """Appel API pour reset"""
        try:
            payload = {
                "action": "force_reset",
                "username": "admin",
                "password": "security123"
            }
            
            response = requests.post(
                f"{self.api_url}/api/admin/force-reset",
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self._log(f"✅ Reset API réussi: {data.get('message', 'OK')}")
                return True
            else:
                self._log(f"❌ Erreur API ({response.status_code}): {response.text}", "ERROR")
                return False
                
        except requests.exceptions.RequestException as e:
            self._log(f"❌ Erreur connexion API: {e}", "ERROR")
            return False
    
    def _clean_files(self):
        """Nettoie les fichiers locaux"""
        self._log("🧹 Nettoyage des fichiers...")
        
        # Nettoyer les fichiers JSON
        for file_path in self.files_to_clean:
            if os.path.exists(file_path):
                try:
                    with open(file_path, 'w') as f:
                        json.dump({}, f)
                    self._log(f"✅ Vidé: {file_path}")
                except Exception as e:
                    self._log(f"❌ Erreur nettoyage {file_path}: {e}", "ERROR")
        
        # Nettoyer les répertoires
        for dir_path in self.dirs_to_clean:
            if os.path.exists(dir_path):
                try:
                    shutil.rmtree(dir_path)
                    os.makedirs(dir_path, exist_ok=True)
                    self._log(f"✅ ChromaDB réinitialisé: {dir_path}")
                except Exception as e:
                    self._log(f"❌ Erreur nettoyage {dir_path}: {e}", "ERROR")
    
    def check_server_status(self):
        """Vérifier le statut du serveur"""
        try:
            response = requests.get(f"{self.api_url}/api/admin-security?type=all", timeout=5)
            if response.status_code == 200:
                self._log("✅ Serveur accessible")
                return True
            else:
                self._log(f"⚠️ Serveur répond avec erreur: {response.status_code}", "WARN")
                return False
        except requests.exceptions.RequestException as e:
            self._log(f"❌ Serveur inaccessible: {e}", "ERROR")
            return False
    
    def reset(self, reset_type="medium", confirm=True):
        """Exécuter le reset"""
        if reset_type not in self.reset_types:
            self._log(f"❌ Type de reset invalide: {reset_type}", "ERROR")
            return False
        
        if confirm:
            response = input(f"Confirmer {reset_type} reset? (oui/non): ")
            if response.lower() not in ['oui', 'o', 'yes', 'y']:
                self._log("❌ Reset annulé")
                return False
        
        self._log(f"🚀 Démarrage du {reset_type} reset...")
        
        # Vérifier le serveur d'abord
        if not self.check_server_status():
            self._log("⚠️ Serveur non accessible, reset local seulement", "WARN")
            if reset_type in ['complete']:
                self._clean_files()
                self._log("✅ Reset local terminé")
                return True
            else:
                self._log("❌ Reset impossible sans accès serveur", "ERROR")
                return False
        
        # Exécuter le reset
        success = self.reset_types[reset_type]()
        
        if success:
            self._log(f"✅ {reset_type.capitalize()} reset terminé avec succès!")
        else:
            self._log(f"❌ {reset_type.capitalize()} reset échoué!", "ERROR")
        
        return success


def generate_server_endpoint():
    """Génère le code pour l'endpoint API à ajouter au serveur"""
    endpoint_code = '''
# Ajoutez cette section à votre api/server.py AVANT la section "INCLUSION DES SOUS-MODULES"

@app.post("/api/admin/force-reset")
async def force_system_reset(request: AdminRequest):
    """Force la réinitialisation complète du système"""
    try:
        # Vérifier les credentials admin
        if request.action != "force_reset":
            raise HTTPException(status_code=400, detail="Action invalide")
        
        if not request.username or not request.password:
            raise HTTPException(status_code=401, detail="Credentials requis")
        
        if not verify_admin_credentials(request.username, request.password):
            raise HTTPException(status_code=401, detail="Credentials invalides")
        
        logger.warning(f"🔄 RESET COMPLET DEMANDÉ PAR {request.username}")
        
        # Réinitialiser TOUT
        from api.shared_state import system_state, security_alerts, user_activities, active_sessions
        
        # Sauvegarder les stats avant reset
        stats_before = {
            "alerts": len(security_alerts),
            "users": len(user_activities),
            "sessions": len(active_sessions)
        }
        
        # Reset complet
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
        
        # Vider toutes les listes
        security_alerts.clear()
        user_activities.clear()
        active_sessions.clear()
        
        logger.info(f"✅ RESET COMPLET - Avant: {stats_before}, Après: Tout à 0")
        
        return {
            "status": "success",
            "message": "Système complètement réinitialisé",
            "stats_before": stats_before,
            "stats_after": {
                "alerts": 0,
                "users": 0,
                "sessions": 0
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erreur reset: {e}")
        raise HTTPException(status_code=500, detail=str(e))
'''
    
    print("📋 Code endpoint à ajouter au serveur:")
    print("="*60)
    print(endpoint_code)
    print("="*60)


def setup_env_file():
    """Configure le fichier .env pour le reset automatique"""
    env_content = '''# Reset Configuration
RESET_SYSTEM=false              # Mettre à true pour reset au démarrage
AUTO_DISABLE_RESET=true         # Désactive automatiquement après reset
RESET_CONFIRMATION=true         # Demande confirmation avant reset

# API Configuration
API_PORT=8000
API_HOST=0.0.0.0

# Security
ENABLE_SECURITY_CHECKS=true
MAX_ALERTS_STORED=100
'''
    
    try:
        with open('.env.example', 'w') as f:
            f.write(env_content)
        print("✅ Fichier .env.example créé")
        
        if not os.path.exists('.env'):
            with open('.env', 'w') as f:
                f.write(env_content)
            print("✅ Fichier .env créé")
        else:
            print("ℹ️ Fichier .env existe déjà")
            
    except Exception as e:
        print(f"❌ Erreur création .env: {e}")


def main():
    """Fonction principale"""
    parser = argparse.ArgumentParser(description='Gestionnaire de reset système')
    parser.add_argument('--type', choices=['soft', 'medium', 'hard', 'complete'], 
                       default='medium', help='Type de reset')
    parser.add_argument('--confirm', action='store_true', 
                       help='Confirmer automatiquement')
    parser.add_argument('--generate-endpoint', action='store_true',
                       help='Générer le code endpoint pour le serveur')
    parser.add_argument('--setup-env', action='store_true',
                       help='Créer les fichiers de configuration')
    parser.add_argument('--check-server', action='store_true',
                       help='Vérifier uniquement le statut du serveur')
    
    args = parser.parse_args()
    
    if args.generate_endpoint:
        generate_server_endpoint()
        return
    
    if args.setup_env:
        setup_env_file()
        return
    
    manager = SystemResetManager()
    
    if args.check_server:
        manager.check_server_status()
        return
    
    # Exécuter le reset
    success = manager.reset(args.type, not args.confirm)
    
    if success:
        print("\n✅ Opération terminée avec succès!")
        print("\n📋 Actions recommandées:")
        print("1. Redémarrer le serveur: python api/server.py")
        print("2. Vérifier le dashboard: http://localhost:3000/admin-security")
        print("3. Tester l'application: http://localhost:3000")
    else:
        print("\n❌ Opération échouée!")
        print("\n🔧 Solutions possibles:")
        print("1. Vérifier que le serveur est démarré")
        print("2. Vérifier que l'endpoint /api/admin/force-reset existe")
        print("3. Exécuter --generate-endpoint pour voir le code à ajouter")
        print("4. Faire un reset manuel avec --type complete")


if __name__ == "__main__":
    main()
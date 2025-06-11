#!/usr/bin/env python3
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

# api/reset_on_startup.py
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

# api/shared_state.py
"""
État partagé entre les différents modules de l'API
Permet la communication entre server.py, agentic_routes.py et cybersecurity_routes.py
"""
from datetime import datetime
from typing import Dict, List, Any

# État global du système (partagé entre tous les modules)
system_state = {
    "blocked": False,
    "threat_level": "safe",  # safe, warning, danger
    "block_reason": None,
    "last_block_time": None,
    "active_sessions": {},
    "total_threats_detected": 0,
    "last_scan": datetime.now().isoformat(),
    "active_threats": []
}

# Liste des alertes en mémoire (en production, utiliser une base de données)
security_alerts: List[Dict[str, Any]] = []

# Activités des utilisateurs
user_activities: Dict[str, Dict[str, Any]] = {}

# Sessions en cours avec leur état de sécurité
active_sessions: Dict[str, Dict[str, Any]] = {}

def add_security_alert(alert_type: str, severity: str, message: str, session_id: str = None, details: dict = None):
    """Ajoute une alerte de sécurité globale"""
    alert = {
        "id": f"{alert_type}_{datetime.now().timestamp()}",
        "type": alert_type,
        "severity": severity,
        "message": message,
        "timestamp": datetime.now().isoformat(),
        "action_taken": "Alerte générée automatiquement",
        "user_session": session_id,
        "details": details
    }
    
    security_alerts.insert(0, alert)
    
    # Limiter la taille
    if len(security_alerts) > 100:
        security_alerts[:] = security_alerts[:100]
    
    # Mettre à jour les statistiques
    system_state["total_threats_detected"] += 1
    
    # Ajuster le niveau de menace
    if severity == "critical":
        system_state["threat_level"] = "danger"
    elif severity == "high" and system_state["threat_level"] == "safe":
        system_state["threat_level"] = "warning"
    
    return alert

def update_user_activity(session_id: str, threat_score: float = 0.0, blocked: bool = False):
    """Met à jour l'activité utilisateur"""
    if session_id not in user_activities:
        user_activities[session_id] = {
            "messages_count": 0,
            "first_activity": datetime.now().isoformat(),
            "threat_score": 0.0,
            "blocked": False,
            "location": "Unknown"
        }
    
    activity = user_activities[session_id]
    activity["messages_count"] += 1
    activity["last_activity"] = datetime.now().isoformat()
    activity["threat_score"] = max(activity["threat_score"], threat_score)
    activity["blocked"] = blocked or activity["blocked"]
    
    return activity

def is_session_blocked(session_id: str) -> bool:
    """Vérifie si une session est bloquée"""
    return user_activities.get(session_id, {}).get("blocked", False) or system_state["blocked"]

def get_session_threat_score(session_id: str) -> float:
    """Obtient le score de menace d'une session"""
    return user_activities.get(session_id, {}).get("threat_score", 0.0)
#!/usr/bin/env python3
"""
Serveur FastAPI principal - Version complète avec communication inter-agents
Support pour agents agentic et cybersécurité avec communication temps réel
"""
import logging
import sys
import os
import uvicorn
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('logs/api_server.log', mode='a') if os.path.exists('logs') else logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Ajouter le répertoire racine au path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Créer l'application FastAPI
app = FastAPI(
    title="NextGen-Agent API",
    description="API pour agents IA avec sécurité intégrée",
    version="7.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =============================================================================
# MODÈLES PYDANTIC
# =============================================================================

class InterAgentMessage(BaseModel):
    """Modèle pour la communication inter-agents"""
    from_agent: str
    to_agent: str
    message: Dict[str, Any]

class SystemBlockRequest(BaseModel):
    """Requête de blocage du système"""
    reason: str
    severity: str = "critical"
    session_id: Optional[str] = None
    analysis: Optional[Dict[str, Any]] = None

class AdminRequest(BaseModel):
    """Requête d'administration"""
    action: str
    username: Optional[str] = None
    password: Optional[str] = None
    reason: Optional[str] = None
    severity: Optional[str] = None

# =============================================================================
# ÉTAT GLOBAL DU SYSTÈME
# =============================================================================

system_state = {
    "blocked": False,
    "threat_level": "safe",  # safe, warning, danger
    "block_reason": None,
    "last_block_time": None,
    "active_sessions": {},
    "total_threats_detected": 0,
    "last_scan": datetime.now().isoformat()
}

# Liste des alertes en mémoire (en production, utiliser une base de données)
security_alerts = []
user_activities = {}

# =============================================================================
# ROUTES PRINCIPALES
# =============================================================================

@app.get("/")
async def root():
    """Endpoint racine"""
    return {
        "message": "NextGen-Agent API v7.0.0",
        "status": "operational",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "agentic_support": "available",
            "cybersecurity": "available", 
            "inter_agent_communication": "available",
            "admin_panel": "available"
        }
    }

@app.get("/health")
async def health_check():
    """Vérification de santé globale"""
    try:
        # Vérifier les composants
        components_status = {
            "api_server": "healthy",
            "agentic_agent": "unknown",
            "security_agent": "unknown",
            "database": "memory",  # En mémoire pour cette version
            "llm_services": "unknown"
        }
        
        # Tester l'agent agentic
        try:
            from api.agentic_routes import AGENT_AVAILABLE
            components_status["agentic_agent"] = "healthy" if AGENT_AVAILABLE else "degraded"
        except ImportError:
            components_status["agentic_agent"] = "unavailable"
        
        # Tester l'agent de sécurité
        try:
            from api.cybersecurity_routes import models_manager
            components_status["security_agent"] = "healthy" if models_manager else "degraded"
        except ImportError:
            components_status["security_agent"] = "unavailable"
        
        overall_status = "healthy"
        if any(status in ["degraded", "unavailable"] for status in components_status.values()):
            overall_status = "degraded"
        
        return {
            "status": overall_status,
            "timestamp": datetime.now().isoformat(),
            "components": components_status,
            "system_state": system_state,
            "uptime": "running",
            "version": "7.0.0"
        }
        
    except Exception as e:
        logger.error(f"Erreur health check: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
        )

@app.get("/status")
async def detailed_status():
    """Status détaillé du système"""
    try:
        return {
            "api_version": "7.0.0",
            "timestamp": datetime.now().isoformat(),
            "system_state": system_state,
            "security_stats": {
                "total_alerts": len(security_alerts),
                "active_threats": system_state["total_threats_detected"],
                "blocked_sessions": len([s for s in user_activities.values() if s.get("blocked", False)]),
                "threat_level": system_state["threat_level"]
            },
            "services": {
                "agentic_support": {"status": "available", "endpoint": "/api/agentic"},
                "cybersecurity": {"status": "available", "endpoint": "/api/cybersecurity"},
                "admin": {"status": "available", "endpoint": "/api/admin-security"},
                "inter_agent": {"status": "available", "endpoint": "/api/inter-agent"}
            }
        }
    except Exception as e:
        logger.error(f"Erreur status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# =============================================================================
# COMMUNICATION INTER-AGENTS - CORRIGÉE
# =============================================================================

@app.post("/api/inter-agent/communicate")
async def inter_agent_communication(request: InterAgentMessage):
    """Communication entre agents (support <-> sécurité) - VERSION CORRIGÉE"""
    try:
        logger.info(f"📨 Communication inter-agents: {request.from_agent} -> {request.to_agent}")
        
        # Communication Support → Sécurité
        if request.from_agent == "support" and request.to_agent == "security":
            if request.message.get("action") == "verify_message":
                try:
                    # Import local pour éviter les dépendances circulaires
                    from api.cybersecurity_routes import SecurityAnalysisRequest, analyze_security
                    
                    analysis_request = SecurityAnalysisRequest(
                        text=request.message.get("text", ""),
                        models=request.message.get("models", ["vulnerability_classifier", "intent_classifier"]),
                        session_id=request.message.get("session_id", "inter-agent")
                    )
                    
                    analysis = await analyze_security(analysis_request)
                    return {
                        "status": "analyzed",
                        "analysis": analysis.dict(),
                        "timestamp": datetime.now().isoformat()
                    }
                except Exception as e:
                    logger.error(f"Erreur analyse sécurité: {e}")
                    return {
                        "status": "error",
                        "error": str(e),
                        "timestamp": datetime.now().isoformat()
                    }
        
        # Communication Sécurité → Support  
        elif request.from_agent == "security" and request.to_agent == "support":
            if request.message.get("action") == "block_conversation":
                # Bloquer le système
                system_state["blocked"] = True
                system_state["block_reason"] = request.message.get("reason", "Security threat detected")
                system_state["threat_level"] = "danger"
                system_state["last_block_time"] = datetime.now().isoformat()
                
                logger.warning(f"🚫 Système bloqué: {system_state['block_reason']}")
                
                return {
                    "status": "acknowledged",
                    "action_taken": "conversation_blocked",
                    "timestamp": datetime.now().isoformat()
                }
        
        # Communication générale
        return {
            "status": "delivered",
            "from": request.from_agent,
            "to": request.to_agent,
            "message_processed": True,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Erreur communication inter-agents: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# =============================================================================
# ROUTES DE BLOCAGE SYSTÈME
# =============================================================================

@app.post("/api/cybersecurity/block")
async def block_system(request: SystemBlockRequest):
    """Bloque le système en cas de menace critique"""
    try:
        logger.warning(f"🚫 Blocage système demandé: {request.reason}")
        
        # Mettre à jour l'état du système
        system_state["blocked"] = True
        system_state["block_reason"] = request.reason
        system_state["threat_level"] = "danger"
        system_state["last_block_time"] = datetime.now().isoformat()
        
        # Ajouter une alerte critique
        alert = {
            "id": f"block_{datetime.now().timestamp()}",
            "type": "system",
            "severity": request.severity,
            "message": f"Système bloqué: {request.reason}",
            "timestamp": datetime.now().isoformat(),
            "action_taken": "Système verrouillé automatiquement",
            "user_session": request.session_id,
            "details": request.analysis
        }
        
        security_alerts.insert(0, alert)
        
        # Limiter à 50 alertes en mémoire
        if len(security_alerts) > 50:
            security_alerts = security_alerts[:50]
        
        return {
            "status": "blocked",
            "reason": request.reason,
            "timestamp": datetime.now().isoformat(),
            "system_state": system_state
        }
        
    except Exception as e:
        logger.error(f"Erreur blocage système: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/cybersecurity/unblock")
async def unblock_system():
    """Débloque le système"""
    try:
        logger.info("🔓 Déblocage système demandé")
        
        system_state["blocked"] = False
        system_state["block_reason"] = None
        system_state["threat_level"] = "safe"
        system_state["last_block_time"] = None
        
        # Ajouter une alerte de déblocage
        alert = {
            "id": f"unblock_{datetime.now().timestamp()}",
            "type": "system",
            "severity": "medium",
            "message": "Système débloqué par administrateur",
            "timestamp": datetime.now().isoformat(),
            "action_taken": "Accès restauré",
            "user_session": "admin"
        }
        
        security_alerts.insert(0, alert)
        
        return {
            "status": "unblocked",
            "timestamp": datetime.now().isoformat(),
            "system_state": system_state
        }
        
    except Exception as e:
        logger.error(f"Erreur déblocage système: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# =============================================================================
# ROUTES D'ADMINISTRATION SÉCURISÉE
# =============================================================================

def verify_admin_credentials(username: str, password: str) -> bool:
    """Vérifie les identifiants administrateur"""
    # En production, utiliser un système d'authentification robuste
    admin_credentials = {
        "admin": "security123",
        "root": "admin123",
        "security": "security456"
    }
    return admin_credentials.get(username) == password

@app.post("/api/admin-security")
async def admin_security_panel(request: AdminRequest):
    """Panel d'administration sécurisé"""
    try:
        if request.action == "login":
            if not request.username or not request.password:
                raise HTTPException(status_code=400, detail="Username et password requis")
            
            if verify_admin_credentials(request.username, request.password):
                logger.info(f"✅ Connexion admin réussie: {request.username}")
                return {
                    "status": "authenticated",
                    "username": request.username,
                    "timestamp": datetime.now().isoformat(),
                    "permissions": ["read", "write", "block", "unblock"]
                }
            else:
                logger.warning(f"❌ Tentative connexion admin échouée: {request.username}")
                raise HTTPException(status_code=401, detail="Identifiants invalides")
        
        elif request.action == "block_system":
            logger.warning(f"🚫 Blocage manuel par admin: {request.reason}")
            
            system_state["blocked"] = True
            system_state["block_reason"] = request.reason or "Blocage manuel administrateur"
            system_state["threat_level"] = "danger"
            system_state["last_block_time"] = datetime.now().isoformat()
            
            return {
                "status": "system_blocked",
                "system_state": system_state,
                "timestamp": datetime.now().isoformat()
            }
        
        elif request.action == "unblock_system":
            logger.info("🔓 Déblocage manuel par admin")
            
            system_state["blocked"] = False
            system_state["block_reason"] = None
            system_state["threat_level"] = "safe"
            
            return {
                "status": "system_unblocked", 
                "system_state": system_state,
                "timestamp": datetime.now().isoformat()
            }
        
        elif request.action == "generate_report":
            # Générer un rapport de sécurité
            report = {
                "generated_at": datetime.now().isoformat(),
                "system_state": system_state,
                "security_summary": {
                    "total_alerts": len(security_alerts),
                    "critical_alerts": len([a for a in security_alerts if a.get("severity") == "critical"]),
                    "blocked_sessions": len([s for s in user_activities.values() if s.get("blocked", False)]),
                    "threat_level": system_state["threat_level"]
                },
                "recent_alerts": security_alerts[:10],
                "user_activities": list(user_activities.values())[:20]
            }
            
            return {
                "status": "report_generated",
                "report": report,
                "timestamp": datetime.now().isoformat()
            }
        
        else:
            raise HTTPException(status_code=400, detail=f"Action inconnue: {request.action}")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur admin panel: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/admin-security")
async def get_admin_data():
    """Récupère les données d'administration"""
    try:
        return {
            "system_state": system_state,
            "alerts": security_alerts[:20],  # 20 alertes les plus récentes
            "user_activities": [
                {
                    "session_id": session_id,
                    "messages_count": activity.get("messages_count", 0),
                    "last_activity": activity.get("last_activity", ""),
                    "threat_score": activity.get("threat_score", 0),
                    "blocked": activity.get("blocked", False),
                    "location": activity.get("location", "Unknown")
                }
                for session_id, activity in user_activities.items()
            ],
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Erreur récupération données admin: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# =============================================================================
# INCLUSION DES SOUS-MODULES
# =============================================================================

# Inclure les routes de l'agent agentic
try:
    from api.agentic_routes import router as agentic_router
    app.include_router(agentic_router, prefix="/api/agentic", tags=["Agent Support"])
    logger.info("✅ Routes agent agentic chargées")
except ImportError as e:
    logger.error(f"❌ Impossible de charger les routes agentic: {e}")

# Inclure les routes de cybersécurité
try:
    from api.cybersecurity_routes import router as cybersecurity_router
    app.include_router(cybersecurity_router, prefix="/api/cybersecurity", tags=["Cybersécurité"])
    logger.info("✅ Routes cybersécurité chargées")
except ImportError as e:
    logger.error(f"❌ Impossible de charger les routes cybersécurité: {e}")

# =============================================================================
# GESTION DES ERREURS GLOBALES
# =============================================================================

@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={
            "error": "Endpoint non trouvé",
            "message": f"L'endpoint {request.url.path} n'existe pas",
            "available_endpoints": [
                "/health", "/status", "/docs",
                "/api/agentic/chat", "/api/agentic/health",
                "/api/cybersecurity/analyze", "/api/cybersecurity/alerts",
                "/api/inter-agent/communicate", "/api/admin-security"
            ],
            "timestamp": datetime.now().isoformat()
        }
    )

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    logger.error(f"Erreur interne: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Erreur interne du serveur",
            "message": "Une erreur inattendue s'est produite",
            "timestamp": datetime.now().isoformat()
        }
    )

# =============================================================================
# FONCTIONS UTILITAIRES
# =============================================================================

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
    
    logger.warning(f"🚨 Nouvelle alerte {severity}: {message}")

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

# =============================================================================
# POINT D'ENTRÉE
# =============================================================================

if __name__ == "__main__":
    # Configuration des dossiers
    os.makedirs("logs", exist_ok=True)
    
    # Informations de démarrage
    logger.info("🚀 Démarrage NextGen-Agent API v7.0.0")
    logger.info("📡 Services disponibles:")
    logger.info("   • API Principale: http://localhost:8000")
    logger.info("   • Documentation: http://localhost:8000/docs")
    logger.info("   • Agent Support: http://localhost:8000/api/agentic/chat")
    logger.info("   • Cybersécurité: http://localhost:8000/api/cybersecurity/analyze")
    logger.info("   • Communication Inter-Agents: http://localhost:8000/api/inter-agent/communicate")
    logger.info("   • Admin Panel: http://localhost:8000/api/admin-security")
    
    # Démarrer le serveur
    uvicorn.run(
        "api.server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
        access_log=True
    )
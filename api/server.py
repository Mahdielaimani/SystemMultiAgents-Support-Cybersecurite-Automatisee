#!/usr/bin/env python3
"""
Serveur FastAPI principal - Version avec Reset Modulaire
Support pour reset sélectif des agents via variables d'environnement
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
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

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

# ============= DÉBUT SYSTÈME DE RESET MODULAIRE =============

def should_reset(component: str) -> bool:
    """Vérifie si un composant doit être réinitialisé"""
    env_var = f"RESET_{component.upper()}_ON_STARTUP"
    return os.getenv(env_var, "false").lower() == "true"

def disable_reset_in_env(component: str):
    """Désactive le reset dans le fichier .env"""
    if os.getenv(f"AUTO_DISABLE_{component.upper()}_RESET", "true").lower() != "true":
        return
    
    try:
        env_path = '.env'
        if not os.path.exists(env_path):
            return
        
        with open(env_path, 'r') as f:
            lines = f.readlines()
        
        env_var = f"RESET_{component.upper()}_ON_STARTUP"
        with open(env_path, 'w') as f:
            for line in lines:
                if line.strip().startswith(f'{env_var}='):
                    f.write(f'{env_var}=false\n')
                    logger.info(f"✅ Auto-désactivation du reset {component}")
                else:
                    f.write(line)
    except Exception as e:
        logger.error(f"Erreur désactivation reset {component}: {e}")

# Reset global du système (tous les composants)
RESET_SYSTEM = should_reset("SYSTEM")

if RESET_SYSTEM:
    print("\n" + "="*70)
    print("🔄 RÉINITIALISATION COMPLÈTE DU SYSTÈME AU DÉMARRAGE")
    print("="*70 + "\n")
    
    # Supprimer TOUS les modules en cache
    modules_to_reset = [
        'api.shared_state',
        'api.cybersecurity_routes',
        'api.agentic_routes',
        'agents.agentic_agent',
        'agents.cybersecurity_agent'
    ]
    
    for module in modules_to_reset:
        if module in sys.modules:
            del sys.modules[module]
    
    print("✅ Tous les modules réinitialisés")

# Importer shared_state APRÈS le reset système si nécessaire
from api.shared_state import system_state, security_alerts, user_activities, active_sessions

# ============= RESET SÉLECTIF PAR COMPOSANT =============

# 1. Reset de l'Agent de Sécurité
if should_reset("SECURITY"):
    logger.warning("🛡️ RESET DE L'AGENT DE SÉCURITÉ AU DÉMARRAGE")
    
    # Réinitialiser l'état de sécurité
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
    
    # Vider les collections de sécurité
    security_alerts.clear()
    user_activities.clear()
    active_sessions.clear()
    
    logger.info(f"✅ Agent Sécurité réinitialisé - Alertes: 0, Sessions: 0")
    
    # Auto-désactiver après reset
    disable_reset_in_env("SECURITY")

# 2. Reset de l'Agent Support (si module disponible)
if should_reset("SUPPORT"):
    logger.warning("🤖 RESET DE L'AGENT SUPPORT AU DÉMARRAGE")
    
    try:
        # Vider les fichiers de mémoire
        import json
        
        memory_files = [
            "data/memory/conversations.json",
            "data/memory/agent_memory.json"
        ]
        
        for file_path in memory_files:
            if os.path.exists(file_path):
                with open(file_path, 'w') as f:
                    json.dump({}, f)
                logger.info(f"✅ Vidé: {file_path}")
        
        # Nettoyer ChromaDB si existe
        import shutil
        chroma_path = "data/vector_db/chroma_db"
        if os.path.exists(chroma_path):
            shutil.rmtree(chroma_path)
            os.makedirs(chroma_path, exist_ok=True)
            logger.info("✅ ChromaDB réinitialisé")
        
        # Auto-désactiver après reset
        disable_reset_in_env("SUPPORT")
        
    except Exception as e:
        logger.error(f"Erreur reset Agent Support: {e}")

# Reset complet système (override les individuels)
if RESET_SYSTEM:
    # Désactiver le reset système pour le prochain démarrage
    disable_reset_in_env("SYSTEM")

# ============= FIN SYSTÈME DE RESET MODULAIRE =============

# Créer l'application FastAPI
app = FastAPI(
    title="NextGen-Agent API",
    description="API pour agents IA avec sécurité intégrée et reset modulaire",
    version="7.1.0",
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
    component: Optional[str] = None  # Pour reset sélectif

class ResetRequest(BaseModel):
    """Requête de reset modulaire"""
    components: list[str]  # ['support', 'security', 'all']
    username: str
    password: str
    backup: bool = True

# =============================================================================
# ROUTES PRINCIPALES
# =============================================================================

@app.get("/")
async def root():
    """Endpoint racine avec info de reset"""
    reset_info = {
        "last_system_reset": os.getenv("LAST_SYSTEM_RESET", "never"),
        "last_security_reset": os.getenv("LAST_SECURITY_RESET", "never"),
        "last_support_reset": os.getenv("LAST_SUPPORT_RESET", "never")
    }
    
    return {
        "message": "NextGen-Agent API v7.1.0",
        "status": "operational",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "agentic_support": "available",
            "cybersecurity": "available", 
            "inter_agent_communication": "available",
            "admin_panel": "available"
        },
        "reset_info": reset_info
    }

@app.get("/health")
async def health_check():
    """Vérification de santé globale avec statut reset"""
    try:
        # Vérifier les composants
        components_status = {
            "api_server": "healthy",
            "agentic_agent": "unknown",
            "security_agent": "unknown",
            "database": "memory",
            "llm_services": "unknown"
        }
        
        # Statut des resets
        reset_status = {
            "support_reset_pending": should_reset("SUPPORT"),
            "security_reset_pending": should_reset("SECURITY"),
            "system_reset_pending": should_reset("SYSTEM")
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
            "reset_status": reset_status,
            "system_state": system_state,
            "uptime": "running",
            "version": "7.1.0"
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

# =============================================================================
# NOUVELLES ROUTES DE RESET MODULAIRE
# =============================================================================

@app.post("/api/admin/modular-reset")
async def modular_reset(request: ResetRequest):
    """Reset modulaire des composants spécifiques"""
    try:
        # Vérifier les credentials
        if not verify_admin_credentials(request.username, request.password):
            raise HTTPException(status_code=401, detail="Credentials invalides")
        
        logger.warning(f"🔄 RESET MODULAIRE demandé par {request.username}: {request.components}")
        
        results = {
            "timestamp": datetime.now().isoformat(),
            "requested_components": request.components,
            "results": {}
        }
        
        # Reset de l'agent support
        if "support" in request.components or "all" in request.components:
            try:
                support_stats = await reset_support_agent(backup=request.backup)
                results["results"]["support"] = {
                    "status": "success",
                    "stats": support_stats
                }
            except Exception as e:
                results["results"]["support"] = {
                    "status": "error",
                    "error": str(e)
                }
        
        # Reset de l'agent sécurité
        if "security" in request.components or "all" in request.components:
            try:
                security_stats = reset_security_agent()
                results["results"]["security"] = {
                    "status": "success",
                    "stats": security_stats
                }
            except Exception as e:
                results["results"]["security"] = {
                    "status": "error",
                    "error": str(e)
                }
        
        # Reset des logs
        if "logs" in request.components or "all" in request.components:
            try:
                log_stats = reset_logs()
                results["results"]["logs"] = {
                    "status": "success",
                    "stats": log_stats
                }
            except Exception as e:
                results["results"]["logs"] = {
                    "status": "error",
                    "error": str(e)
                }
        
        return results
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur reset modulaire: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def reset_support_agent(backup: bool = True) -> dict:
    """Reset de l'agent support uniquement"""
    import json
    import shutil
    
    stats = {
        "files_cleaned": 0,
        "memory_cleared": False,
        "chromadb_reset": False
    }
    
    # Nettoyer les fichiers mémoire
    memory_files = [
        "data/memory/conversations.json",
        "data/memory/agent_memory.json"
    ]
    
    for file_path in memory_files:
        if os.path.exists(file_path):
            if backup:
                backup_path = f"{file_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                shutil.copy2(file_path, backup_path)
            
            with open(file_path, 'w') as f:
                json.dump({}, f)
            stats["files_cleaned"] += 1
    
    # Reset de la mémoire de l'agent si chargé
    try:
        from api.agentic_routes import agent
        if agent and hasattr(agent, 'memory_store'):
            agent.memory_store.clear()
            if hasattr(agent, '_save_memory'):
                agent._save_memory()
            stats["memory_cleared"] = True
    except:
        pass
    
    # Reset ChromaDB
    chroma_path = "data/vector_db/chroma_db"
    if os.path.exists(chroma_path):
        if backup:
            backup_path = f"{chroma_path}_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            shutil.copytree(chroma_path, backup_path)
        
        shutil.rmtree(chroma_path)
        os.makedirs(chroma_path, exist_ok=True)
        stats["chromadb_reset"] = True
    
    # Mettre à jour la date du dernier reset
    update_env_var("LAST_SUPPORT_RESET", datetime.now().isoformat())
    
    logger.info(f"✅ Agent Support reset - Stats: {stats}")
    return stats

def reset_security_agent() -> dict:
    """Reset de l'agent sécurité uniquement"""
    stats_before = {
        "alerts": len(security_alerts),
        "users": len(user_activities),
        "sessions": len(active_sessions),
        "threats": system_state.get("total_threats_detected", 0)
    }
    
    # Reset complet de l'état
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
    
    # Vider les collections
    security_alerts.clear()
    user_activities.clear()
    active_sessions.clear()
    
    # Mettre à jour la date du dernier reset
    update_env_var("LAST_SECURITY_RESET", datetime.now().isoformat())
    
    stats_after = {
        "alerts": 0,
        "users": 0,
        "sessions": 0,
        "threats": 0
    }
    
    logger.info(f"✅ Agent Sécurité reset - Avant: {stats_before}, Après: {stats_after}")
    
    return {
        "before": stats_before,
        "after": stats_after
    }

def reset_logs() -> dict:
    """Reset des fichiers de logs"""
    stats = {
        "files_cleared": 0,
        "total_size_cleared": 0
    }
    
    log_patterns = ["logs/*.log", "*.log"]
    
    for pattern in log_patterns:
        log_files = list(Path(".").glob(pattern))
        for log_file in log_files:
            if os.path.exists(log_file):
                # Obtenir la taille avant
                size = os.path.getsize(log_file)
                stats["total_size_cleared"] += size
                
                # Vider le fichier
                open(log_file, 'w').close()
                stats["files_cleared"] += 1
    
    logger.info(f"✅ Logs reset - Stats: {stats}")
    return stats

def update_env_var(key: str, value: str):
    """Met à jour une variable dans le fichier .env"""
    try:
        env_path = '.env'
        lines = []
        found = False
        
        if os.path.exists(env_path):
            with open(env_path, 'r') as f:
                lines = f.readlines()
        
        # Mettre à jour ou ajouter la variable
        with open(env_path, 'w') as f:
            for line in lines:
                if line.strip().startswith(f'{key}='):
                    f.write(f'{key}={value}\n')
                    found = True
                else:
                    f.write(line)
            
            if not found:
                f.write(f'\n{key}={value}\n')
                
    except Exception as e:
        logger.error(f"Erreur mise à jour .env: {e}")

# =============================================================================
# ROUTES EXISTANTES MODIFIÉES
# =============================================================================

@app.post("/api/admin/force-reset")
async def force_system_reset(request: AdminRequest):
    """Force la réinitialisation complète du système (compatibilité)"""
    try:
        # Rediriger vers le nouveau système modulaire
        reset_request = ResetRequest(
            components=["all"],
            username=request.username,
            password=request.password,
            backup=True
        )
        
        return await modular_reset(reset_request)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erreur reset: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/admin/reset-status")
async def get_reset_status():
    """Obtient le statut des resets"""
    try:
        return {
            "timestamp": datetime.now().isoformat(),
            "pending_resets": {
                "system": should_reset("SYSTEM"),
                "support": should_reset("SUPPORT"),
                "security": should_reset("SECURITY")
            },
            "last_resets": {
                "system": os.getenv("LAST_SYSTEM_RESET", "never"),
                "support": os.getenv("LAST_SUPPORT_RESET", "never"),
                "security": os.getenv("LAST_SECURITY_RESET", "never")
            },
            "current_state": {
                "security_alerts": len(security_alerts),
                "active_sessions": len(active_sessions),
                "system_blocked": system_state.get("blocked", False),
                "threat_level": system_state.get("threat_level", "safe")
            }
        }
    except Exception as e:
        logger.error(f"Erreur status reset: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# =============================================================================
# ROUTES EXISTANTES (INCHANGÉES)
# =============================================================================

@app.get("/status")
async def detailed_status():
    """Status détaillé du système"""
    try:
        return {
            "api_version": "7.1.0",
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

@app.post("/api/inter-agent/communicate")
async def inter_agent_communication(request: InterAgentMessage):
    """Communication entre agents (support <-> sécurité)"""
    try:
        logger.info(f"📨 Communication inter-agents: {request.from_agent} -> {request.to_agent}")
        
        # Communication Support → Sécurité
        if request.from_agent == "support" and request.to_agent == "security":
            if request.message.get("action") == "verify_message":
                try:
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

@app.post("/api/cybersecurity/block")
async def block_system(request: SystemBlockRequest):
    """Bloque le système en cas de menace critique"""
    try:
        logger.warning(f"🚫 Blocage système demandé: {request.reason}")
        
        system_state["blocked"] = True
        system_state["block_reason"] = request.reason
        system_state["threat_level"] = "danger"
        system_state["last_block_time"] = datetime.now().isoformat()
        
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
        
        if len(security_alerts) > 50:
            security_alerts[:] = security_alerts[:50]
        
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

def verify_admin_credentials(username: str, password: str) -> bool:
    """Vérifie les identifiants administrateur"""
    admin_credentials = {
        "admin": os.getenv("ADMIN_PASSWORD", "security123"),
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
                    "permissions": ["read", "write", "block", "unblock", "reset"]
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
            "alerts": security_alerts[:20],
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
                "/api/inter-agent/communicate", "/api/admin-security",
                "/api/admin/force-reset", "/api/admin/modular-reset",
                "/api/admin/reset-status"
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
    
    if len(security_alerts) > 100:
        security_alerts[:] = security_alerts[:100]
    
    system_state["total_threats_detected"] += 1
    
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
    os.makedirs("logs", exist_ok=True)
    
    logger.info("🚀 Démarrage NextGen-Agent API v7.1.0 avec Reset Modulaire")
    logger.info("📡 Services disponibles:")
    logger.info("   • API Principale: http://localhost:8000")
    logger.info("   • Documentation: http://localhost:8000/docs")
    logger.info("   • Agent Support: http://localhost:8000/api/agentic/chat")
    logger.info("   • Cybersécurité: http://localhost:8000/api/cybersecurity/analyze")
    logger.info("   • Communication Inter-Agents: http://localhost:8000/api/inter-agent/communicate")
    logger.info("   • Admin Panel: http://localhost:8000/api/admin-security")
    logger.info("   • Reset Modulaire: http://localhost:8000/api/admin/modular-reset")
    logger.info("   • Status Reset: http://localhost:8000/api/admin/reset-status")
    
    uvicorn.run(
        "api.server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
        access_log=True
    )
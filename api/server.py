# api/server.py
"""
Serveur API principal pour NextGen-Agent avec NetworkX hybride et Cybersécurité
"""
import os
import sys
import logging
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

# Ajouter le répertoire racine au PYTHONPATH
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestionnaire de cycle de vie de l'application"""
    logger.info("🚀 Démarrage du serveur NextGen-Agent avec NetworkX hybride et Cybersécurité")
    yield
    logger.info("🛑 Arrêt du serveur NextGen-Agent")

# Création de l'application FastAPI
app = FastAPI(
    title="NextGen-Agent API",
    description="API pour les agents IA intelligents avec NetworkX RAG hybride et Cybersécurité",
    version="6.0.0",
    lifespan=lifespan
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import et inclusion des routes
try:
    from api.agentic_routes import router as agentic_router
    app.include_router(agentic_router, prefix="/api/agentic", tags=["agentic"])
    logger.info("✅ Routes agentic NetworkX chargées")
except ImportError as e:
    logger.warning(f"⚠️  Routes agentic non disponibles: {e}")

try:
    from api.guardian_routes import router as guardian_router
    app.include_router(guardian_router, prefix="/api/guardian", tags=["guardian"])
    logger.info("✅ Routes guardian chargées")
except ImportError as e:
    logger.warning(f"⚠️  Routes guardian non disponibles: {e}")

try:
    from api.cybersecurity_routes import router as cybersecurity_router
    app.include_router(cybersecurity_router, prefix="/api/cybersecurity", tags=["cybersecurity"])
    logger.info("✅ Routes cybersécurité chargées")
except ImportError as e:
    logger.warning(f"⚠️  Routes cybersécurité non disponibles: {e}")

# Routes de base
@app.get("/")
async def root():
    """Endpoint racine"""
    return {
        "message": "NextGen-Agent API v6.0",
        "status": "running",
        "agent_type": "NetworkX Hybrid RAG with Security",
        "features": [
            "Vector RAG (ChromaDB + BGE)",
            "Graph RAG (NetworkX)",
            "Conversational Memory",
            "Hybrid LLM (Gemini + Mistral)",
            "Real-time Graph Learning",
            "TeamSquare Knowledge Base",
            "AI Security Models (Vulnerability, Network, Intent)",
            "Real-time Threat Detection",
            "Automated Response System"
        ]
    }

@app.get("/health")
async def health_check():
    """Vérification de santé du serveur"""
    health_status = {
        "status": "healthy",
        "version": "6.0.0",
        "timestamp": "2025-06-07",
        "components": {}
    }
    
    # Vérifier l'agent support
    try:
        from agents.support_agent.agent import get_support_agent
        agent = get_support_agent()
        agent_health = agent.health_check()
        health_status["components"]["support_agent"] = {
            "status": agent_health.get("agent_status", "unknown"),
            "details": agent_health
        }
    except Exception as e:
        logger.error(f"❌ Erreur health check support agent: {e}")
        health_status["components"]["support_agent"] = {
            "status": "error",
            "error": str(e)
        }
    
    # Vérifier les modèles de sécurité
    try:
        from agents.cybersecurity_agent.custom_model_loaders import HuggingFaceSecurityModels
        security_models = HuggingFaceSecurityModels()
        models_info = security_models.get_model_info()
        health_status["components"]["security_models"] = {
            "status": "healthy",
            "models": models_info["models"]
        }
    except Exception as e:
        logger.error(f"❌ Erreur health check modèles sécurité: {e}")
        health_status["components"]["security_models"] = {
            "status": "error",
            "error": str(e)
        }
    
    # Déterminer le statut global
    if any(comp.get("status") == "error" for comp in health_status["components"].values()):
        health_status["status"] = "degraded"
    
    return health_status

@app.get("/api/status")
async def api_status():
    """Status détaillé de l'API"""
    try:
        status = {
            "api_version": "6.0.0",
            "endpoints": {
                "support": [
                    "/api/agentic/chat",
                    "/api/agentic/health",
                    "/api/agentic/status",
                    "/api/agentic/memory/{session_id}",
                    "/api/agentic/networkx/stats",
                    "/api/agentic/rag/stats"
                ],
                "security": [
                    "/api/cybersecurity/analyze",
                    "/api/cybersecurity/alerts",
                    "/api/cybersecurity/report",
                    "/api/cybersecurity/block",
                    "/api/cybersecurity/unblock",
                    "/api/cybersecurity/models/info",
                    "/api/cybersecurity/ws"
                ],
                "guardian": [
                    "/api/guardian/status",
                    "/api/guardian/realtime",
                    "/api/guardian/start",
                    "/api/guardian/stop",
                    "/api/guardian/vulnerabilities"
                ]
            },
            "features": {
                "networkx_graph": True,
                "vector_rag": True,
                "memory": True,
                "hybrid_llm": True,
                "security_models": True,
                "threat_detection": True,
                "real_time_monitoring": True
            }
        }
        
        # Ajouter les infos des agents si disponibles
        try:
            from agents.support_agent.agent import get_support_agent
            agent = get_support_agent()
            agent_info = agent.get_agent_info()
            status["agents"] = {
                "support": agent_info
            }
        except:
            pass
        
        try:
            from api.cybersecurity_routes import system_state, security_alerts
            status["security_state"] = {
                "system": system_state,
                "active_alerts": len(security_alerts)
            }
        except:
            pass
        
        return status
        
    except Exception as e:
        logger.error(f"❌ Erreur API status: {e}")
        return {
            "api_version": "6.0.0",
            "error": str(e),
            "status": "error"
        }

@app.get("/api/agents/info")
async def get_all_agents_info():
    """Informations sur tous les agents disponibles"""
    agents_info = {}
    
    # Agent support
    try:
        from agents.support_agent.agent import get_support_agent
        agent = get_support_agent()
        agents_info["support"] = {
            "status": "active",
            "info": agent.get_agent_info(),
            "health": agent.health_check()
        }
    except Exception as e:
        agents_info["support"] = {
            "status": "error",
            "error": str(e)
        }
    
    # Agent cybersécurité
    try:
        from agents.cybersecurity_agent.custom_model_loaders import HuggingFaceSecurityModels
        security_models = HuggingFaceSecurityModels()
        agents_info["security"] = {
            "status": "active",
            "models": security_models.get_model_info(),
            "capabilities": [
                "Vulnerability Detection",
                "Network Traffic Analysis",
                "Intent Classification",
                "Real-time Threat Detection",
                "Automated Response"
            ]
        }
    except Exception as e:
        agents_info["security"] = {
            "status": "error",
            "error": str(e)
        }
    
    # Robot gardien
    try:
        from agents.cybersecurity_agent.guardian_robot import guardian_robot
        agents_info["guardian"] = {
            "status": guardian_robot.get_status()["status"],
            "info": guardian_robot.get_status()
        }
    except Exception as e:
        agents_info["guardian"] = {
            "status": "error",
            "error": str(e)
        }
    
    return {
        "agents": agents_info,
        "total_agents": len(agents_info),
        "active_agents": sum(1 for a in agents_info.values() if a.get("status") == "active"),
        "timestamp": "2025-06-07T00:00:00Z"
    }

# Endpoint spécial pour la communication inter-agents
@app.post("/api/inter-agent/communicate")
async def inter_agent_communication(
    from_agent: str,
    to_agent: str,
    message: dict
):
    """Communication entre agents (support <-> sécurité)"""
    try:
        logger.info(f"📨 Communication inter-agents: {from_agent} -> {to_agent}")
        
        # Si l'agent sécurité envoie une alerte à l'agent support
        if from_agent == "security" and to_agent == "support":
            if message.get("action") == "block_conversation":
                # Implémenter la logique de blocage
                from api.cybersecurity_routes import system_state
                system_state["blocked"] = True
                system_state["block_reason"] = message.get("reason", "Security threat detected")
                
                return {
                    "status": "acknowledged",
                    "action_taken": "conversation_blocked",
                    "timestamp": "2025-06-07T00:00:00Z"
                }
        
        # Si l'agent support demande une vérification de sécurité
        elif from_agent == "support" and to_agent == "security":
            if message.get("action") == "verify_message":
                # Analyser le message
                from api.cybersecurity_routes import analyze_security, SecurityAnalysisRequest
                
                request = SecurityAnalysisRequest(
                    text=message.get("text", ""),
                    session_id=message.get("session_id", "inter-agent")
                )
                
                analysis = await analyze_security(request)
                return {
                    "status": "analyzed",
                    "analysis": analysis.dict(),
                    "timestamp": "2025-06-07T00:00:00Z"
                }
        
        return {
            "status": "delivered",
            "from": from_agent,
            "to": to_agent,
            "timestamp": "2025-06-07T00:00:00Z"
        }
        
    except Exception as e:
        logger.error(f"❌ Erreur communication inter-agents: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("API_PORT", "8000"))
    
    # Afficher un banner au démarrage
    print("""
    ╔══════════════════════════════════════════════════════════════════╗
    ║                    NEXTGEN-AGENT API SERVER                      ║
    ║                                                                  ║
    ║  🤖 Agents Support + 🛡️ Cybersécurité + 🔍 Guardian Robot        ║
    ║                                                                  ║
    ║  Features:                                                       ║
    ║  • NetworkX Hybrid RAG                                           ║
    ║  • Real-time Threat Detection                                    ║
    ║  • Multi-Agent Communication                                     ║
    ║  • AI Security Models (3 types)                                  ║
    ║                                                                  ║
    ║  Port: {:<57}║
    ╚══════════════════════════════════════════════════════════════════╝
    """.format(port))
    
    logger.info(f"🚀 Lancement du serveur NextGen-Agent avec Cybersécurité sur le port {port}")
    
    uvicorn.run(
        "api.server:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info"
    )
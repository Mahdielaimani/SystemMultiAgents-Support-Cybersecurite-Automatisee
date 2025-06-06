"""
Serveur API principal pour NextGen-Agent avec NetworkX hybride
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
    logger.info("🚀 Démarrage du serveur NextGen-Agent avec NetworkX hybride")
    yield
    logger.info("🛑 Arrêt du serveur NextGen-Agent")

# Création de l'application FastAPI
app = FastAPI(
    title="NextGen-Agent API",
    description="API pour les agents IA intelligents avec NetworkX RAG hybride",
    version="5.0.0",
    lifespan=lifespan
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
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

# Routes de base
@app.get("/")
async def root():
    """Endpoint racine"""
    return {
        "message": "NextGen-Agent API v5.0",
        "status": "running",
        "agent_type": "NetworkX Hybrid RAG",
        "features": [
            "Vector RAG (ChromaDB + BGE)",
            "Graph RAG (NetworkX)",
            "Conversational Memory",
            "Hybrid LLM (Gemini + Mistral)",
            "Real-time Graph Learning",
            "TeamSquare Knowledge Base"
        ]
    }

@app.get("/health")
async def health_check():
    """Vérification de santé du serveur"""
    try:
        # Tester l'agent principal
        from agents.support_agent.agent import get_support_agent
        agent = get_support_agent()
        agent_health = agent.health_check()
        
        return {
            "status": "healthy",
            "version": "5.0.0",
            "timestamp": "2025-06-02",
            "agent_status": agent_health.get("agent_status", "unknown"),
            "components": agent_health.get("components", {}),
            "graph_stats": agent_health.get("graph_stats", {}),
            "vector_stats": agent_health.get("vector_stats", {}),
            "memory_stats": agent_health.get("memory_stats", {})
        }
        
    except Exception as e:
        logger.error(f"❌ Erreur health check: {e}")
        return {
            "status": "degraded",
            "version": "5.0.0",
            "error": str(e)
        }

@app.get("/api/status")
async def api_status():
    """Status détaillé de l'API"""
    try:
        # Test de l'agent NetworkX
        from agents.support_agent.agent import get_support_agent
        agent = get_support_agent()
        agent_info = agent.get_agent_info()
        
        return {
            "api_version": "5.0.0",
            "agent_info": agent_info,
            "endpoints": [
                "/api/agentic/chat",
                "/api/agentic/health",
                "/api/agentic/status",
                "/api/agentic/memory/{session_id}",
                "/api/agentic/networkx/stats",
                "/api/agentic/rag/stats",
                "/api/guardian/scan"
            ],
            "features": {
                "networkx_graph": True,
                "vector_rag": True,
                "memory": True,
                "hybrid_llm": True
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Erreur API status: {e}")
        return {
            "api_version": "5.0.0",
            "error": str(e),
            "agent_status": "error"
        }

@app.get("/api/agent/info")
async def get_agent_info():
    """Informations détaillées sur l'agent"""
    try:
        from agents.support_agent.agent import get_support_agent
        agent = get_support_agent()
        
        info = agent.get_agent_info()
        health = agent.health_check()
        
        return {
            **info,
            "health": health,
            "timestamp": "2025-06-02T16:00:00Z"
        }
        
    except Exception as e:
        logger.error(f"❌ Erreur agent info: {e}")
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("API_PORT", "8000"))
    logger.info(f"🚀 Lancement du serveur NextGen-Agent NetworkX sur le port {port}")
    uvicorn.run(
        "api.server:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info"
    )

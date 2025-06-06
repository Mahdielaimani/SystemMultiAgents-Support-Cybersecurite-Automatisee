"""
Routes API pour l'agent agentic avec routage externe
"""
import logging
import sys
import os
from pathlib import Path
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any, AsyncGenerator
import json

# Ajouter le répertoire racine au path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Configuration du logging
logger = logging.getLogger(__name__)

# IMPORTANT: Création du router FastAPI
router = APIRouter()

# Import de l'agent avec routage externe
try:
    from agents.support_agent.agentic_support_agent_with_external_routing import AgenticSupportAgentWithExternalRouting
    agent = AgenticSupportAgentWithExternalRouting()
    AGENT_AVAILABLE = True
    logger.info("✅ Agent avec routage externe chargé avec succès")
except ImportError as e:
    logger.error(f"❌ Erreur import agent avec routage: {e}")
    # Fallback vers l'agent NetworkX si le routage échoue
    try:
        from agents.support_agent.agentic_support_agent_networkx import AgenticSupportAgentNetworkX
        agent = AgenticSupportAgentNetworkX()
        AGENT_AVAILABLE = True
        logger.warning("⚠️ Fallback vers agent NetworkX")
    except ImportError:
        agent = None
        AGENT_AVAILABLE = False
        logger.error("❌ Aucun agent disponible")

# Modèles Pydantic
class AgenticChatRequest(BaseModel):
    query: str
    session_id: Optional[str] = "default"

class AgenticChatResponse(BaseModel):
    content: str
    metadata: Dict[str, Any] = {}

async def stream_response(content: str) -> AsyncGenerator[str, None]:
    """Génère une réponse en streaming"""
    # Simuler le streaming en envoyant la réponse par chunks
    words = content.split()
    for i, word in enumerate(words):
        chunk = {
            "content": word + " ",
            "done": i == len(words) - 1
        }
        yield f"data: {json.dumps(chunk)}\n\n"
        # Petite pause pour simuler le streaming
        import asyncio
        await asyncio.sleep(0.05)
    
    # Signal de fin
    yield f"data: {json.dumps({'content': '', 'done': True})}\n\n"

@router.get("/health")
async def agentic_health():
    """Vérification de santé de l'agent avec routage"""
    return {
        "status": "healthy" if AGENT_AVAILABLE else "degraded",
        "agent": "agentic_with_external_routing" if AGENT_AVAILABLE else "none",
        "version": "7.0.0",
        "features": ["vector_rag", "networkx_graph", "memory", "external_routing", "streaming"] if AGENT_AVAILABLE else []
    }

@router.post("/chat")
async def agentic_chat(request: AgenticChatRequest):
    """Endpoint principal pour le chat avec routage externe"""
    try:
        if not AGENT_AVAILABLE or not agent:
            raise HTTPException(status_code=503, detail="Agent non disponible")
        
        logger.info(f"🔍 Requête reçue: {request.query[:50]}... (Session: {request.session_id})")
        
        # Traitement avec l'agent de routage
        response_content = agent.process_query(request.query, request.session_id)
        
        # Métadonnées enrichies
        metadata = {
            "source": "agentic_with_external_routing", 
            "session_id": request.session_id,
            "agent_version": "7.0.0"
        }
        
        # Informations LLM
        if hasattr(agent, 'llm_manager') and agent.llm_manager:
            metadata.update({
                "provider": agent.llm_manager.current_provider,
                "tokens_used_today": getattr(agent.llm_manager, 'tokens_used_today', 0),
                "model": "gemini-1.5-flash" if agent.llm_manager.current_provider == "gemini" else "mistral-7b"
            })
        
        # Score de confiance
        if hasattr(agent, 'last_confidence_score'):
            metadata["confidence_score"] = agent.last_confidence_score
        
        # Statistiques de routage externe
        if hasattr(agent, 'stats'):
            metadata.update({
                "external_offers": agent.stats.get('external_offers', 0),
                "external_searches": agent.stats.get('external_searches', 0),
                "pending_external_search": request.session_id in getattr(agent, 'pending_external_searches', {})
            })
        
        logger.info(f"✅ Réponse générée avec routage externe (Confiance: {metadata.get('confidence_score', 'N/A')})")
        
        return AgenticChatResponse(
            content=response_content,
            metadata=metadata
        )
        
    except Exception as e:
        logger.error(f"❌ Erreur chat avec routage: {e}")
        # Réponse de fallback en cas d'erreur
        fallback_response = f"""Bonjour ! Je suis l'assistant TeamSquare avec routage externe.

**Votre question :** {request.query}

Je rencontre actuellement un problème technique, mais je peux vous aider avec :
• Questions sur TeamSquare (prix, fonctionnalités)
• Recherche externe pour questions hors sujet
• Mémoire conversationnelle

Pouvez-vous reformuler votre question ?"""
        
        return AgenticChatResponse(
            content=fallback_response,
            metadata={"error": str(e), "fallback": True, "session_id": request.session_id}
        )

@router.post("/chat/stream")
async def agentic_chat_stream(request: AgenticChatRequest):
    """Endpoint de chat avec streaming"""
    try:
        if not AGENT_AVAILABLE or not agent:
            raise HTTPException(status_code=503, detail="Agent non disponible")
        
        logger.info(f"🔍 Requête streaming: {request.query[:50]}... (Session: {request.session_id})")
        
        # Traitement avec l'agent de routage
        response_content = agent.process_query(request.query, request.session_id)
        
        # Retourner la réponse en streaming
        return StreamingResponse(
            stream_response(response_content),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "*",
            }
        )
        
    except Exception as e:
        logger.error(f"❌ Erreur chat streaming: {e}")
        
        # Réponse d'erreur en streaming
        error_response = f"Désolé, je rencontre un problème technique avec votre question: {request.query}"
        return StreamingResponse(
            stream_response(error_response),
            media_type="text/event-stream"
        )

# Version simplifiée pour compatibilité avec votre code
@router.post("/chat/simple")
async def chat(prompt: str, session_id: str = "default"):
    """
    Chat simple avec l'agent (compatible avec votre code)
    """
    try:
        if not AGENT_AVAILABLE or not agent:
            raise HTTPException(status_code=503, detail="Agent non disponible")
        
        logger.info(f"🔍 Chat simple: {prompt[:50]}...")
        
        # Traitement avec l'agent
        response_content = agent.process_query(prompt, session_id)
        
        # Retourner en streaming
        return StreamingResponse(
            stream_response(response_content),
            media_type="text/event-stream"
        )
        
    except Exception as e:
        logger.error(f"❌ Erreur chat simple: {e}")
        error_response = f"Erreur: {str(e)}"
        return StreamingResponse(
            stream_response(error_response),
            media_type="text/event-stream"
        )

@router.get("/status")
async def agentic_status():
    """Status détaillé de l'agent avec routage"""
    try:
        if not AGENT_AVAILABLE or not agent:
            return {"error": "Agent non disponible", "agent_available": False}
        
        # Récupérer les statistiques de l'agent
        stats = agent.get_stats()
        
        return {
            "agent_available": True,
            "agent_type": "agentic_with_external_routing",
            "timestamp": "2025-06-03T02:50:00Z",
            "version": "7.0.0",
            "stats": stats,
            "features": {
                "vector_rag": stats["components"]["vectorstore"],
                "networkx_graph": stats["components"]["networkx"],
                "memory": stats["components"]["memory"],
                "external_routing": True,
                "streaming": True,
                "llm_hybrid": stats["components"]["llm_manager"]
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Erreur status: {e}")
        return {
            "error": str(e),
            "agent_available": False,
            "timestamp": "2025-06-03T02:50:00Z"
        }

@router.get("/external/pending")
async def get_pending_external_searches():
    """Liste des recherches externes en attente"""
    try:
        if not AGENT_AVAILABLE or not hasattr(agent, 'pending_external_searches'):
            return {"error": "Agent non disponible"}
        
        return {
            "pending_count": len(agent.pending_external_searches),
            "sessions": list(agent.pending_external_searches.keys())
        }
        
    except Exception as e:
        logger.error(f"❌ Erreur pending external: {e}")
        return {"error": str(e)}

@router.get("/stats")
async def get_agent_stats():
    """Statistiques complètes de l'agent"""
    try:
        if not AGENT_AVAILABLE or not hasattr(agent, 'get_stats'):
            return {"error": "Agent non disponible"}
        
        return agent.get_stats()
        
    except Exception as e:
        logger.error(f"❌ Erreur stats: {e}")
        return {"error": str(e)}

# Ajout de la méthode stream à l'agent si elle n'existe pas
if AGENT_AVAILABLE and agent and not hasattr(agent, 'stream'):
    async def stream_method(prompt: str, session_id: str = "default"):
        """Méthode stream pour compatibilité"""
        response_content = agent.process_query(prompt, session_id)
        async for chunk in stream_response(response_content):
            yield chunk
    
    # Ajouter la méthode à l'agent
    agent.stream = stream_method
    logger.info("✅ Méthode stream ajoutée à l'agent")

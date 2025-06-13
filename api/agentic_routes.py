# api/agentic_routes.py - VERSION CORRIGÉE AVEC DÉTECTION AMÉLIORÉE
"""
Routes API pour l'agent agentic avec analyse de sécurité automatique
"""
import logging
import sys
import os
import requests
from pathlib import Path
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any, AsyncGenerator
import json
import asyncio

# Ajouter le répertoire racine au path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Configuration du logging
logger = logging.getLogger(__name__)

# IMPORTANT: Création du router FastAPI
router = APIRouter()

# Import de l'état partagé
from api.shared_state import system_state, security_alerts, update_user_activity, is_session_blocked

# Import de l'agent avec routage externe
try:
    from agents.support_agent.agentic_support_agent_with_external_routing import AgenticSupportAgentWithExternalRouting
    agent = AgenticSupportAgentWithExternalRouting()
    AGENT_AVAILABLE = True
    logger.info("✅ Agent avec routage externe chargé avec succès")
except ImportError as e:
    logger.error(f"❌ Erreur import agent avec routage: {e}")

# Modèles Pydantic
class AgenticChatRequest(BaseModel):
    query: str
    session_id: Optional[str] = "default"

class AgenticChatResponse(BaseModel):
    content: str
    metadata: Dict[str, Any] = {}

# Listes de mots-clés dangereux pour détection fallback
DANGEROUS_KEYWORDS = {
    'sql_injection': ['sql injection', 'drop table', 'or 1=1', 'union select', 'delete from', '; drop', '--', '/*', '*/', 'exec(', 'execute('],
    'xss': ['<script', 'javascript:', 'onerror=', 'onload=', 'alert(', 'document.cookie', '<iframe', 'eval('],
    'command_injection': ['rm -rf', 'sudo', 'chmod 777', '/etc/passwd', 'nc -e', 'bash -i', '&&', '||', '|', ';'],
    'path_traversal': ['../..', '..\\', '%2e%2e', 'etc/passwd', 'windows/system32'],
    'ddos': ['ddos', 'dos attack', 'flood', 'botnet', 'amplification'],
    'exploit': ['exploit', 'vulnérabilité', 'vulnerability', 'buffer overflow', 'heap spray'],
    'malicious_intent': ['hack', 'pirater', 'craquer', 'breach', 'backdoor', 'trojan', 'malware', 'virus']
}

def detect_threats_by_keywords(query: str) -> Dict[str, Any]:
    """Détection de menaces par mots-clés comme fallback"""
    query_lower = query.lower()
    threats_found = []
    threat_types = []
    
    for threat_type, keywords in DANGEROUS_KEYWORDS.items():
        for keyword in keywords:
            if keyword in query_lower:
                threats_found.append(keyword)
                if threat_type not in threat_types:
                    threat_types.append(threat_type)
    
    if threats_found:
        # Déterminer le niveau de menace
        if len(threats_found) >= 3 or 'sql injection' in query_lower or 'drop table' in query_lower:
            threat_level = "critical"
        elif len(threats_found) >= 2:
            threat_level = "high"
        else:
            threat_level = "medium"
        
        return {
            "threat_detected": True,
            "threat_level": threat_level,
            "threats_found": threats_found,
            "threat_types": threat_types,
            "detection_method": "keyword_matching"
        }
    
    return {
        "threat_detected": False,
        "threat_level": "safe",
        "detection_method": "keyword_matching"
    }

async def analyze_message_security(query: str, session_id: str) -> Dict[str, Any]:
    """Analyse la sécurité d'un message automatiquement - VERSION AMÉLIORÉE"""
    try:
        # Appeler l'API de sécurité interne
        security_analysis = {
            "text": query,
            "models": ["vulnerability_classifier", "intent_classifier"],
            "session_id": session_id
        }
        
        # Utiliser l'import direct au lieu de requests pour éviter les problèmes de réseau
        from api.cybersecurity_routes import analyze_security, SecurityAnalysisRequest
        
        # Créer la requête
        request = SecurityAnalysisRequest(**security_analysis)
        
        # Analyser directement
        analysis_response = await analyze_security(request)
        analysis = analysis_response.dict()
        
        # Si l'analyse retourne "safe" mais qu'on détecte des mots-clés dangereux
        if analysis.get('overall_threat_level', 'safe') == 'safe':
            keyword_detection = detect_threats_by_keywords(query)
            
            if keyword_detection['threat_detected']:
                logger.warning(f"⚠️ Menace détectée par mots-clés: {keyword_detection['threats_found']}")
                
                # Mettre à jour l'analyse avec la détection par mots-clés
                analysis['overall_threat_level'] = keyword_detection['threat_level']
                analysis['keyword_detection'] = keyword_detection
                analysis['vulnerability_classifier'] = {
                    'vulnerability_type': keyword_detection['threat_types'][0].upper() if keyword_detection['threat_types'] else 'UNKNOWN',
                    'confidence': 0.9,
                    'detection_method': 'keyword_matching'
                }
                analysis['intent_classifier'] = {
                    'intent': 'Malicious',
                    'confidence': 0.85,
                    'detection_method': 'keyword_matching'
                }
        
        logger.info(f"🔍 Analyse sécurité finale: {analysis.get('overall_threat_level', 'unknown')}")
        return analysis
            
    except Exception as e:
        logger.error(f"❌ Erreur analyse sécurité: {e}")
        
        # En cas d'erreur, utiliser la détection par mots-clés
        keyword_detection = detect_threats_by_keywords(query)
        
        return {
            "overall_threat_level": keyword_detection['threat_level'],
            "error": str(e),
            "fallback_detection": keyword_detection,
            "vulnerability_classifier": {
                'vulnerability_type': keyword_detection['threat_types'][0].upper() if keyword_detection.get('threat_types') else 'SAFE',
                'confidence': 0.8
            },
            "intent_classifier": {
                'intent': 'Malicious' if keyword_detection['threat_detected'] else 'Neutral',
                'confidence': 0.8
            }
        }

async def check_and_block_if_needed(analysis: Dict[str, Any], session_id: str, query: str) -> bool:
    """Vérifie si le système doit être bloqué - VERSION AMÉLIORÉE"""
    try:
        threat_level = analysis.get('overall_threat_level', 'safe')
        
        # Critères de blocage
        should_block = False
        block_reason = ""
        
        # Bloquer si menace critique ou high
        if threat_level in ["critical", "high"]:
            should_block = True
            block_reason = f"Niveau de menace {threat_level} détecté"
        
        # Bloquer si intention malveillante avec haute confiance
        intent_result = analysis.get('intent_classifier', {})
        if (intent_result.get('intent') == 'Malicious' and 
            intent_result.get('confidence', 0) > 0.7):
            should_block = True
            block_reason = "Intention malveillante confirmée"
        
        # Bloquer si vulnérabilité détectée
        vuln_result = analysis.get('vulnerability_classifier', {})
        if (vuln_result.get('vulnerability_type') not in ['SAFE', 'error', None] and
            vuln_result.get('confidence', 0) > 0.6):
            should_block = True
            block_reason = f"Vulnérabilité détectée: {vuln_result.get('vulnerability_type')}"
        
        # Bloquer si détection par mots-clés
        if analysis.get('keyword_detection', {}).get('threat_detected'):
            should_block = True
            threats = analysis['keyword_detection']['threats_found']
            block_reason = f"Contenu malveillant détecté: {', '.join(threats[:3])}"
        
        if should_block:
            logger.warning(f"🚫 Blocage système initié: {block_reason}")
            
            # Mettre à jour l'état du système directement
            system_state["blocked"] = True
            system_state["block_reason"] = block_reason
            system_state["threat_level"] = "danger"
            system_state["last_block_time"] = analysis.get("timestamp", datetime.now().isoformat())
            
            # Mettre à jour l'activité utilisateur
            update_user_activity(session_id, threat_score=1.0, blocked=True)
            
            # Ajouter une alerte avec plus de détails
            from api.shared_state import add_security_alert
            add_security_alert(
                alert_type="system",
                severity="critical" if threat_level == "critical" else "high",
                message=f"Session bloquée: {block_reason} | Query: {query[:100]}...",
                session_id=session_id,
                details={
                    "analysis": analysis,
                    "query": query,
                    "threat_level": threat_level,
                    "block_reason": block_reason
                }
            )
            
            logger.info("✅ Système bloqué avec succès et alerte créée")
        
        return should_block
        
    except Exception as e:
        logger.error(f"❌ Erreur vérification blocage: {e}")
        return False

async def stream_response(content: str) -> AsyncGenerator[str, None]:
    """Génère une réponse en streaming"""
    words = content.split()
    for i, word in enumerate(words):
        chunk = {
            "content": word + " ",
            "done": i == len(words) - 1
        }
        yield f"data: {json.dumps(chunk)}\n\n"
        await asyncio.sleep(0.05)
    
    yield f"data: {json.dumps({'content': '', 'done': True})}\n\n"

@router.get("/health")
async def agentic_health():
    """Vérification de santé de l'agent avec routage"""
    return {
        "status": "healthy" if AGENT_AVAILABLE else "degraded",
        "agent": "agentic_with_external_routing" if AGENT_AVAILABLE else "none",
        "version": "7.0.2",
        "features": ["vector_rag", "networkx_graph", "memory", "external_routing", "streaming", "auto_security_analysis", "keyword_detection"] if AGENT_AVAILABLE else [],
        "security_enabled": True
    }

@router.post("/chat")
async def agentic_chat(request: AgenticChatRequest):
    """Endpoint principal pour le chat avec analyse de sécurité automatique - VERSION AMÉLIORÉE"""
    try:
        if not AGENT_AVAILABLE or not agent:
            raise HTTPException(status_code=503, detail="Agent non disponible")
        
        logger.info(f"🔍 Requête reçue: {request.query[:50]}... (Session: {request.session_id})")
        
        # Vérifier si la session est déjà bloquée
        if is_session_blocked(request.session_id):
            logger.warning(f"🚫 Session déjà bloquée: {request.session_id}")
            return AgenticChatResponse(
                content="""🚫 **Accès Refusé**

Votre session a été suspendue pour des raisons de sécurité. 

Si vous pensez qu'il s'agit d'une erreur, veuillez contacter notre support.""",
                metadata={
                    "source": "security_block",
                    "blocked": True,
                    "session_blocked": True,
                    "session_id": request.session_id
                }
            )
        
        # 1. ANALYSE DE SÉCURITÉ AUTOMATIQUE AMÉLIORÉE
        security_analysis = await analyze_message_security(request.query, request.session_id)
        
        # 2. VÉRIFIER SI BLOCAGE NÉCESSAIRE (avec la query pour plus de contexte)
        system_blocked = await check_and_block_if_needed(security_analysis, request.session_id, request.query)
        
        # 3. GÉNÉRER RÉPONSE ADAPTÉE
        if system_blocked:
            # Réponse de sécurité si système bloqué
            response_content = """🚫 **Accès Temporairement Restreint**

Pour des raisons de sécurité, cette conversation a été suspendue. Notre système de protection a détecté un contenu potentiellement malveillant.

**Que faire maintenant ?**
• Reformulez votre question de manière plus claire
• Évitez d'utiliser des termes techniques sensibles
• Contactez notre support si c'est une erreur

**Support TeamSquare :** Nous sommes là pour vous aider de manière sécurisée ! 🛡️"""
            
            metadata = {
                "source": "security_block",
                "blocked": True,
                "threat_level": security_analysis.get('overall_threat_level', 'unknown'),
                "session_id": request.session_id,
                "analysis": security_analysis,
                "block_reason": system_state.get("block_reason", "Menace détectée")
            }
            
        else:
            # Traitement normal avec l'agent
            response_content = agent.process_query(request.query, request.session_id)
            
            # Métadonnées enrichies avec analyse sécurité
            metadata = {
                "source": "agentic_with_external_routing", 
                "session_id": request.session_id,
                "agent_version": "7.0.2",
                "security_analysis": security_analysis,
                "threat_level": security_analysis.get('overall_threat_level', 'safe'),
                "blocked": False
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
            
            # Mettre à jour l'activité utilisateur avec un score approprié
            threat_score = 0.0
            if security_analysis.get('overall_threat_level') == 'critical':
                threat_score = 1.0
            elif security_analysis.get('overall_threat_level') == 'high':
                threat_score = 0.8
            elif security_analysis.get('overall_threat_level') == 'medium':
                threat_score = 0.5
            elif security_analysis.get('overall_threat_level') == 'low':
                threat_score = 0.25
            
            update_user_activity(request.session_id, threat_score=threat_score, blocked=False)
        
        logger.info(f"✅ Réponse générée (Blocked: {system_blocked}) - Threat: {security_analysis.get('overall_threat_level', 'safe')}")
        
        return AgenticChatResponse(
            content=response_content,
            metadata=metadata
        )
        
    except Exception as e:
        logger.error(f"❌ Erreur chat avec routage: {e}")
        # Réponse de fallback en cas d'erreur
        fallback_response = f"""Bonjour ! Je suis l'assistant TeamSquare avec protection de sécurité.

**Votre question :** {request.query}

Je rencontre actuellement un problème technique, mais je peux vous aider avec :
• Questions sur TeamSquare (prix, fonctionnalités)
• Support technique général
• Informations sur nos services

Pouvez-vous reformuler votre question ?"""
        
        return AgenticChatResponse(
            content=fallback_response,
            metadata={"error": str(e), "fallback": True, "session_id": request.session_id}
        )

@router.post("/chat/stream")
async def agentic_chat_stream(request: AgenticChatRequest):
    """Endpoint de chat avec streaming et sécurité"""
    try:
        if not AGENT_AVAILABLE or not agent:
            raise HTTPException(status_code=503, detail="Agent non disponible")
        
        logger.info(f"🔍 Requête streaming: {request.query[:50]}... (Session: {request.session_id})")
        
        # Vérifier si la session est bloquée
        if is_session_blocked(request.session_id):
            response_content = "🚫 Accès suspendu pour des raisons de sécurité. Veuillez contacter le support."
            return StreamingResponse(
                stream_response(response_content),
                media_type="text/event-stream"
            )
        
        # Analyse de sécurité
        security_analysis = await analyze_message_security(request.query, request.session_id)
        system_blocked = await check_and_block_if_needed(security_analysis, request.session_id, request.query)
        
        if system_blocked:
            response_content = "🚫 Accès suspendu pour des raisons de sécurité. Veuillez reformuler votre question."
        else:
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
        error_response = f"Désolé, je rencontre un problème technique avec votre question: {request.query}"
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
            "timestamp": datetime.now().isoformat(),
            "version": "7.0.2",
            "stats": stats,
            "security": {
                "enabled": True,
                "threat_level": system_state.get("threat_level", "safe"),
                "blocked_sessions": len([k for k, v in user_activities.items() if v.get("blocked", False)]),
                "total_alerts": len(security_alerts)
            },
            "features": {
                "vector_rag": stats.get("components_status", {}).get("chromadb", False),
                "networkx_graph": True,
                "memory": True,
                "external_routing": True,
                "streaming": True,
                "security_analysis": True,
                "auto_blocking": True,
                "keyword_detection": True,
                "llm_hybrid": stats.get("components_status", {}).get("llm_manager", False)
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Erreur status: {e}")
        return {
            "error": str(e),
            "agent_available": False,
            "timestamp": datetime.now().isoformat()
        }

@router.get("/security/stats")
async def get_security_stats():
    """Statistiques de sécurité"""
    try:
        from api.shared_state import user_activities
        
        blocked_sessions = sum(1 for activity in user_activities.values() if activity.get("blocked", False))
        high_risk_sessions = sum(1 for activity in user_activities.values() if activity.get("threat_score", 0) > 0.7)
        
        return {
            "total_alerts": len(security_alerts),
            "recent_alerts": security_alerts[:5],
            "blocked_sessions": blocked_sessions,
            "high_risk_sessions": high_risk_sessions,
            "system_state": system_state,
            "security_integrated": True,
            "keyword_detection_enabled": True
        }
    except Exception as e:
        return {"security_integrated": False, "error": str(e)}

# Import nécessaire pour le timestamp
from datetime import datetime
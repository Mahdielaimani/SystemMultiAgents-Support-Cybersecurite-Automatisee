# api/cybersecurity_routes.py - VERSION CORRIGÉE
"""
Routes API pour l'agent de cybersécurité avec intégration des modèles AI
"""
import logging
import sys
import os
from pathlib import Path
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import json
from datetime import datetime
import asyncio

# Ajouter le répertoire racine au path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Configuration du logging
logger = logging.getLogger(__name__)

# IMPORTANT: Création du router FastAPI
router = APIRouter()

# Import des modèles de sécurité avec gestion d'erreur
try:
    from agents.cybersecurity_agent.custom_model_loaders import HuggingFaceSecurityModels
    security_models = HuggingFaceSecurityModels()
    MODELS_AVAILABLE = True
    logger.info("✅ Modèles de sécurité chargés avec succès")
except Exception as e:
    logger.error(f"❌ Erreur chargement modèles de sécurité: {e}")
    security_models = None
    MODELS_AVAILABLE = False

# Import de l'agent de cybersécurité
try:
    from agents.cybersecurity_agent.enhanced_agent import EnhancedCybersecurityAgent
    cyber_agent = EnhancedCybersecurityAgent()
    AGENT_AVAILABLE = True
    logger.info("✅ Agent de cybersécurité chargé")
except Exception as e:
    logger.error(f"❌ Erreur chargement agent cybersécurité: {e}")
    cyber_agent = None
    AGENT_AVAILABLE = False

# Stockage des alertes et état du système (partagé avec server.py)
from api.shared_state import security_alerts, system_state

# Modèles Pydantic
class SecurityAnalysisRequest(BaseModel):
    text: str
    models: List[str] = ["vulnerability_classifier", "network_analyzer", "intent_classifier"]
    session_id: Optional[str] = "default"

class SecurityAnalysisResponse(BaseModel):
    vulnerability_classifier: Optional[Dict[str, Any]] = None
    network_analyzer: Optional[Dict[str, Any]] = None
    intent_classifier: Optional[Dict[str, Any]] = None
    overall_threat_level: str
    timestamp: str
    metadata: Dict[str, Any] = {}

class SecurityAlert(BaseModel):
    id: str
    type: str  # vulnerability, network, intent
    severity: str  # low, medium, high, critical
    message: str
    timestamp: str
    action_taken: str
    details: Optional[Dict[str, Any]] = {}

class SystemBlockRequest(BaseModel):
    reason: str
    severity: str = "critical"
    session_id: Optional[str] = None
    analysis: Optional[Dict[str, Any]] = None
    block_duration: Optional[int] = None  # en secondes

@router.get("/health")
async def security_health():
    """Vérification de santé du système de sécurité"""
    return {
        "status": "healthy" if MODELS_AVAILABLE else "degraded",
        "models_loaded": MODELS_AVAILABLE,
        "agent_available": AGENT_AVAILABLE,
        "system_state": system_state,
        "active_alerts": len(security_alerts),
        "version": "1.0.0"
    }

@router.post("/analyze")
async def analyze_security(request: SecurityAnalysisRequest):
    """Analyse de sécurité d'un texte avec les modèles AI - VERSION CORRIGÉE"""
    try:
        logger.info(f"🔍 Analyse de sécurité: {request.text[:50]}...")
        
        results = {}
        threat_detected = False
        threat_score = 0.0
        
        # Si les modèles ne sont pas disponibles, utiliser une analyse basique
        if not MODELS_AVAILABLE or not security_models:
            logger.warning("⚠️ Modèles AI non disponibles, utilisation de l'analyse basique")
            
            # Analyse basique par mots-clés
            text_lower = request.text.lower()
            
            # Détection de vulnérabilités
            vuln_keywords = {
                "sql": ["select", "union", "drop table", "or 1=1", "' or '", "--", "';"],
                "xss": ["<script>", "alert(", "javascript:", "onerror=", "onload="],
                "injection": ["exec(", "eval(", "system(", "../", "..\\"]
            }
            
            for vuln_type, keywords in vuln_keywords.items():
                if any(keyword in text_lower for keyword in keywords):
                    results["vulnerability_classifier"] = {
                        "vulnerability_type": vuln_type.upper(),
                        "confidence": 0.85
                    }
                    threat_detected = True
                    threat_score += 0.85
                    break
            else:
                results["vulnerability_classifier"] = {
                    "vulnerability_type": "SAFE",
                    "confidence": 0.90
                }
            
            # Détection d'intentions malveillantes
            malicious_keywords = ["hack", "exploit", "vulnérabilité", "attaque", "ddos", "injection", "contourner"]
            if any(keyword in text_lower for keyword in malicious_keywords):
                results["intent_classifier"] = {
                    "intent": "Malicious",
                    "confidence": 0.80
                }
                threat_detected = True
                threat_score += 0.80
            else:
                results["intent_classifier"] = {
                    "intent": "Legitimate",
                    "confidence": 0.90
                }
            
        else:
            # Utiliser les modèles AI
            if "vulnerability_classifier" in request.models:
                try:
                    vuln_result = security_models.classify_vulnerability(request.text)
                    results["vulnerability_classifier"] = vuln_result
                    
                    if vuln_result.get("vulnerability_type") not in ["SAFE", "error"]:
                        threat_detected = True
                        threat_score += vuln_result.get("confidence", 0) * 1.5
                        
                        # Créer une alerte
                        await create_alert(
                            type="vulnerability",
                            severity="high" if vuln_result.get("confidence", 0) > 0.8 else "medium",
                            message=f"Vulnérabilité détectée: {vuln_result.get('vulnerability_type')}",
                            details=vuln_result
                        )
                except Exception as e:
                    logger.error(f"Erreur vulnerability_classifier: {e}")
                    results["vulnerability_classifier"] = {"error": str(e)}
            
            if "network_analyzer" in request.models:
                try:
                    net_result = security_models.analyze_network_traffic(request.text)
                    results["network_analyzer"] = net_result
                    
                    if net_result.get("traffic_type") not in ["NORMAL", "error"]:
                        threat_detected = True
                        severity = "critical" if net_result.get("traffic_type") == "DDOS" else "high"
                        threat_score += net_result.get("confidence", 0) * 2
                        
                        await create_alert(
                            type="network",
                            severity=severity,
                            message=f"Activité réseau suspecte: {net_result.get('traffic_type')}",
                            details=net_result
                        )
                except Exception as e:
                    logger.error(f"Erreur network_analyzer: {e}")
                    results["network_analyzer"] = {"error": str(e)}
            
            if "intent_classifier" in request.models:
                try:
                    intent_result = security_models.classify_intent(request.text)
                    results["intent_classifier"] = intent_result
                    
                    if intent_result.get("intent") == "Malicious":
                        threat_detected = True
                        threat_score += intent_result.get("confidence", 0) * 1.5
                        
                        await create_alert(
                            type="intent",
                            severity="high" if intent_result.get("confidence", 0) > 0.7 else "medium",
                            message=f"Intention malveillante détectée (confiance: {intent_result.get('confidence', 0):.2%})",
                            details=intent_result
                        )
                except Exception as e:
                    logger.error(f"Erreur intent_classifier: {e}")
                    results["intent_classifier"] = {"error": str(e)}
        
        # Calculer le niveau de menace global
        if threat_score >= 2.5:
            threat_level = "critical"
        elif threat_score >= 1.5:
            threat_level = "high"
        elif threat_score >= 0.5:
            threat_level = "medium"
        elif threat_score > 0:
            threat_level = "low"
        else:
            threat_level = "safe"
        
        results["overall_threat_level"] = threat_level
        
        # Mettre à jour l'état du système
        system_state["threat_level"] = threat_level
        system_state["last_scan"] = datetime.now().isoformat()
        
        # Si menace critique, bloquer le système automatiquement
        if threat_level == "critical":
            logger.warning(f"🚨 MENACE CRITIQUE DÉTECTÉE - Blocage automatique")
            await block_system(SystemBlockRequest(
                reason=f"Menace critique détectée: {request.text[:50]}...",
                severity="critical",
                session_id=request.session_id,
                analysis=results
            ))
        
        # Ajouter les métadonnées
        results["timestamp"] = datetime.now().isoformat()
        results["metadata"] = {
            "text_length": len(request.text),
            "models_used": request.models,
            "threat_detected": threat_detected,
            "threat_score": threat_score,
            "session_id": request.session_id
        }
        
        logger.info(f"✅ Analyse terminée - Niveau de menace: {threat_level}")
        
        return SecurityAnalysisResponse(**results)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erreur analyse sécurité: {e}")
        # Retourner une réponse valide même en cas d'erreur
        return SecurityAnalysisResponse(
            vulnerability_classifier={"error": str(e)},
            network_analyzer={"error": str(e)},
            intent_classifier={"error": str(e)},
            overall_threat_level="error",
            timestamp=datetime.now().isoformat(),
            metadata={"error": str(e)}
        )

@router.post("/alert")
async def create_alert(
    type: str,
    severity: str,
    message: str,
    details: Optional[Dict[str, Any]] = None
):
    """Créer une alerte de sécurité"""
    alert = SecurityAlert(
        id=f"alert_{datetime.now().timestamp()}",
        type=type,
        severity=severity,
        message=message,
        timestamp=datetime.now().isoformat(),
        action_taken="Alerte créée et loggée",
        details=details or {}
    )
    
    security_alerts.append(alert.dict())
    
    # Limiter le nombre d'alertes stockées
    if len(security_alerts) > 100:
        security_alerts.pop(0)
    
    # Si alerte critique, notifier immédiatement
    if severity == "critical":
        logger.warning(f"🚨 ALERTE CRITIQUE: {message}")
        system_state["active_threats"].append(alert.dict())
        system_state["total_threats_detected"] = system_state.get("total_threats_detected", 0) + 1
    
    logger.info(f"🚨 Nouvelle alerte créée: {type} - {severity} - {message}")
    
    return alert

@router.get("/alerts")
async def get_alerts(
    limit: int = 50,
    severity: Optional[str] = None,
    type: Optional[str] = None
):
    """Récupérer les alertes de sécurité"""
    # Forcer l'utilisation de la liste partagée
    from api.shared_state import security_alerts as shared_alerts
    
    filtered_alerts = list(shared_alerts)  # Créer une copie pour éviter les modifications
    
    if severity:
        filtered_alerts = [a for a in filtered_alerts if a["severity"] == severity]
    
    if type:
        filtered_alerts = [a for a in filtered_alerts if a["type"] == type]
    
    # Trier par timestamp décroissant
    filtered_alerts.sort(key=lambda x: x["timestamp"], reverse=True)
    
    return {
        "alerts": filtered_alerts[:limit],
        "total": len(filtered_alerts),
        "filters": {
            "severity": severity,
            "type": type
        },
        "timestamp": datetime.now().isoformat()  # Pour forcer le refresh
    }

@router.post("/block")
async def block_system(request: SystemBlockRequest):
    """Bloquer le système pour des raisons de sécurité"""
    system_state["blocked"] = True
    system_state["block_reason"] = request.reason
    system_state["block_time"] = datetime.now().isoformat()
    system_state["threat_level"] = "danger"
    
    # Créer une alerte de blocage
    await create_alert(
        type="system",
        severity=request.severity,
        message=f"Système bloqué: {request.reason}",
        details={
            "duration": request.block_duration,
            "session_id": request.session_id,
            "analysis": request.analysis
        }
    )
    
    # Si durée spécifiée, débloquer après le délai
    if request.block_duration:
        asyncio.create_task(auto_unblock(request.block_duration))
    
    logger.warning(f"🚫 Système bloqué: {request.reason}")
    
    return {
        "status": "blocked",
        "reason": request.reason,
        "timestamp": system_state["block_time"]
    }

@router.post("/unblock")
async def unblock_system():
    """Débloquer le système"""
    system_state["blocked"] = False
    system_state["block_reason"] = None
    system_state["threat_level"] = "safe"
    system_state["active_threats"] = []
    
    logger.info("✅ Système débloqué")
    
    return {
        "status": "unblocked",
        "timestamp": datetime.now().isoformat()
    }

async def auto_unblock(duration: int):
    """Débloquer automatiquement le système après un délai"""
    await asyncio.sleep(duration)
    if system_state["blocked"]:
        await unblock_system()
        logger.info(f"✅ Système débloqué automatiquement après {duration} secondes")

# Gestionnaire de modèles pour compatibilité
models_manager = security_models
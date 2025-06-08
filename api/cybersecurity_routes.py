# api/cybersecurity_routes.py
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

# Import des modèles de sécurité
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

# Stockage des alertes et état du système
security_alerts = []
system_state = {
    "blocked": False,
    "threat_level": "safe",
    "active_threats": [],
    "last_scan": None
}

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
    """Analyse de sécurité d'un texte avec les modèles AI"""
    try:
        if not MODELS_AVAILABLE or not security_models:
            raise HTTPException(status_code=503, detail="Modèles de sécurité non disponibles")
        
        logger.info(f"🔍 Analyse de sécurité: {request.text[:50]}...")
        
        results = {}
        threat_detected = False
        
        # Analyse avec chaque modèle
        if "vulnerability_classifier" in request.models:
            try:
                vuln_result = security_models.classify_vulnerability(request.text)
                results["vulnerability_classifier"] = vuln_result
                
                if vuln_result.get("vulnerability_type") != "SAFE":
                    threat_detected = True
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
                
                if net_result.get("traffic_type") != "NORMAL":
                    threat_detected = True
                    severity = "critical" if net_result.get("traffic_type") == "DDOS" else "high"
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
                    await create_alert(
                        type="intent",
                        severity="high" if intent_result.get("confidence", 0) > 0.5 else "medium",
                        message=f"Intention malveillante détectée (confiance: {intent_result.get('confidence', 0):.2%})",
                        details=intent_result
                    )
            except Exception as e:
                logger.error(f"Erreur intent_classifier: {e}")
                results["intent_classifier"] = {"error": str(e)}
        
        # Calculer le niveau de menace global
        threat_level = calculate_overall_threat_level(results)
        results["overall_threat_level"] = threat_level
        
        # Mettre à jour l'état du système
        system_state["threat_level"] = threat_level
        system_state["last_scan"] = datetime.now().isoformat()
        
        # Si menace critique, bloquer le système
        if threat_level == "critical":
            await block_system("Menace critique détectée", "critical")
        
        # Ajouter les métadonnées
        results["timestamp"] = datetime.now().isoformat()
        results["metadata"] = {
            "text_length": len(request.text),
            "models_used": request.models,
            "threat_detected": threat_detected,
            "session_id": request.session_id
        }
        
        logger.info(f"✅ Analyse terminée - Niveau de menace: {threat_level}")
        
        return SecurityAnalysisResponse(**results)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erreur analyse sécurité: {e}")
        raise HTTPException(status_code=500, detail=str(e))

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
    
    return alert

@router.get("/alerts")
async def get_alerts(
    limit: int = 50,
    severity: Optional[str] = None,
    type: Optional[str] = None
):
    """Récupérer les alertes de sécurité"""
    filtered_alerts = security_alerts
    
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
        }
    }

@router.post("/block")
async def block_system(request: SystemBlockRequest):
    """Bloquer le système pour des raisons de sécurité"""
    system_state["blocked"] = True
    system_state["block_reason"] = request.reason
    system_state["block_time"] = datetime.now().isoformat()
    
    # Créer une alerte de blocage
    await create_alert(
        type="system",
        severity=request.severity,
        message=f"Système bloqué: {request.reason}",
        details={"duration": request.block_duration}
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

@router.get("/report")
async def generate_security_report():
    """Générer un rapport de sécurité"""
    # Compter les alertes par type et sévérité
    alert_stats = {
        "by_type": {},
        "by_severity": {},
        "total": len(security_alerts)
    }
    
    for alert in security_alerts:
        # Par type
        alert_type = alert["type"]
        alert_stats["by_type"][alert_type] = alert_stats["by_type"].get(alert_type, 0) + 1
        
        # Par sévérité
        severity = alert["severity"]
        alert_stats["by_severity"][severity] = alert_stats["by_severity"].get(severity, 0) + 1
    
    # Alertes critiques récentes
    critical_alerts = [a for a in security_alerts if a["severity"] == "critical"][-5:]
    
    report = {
        "generated_at": datetime.now().isoformat(),
        "system_state": system_state,
        "alert_statistics": alert_stats,
        "recent_critical_alerts": critical_alerts,
        "recommendations": generate_recommendations(alert_stats),
        "models_status": {
            "vulnerability_classifier": "active" if MODELS_AVAILABLE else "inactive",
            "network_analyzer": "active" if MODELS_AVAILABLE else "inactive",
            "intent_classifier": "active" if MODELS_AVAILABLE else "inactive"
        }
    }
    
    return report

@router.get("/models/info")
async def get_models_info():
    """Informations sur les modèles de sécurité"""
    if not MODELS_AVAILABLE or not security_models:
        raise HTTPException(status_code=503, detail="Modèles non disponibles")
    
    try:
        info = security_models.get_model_info()
        return info
    except Exception as e:
        logger.error(f"Erreur récupération info modèles: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/models/test")
async def test_models():
    """Tester les modèles de sécurité"""
    if not MODELS_AVAILABLE or not security_models:
        raise HTTPException(status_code=503, detail="Modèles non disponibles")
    
    try:
        test_results = security_models.test_all_models()
        return test_results
    except Exception as e:
        logger.error(f"Erreur test modèles: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Fonctions utilitaires
def calculate_overall_threat_level(results: Dict[str, Any]) -> str:
    """Calculer le niveau de menace global"""
    threat_score = 0
    
    # Vérifier les vulnérabilités
    if "vulnerability_classifier" in results:
        vuln = results["vulnerability_classifier"]
        if vuln.get("vulnerability_type") not in ["SAFE", "error", None]:
            threat_score += vuln.get("confidence", 0) * 3
    
    # Vérifier le trafic réseau
    if "network_analyzer" in results:
        net = results["network_analyzer"]
        if net.get("traffic_type") not in ["NORMAL", "error", None]:
            threat_score += net.get("confidence", 0) * 2
    
    # Vérifier l'intention
    if "intent_classifier" in results:
        intent = results["intent_classifier"]
        if intent.get("intent") == "Malicious":
            threat_score += intent.get("confidence", 0) * 2.5
        elif intent.get("intent") == "Suspicious":
            threat_score += intent.get("confidence", 0) * 1
    
    # Déterminer le niveau
    if threat_score >= 2.5:
        return "critical"
    elif threat_score >= 1.5:
        return "high"
    elif threat_score >= 0.5:
        return "medium"
    elif threat_score > 0:
        return "low"
    else:
        return "safe"

def generate_recommendations(alert_stats: Dict[str, Any]) -> List[str]:
    """Générer des recommandations basées sur les statistiques"""
    recommendations = []
    
    # Recommandations basées sur le nombre total d'alertes
    if alert_stats["total"] > 50:
        recommendations.append("Nombre élevé d'alertes détectées - renforcer la surveillance")
    
    # Recommandations par type
    if alert_stats["by_type"].get("vulnerability", 0) > 10:
        recommendations.append("Nombreuses vulnérabilités détectées - mettre à jour les filtres de sécurité")
    
    if alert_stats["by_type"].get("network", 0) > 5:
        recommendations.append("Activité réseau suspecte fréquente - vérifier les règles du pare-feu")
    
    if alert_stats["by_type"].get("intent", 0) > 15:
        recommendations.append("Intentions malveillantes récurrentes - former les utilisateurs")
    
    # Recommandations par sévérité
    if alert_stats["by_severity"].get("critical", 0) > 0:
        recommendations.append("Alertes critiques détectées - audit de sécurité recommandé")
    
    if not recommendations:
        recommendations.append("Système sécurisé - continuer la surveillance normale")
    
    return recommendations

async def auto_unblock(duration: int):
    """Débloquer automatiquement le système après un délai"""
    await asyncio.sleep(duration)
    if system_state["blocked"]:
        await unblock_system()
        logger.info(f"✅ Système débloqué automatiquement après {duration} secondes")

# WebSocket pour les notifications en temps réel (optionnel)
from fastapi import WebSocket, WebSocketDisconnect
from typing import Set

class ConnectionManager:
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.add(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                pass

manager = ConnectionManager()

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket pour les notifications en temps réel"""
    await manager.connect(websocket)
    try:
        while True:
            # Envoyer l'état du système périodiquement
            await websocket.send_json({
                "type": "system_state",
                "data": system_state,
                "timestamp": datetime.now().isoformat()
            })
            await asyncio.sleep(5)  # Mise à jour toutes les 5 secondes
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"Erreur WebSocket: {e}")
        manager.disconnect(websocket)
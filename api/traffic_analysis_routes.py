# api/traffic_analysis_routes.py
"""
Routes API pour l'analyse de trafic réseau en temps réel
Intégration avec le modèle CICIDS2017
"""
import asyncio
import logging
import threading
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from pathlib import Path
import sys

# Ajouter le répertoire racine au path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

logger = logging.getLogger(__name__)

# Créer le router
router = APIRouter()

# État global de l'analyse de trafic
traffic_analysis_state = {
    "active": False,
    "start_time": None,
    "total_flows": 0,
    "normal_flows": 0,
    "threat_flows": 0,
    "current_throughput": 0,
    "packets_per_second": 0,
    "recent_detections": [],
    "config": {
        "duration": 30,
        "interface": "any",
        "sensitivity": "medium"
    }
}

# Thread de capture global
capture_thread = None
stop_capture_event = threading.Event()

# Modèles Pydantic
class TrafficAnalysisConfig(BaseModel):
    duration: int = 30  # -1 pour continu
    interface: str = "any"
    sensitivity: str = "medium"  # low, medium, high

class TrafficDetection(BaseModel):
    type: str
    confidence: float
    description: str
    timestamp: str
    source_ip: Optional[str] = None
    dest_ip: Optional[str] = None
    flow_info: Optional[Dict] = None

# Fonction de capture en arrière-plan
def background_traffic_capture():
    """Fonction de capture de trafic en arrière-plan"""
    global traffic_analysis_state
    
    try:
        from agents.cybersecurity_agent.traffic_collector import RealTimeTrafficCollector
        from agents.cybersecurity_agent.custom_model_loaders import NetworkAnalyzerXGBoost
        
        logger.info("🔍 Démarrage capture trafic en arrière-plan")
        
        # Initialiser le collecteur et le modèle
        collector = RealTimeTrafficCollector(
            interface=traffic_analysis_state["config"]["interface"]
        )
        model = NetworkAnalyzerXGBoost()
        
        # Statistiques de performance
        last_packet_count = 0
        last_time = time.time()
        
        while not stop_capture_event.is_set():
            try:
                # Capturer du trafic par blocs de 10 secondes
                features_df = collector.start_capture(duration=10, max_packets=100)
                
                if not features_df.empty:
                    current_time = time.time()
                    new_flows = len(features_df)
                    
                    # Mettre à jour les statistiques
                    traffic_analysis_state["total_flows"] += new_flows
                    
                    # Calculer le débit
                    time_diff = current_time - last_time
                    if time_diff > 0:
                        traffic_analysis_state["packets_per_second"] = int(
                            (new_flows - last_packet_count) / time_diff
                        )
                    
                    last_packet_count = new_flows
                    last_time = current_time
                    
                    # Analyser chaque flow avec le modèle
                    normal_count = 0
                    threat_count = 0
                    
                    for index, row in features_df.iterrows():
                        try:
                            # Créer une description du flow pour le modèle
                            flow_description = create_flow_description(row)
                            
                            # Prédiction avec le modèle CICIDS2017
                            prediction = model.predict([flow_description])
                            
                            if prediction and len(prediction) > 0:
                                result = prediction[0]
                                label = result.get('label', 'UNKNOWN')
                                confidence = result.get('score', 0)
                                
                                if label == 'NORMAL':
                                    normal_count += 1
                                else:
                                    threat_count += 1
                                    
                                    # Ajouter aux détections si c'est une menace
                                    if confidence > get_sensitivity_threshold():
                                        detection = {
                                            "type": label,
                                            "confidence": confidence,
                                            "description": f"Trafic suspect détecté: {label}",
                                            "timestamp": datetime.now().isoformat(),
                                            "flow_info": {
                                                "fwd_packets": row.get('Total Fwd Packets', 0),
                                                "bwd_packets": row.get('Total Backward Packets', 0),
                                                "duration": row.get('Flow Duration', 0)
                                            }
                                        }
                                        
                                        # Ajouter à la liste des détections récentes
                                        traffic_analysis_state["recent_detections"].insert(0, detection)
                                        
                                        # Limiter à 20 détections récentes
                                        if len(traffic_analysis_state["recent_detections"]) > 20:
                                            traffic_analysis_state["recent_detections"] = traffic_analysis_state["recent_detections"][:20]
                                        
                                        logger.warning(f"🚨 Menace détectée: {label} (confiance: {confidence:.2%})")
                            
                        except Exception as e:
                            logger.debug(f"Erreur analyse flow: {e}")
                    
                    # Mettre à jour les compteurs
                    traffic_analysis_state["normal_flows"] += normal_count
                    traffic_analysis_state["threat_flows"] += threat_count
                    
                    # Calculer le débit approximatif en bytes
                    avg_packet_size = 1024  # Estimation
                    traffic_analysis_state["current_throughput"] = int(
                        traffic_analysis_state["packets_per_second"] * avg_packet_size
                    )
                    
                    logger.info(f"📊 Flows analysés: {new_flows} (Normal: {normal_count}, Menaces: {threat_count})")
                
                else:
                    # Pas de trafic capturé
                    traffic_analysis_state["packets_per_second"] = 0
                    traffic_analysis_state["current_throughput"] = 0
                
                # Vérifier si on doit arrêter (durée limitée)
                if (traffic_analysis_state["config"]["duration"] > 0 and 
                    traffic_analysis_state["start_time"] and
                    time.time() - traffic_analysis_state["start_time"] >= traffic_analysis_state["config"]["duration"]):
                    logger.info("⏰ Durée d'analyse terminée")
                    break
                
                # Pause courte avant la prochaine capture
                time.sleep(2)
                
            except Exception as e:
                logger.error(f"❌ Erreur dans la boucle de capture: {e}")
                time.sleep(5)  # Pause plus longue en cas d'erreur
        
    except Exception as e:
        logger.error(f"❌ Erreur fatale capture trafic: {e}")
    
    finally:
        # Nettoyer l'état
        traffic_analysis_state["active"] = False
        logger.info("🛑 Capture trafic arrêtée")

def create_flow_description(flow_row) -> str:
    """Crée une description textuelle d'un flow pour le modèle"""
    try:
        fwd_packets = flow_row.get('Total Fwd Packets', 0)
        bwd_packets = flow_row.get('Total Backward Packets', 0)
        duration = flow_row.get('Flow Duration', 0)
        fwd_bytes = flow_row.get('Total Length of Fwd Packets', 0)
        flags = {
            'syn': flow_row.get('SYN Flag Count', 0),
            'ack': flow_row.get('ACK Flag Count', 0),
            'rst': flow_row.get('RST Flag Count', 0)
        }
        
        # Créer une description basée sur les caractéristiques du flow
        if fwd_packets > 100 and bwd_packets < 10:
            return f"high volume one-way traffic with {fwd_packets} packets"
        elif flags['syn'] > 10 and flags['ack'] < 5:
            return f"multiple syn requests scanning pattern"
        elif duration < 1000 and fwd_packets > 20:
            return f"short duration high packet rate flow"
        elif fwd_bytes > 10000 and bwd_packets == 0:
            return f"large data transfer without response"
        else:
            return f"normal bidirectional flow {fwd_packets} forward {bwd_packets} backward packets"
            
    except Exception as e:
        logger.debug(f"Erreur création description flow: {e}")
        return "network flow analysis"

def get_sensitivity_threshold() -> float:
    """Retourne le seuil de confiance selon la sensibilité"""
    sensitivity = traffic_analysis_state["config"]["sensitivity"]
    
    if sensitivity == "high":
        return 0.5  # Détecter plus de menaces
    elif sensitivity == "medium":
        return 0.7  # Équilibré
    else:  # low
        return 0.8  # Seulement les menaces très sûres

# Routes API
@router.post("/start-traffic-analysis")
async def start_traffic_analysis(config: TrafficAnalysisConfig, background_tasks: BackgroundTasks):
    """Démarre l'analyse de trafic réseau"""
    global capture_thread, stop_capture_event
    
    try:
        if traffic_analysis_state["active"]:
            raise HTTPException(status_code=400, detail="Analyse déjà en cours")
        
        logger.info(f"🚀 Démarrage analyse trafic - Config: {config.dict()}")
        
        # Mettre à jour la configuration
        traffic_analysis_state["config"] = config.dict()
        traffic_analysis_state["active"] = True
        traffic_analysis_state["start_time"] = time.time()
        
        # Réinitialiser les statistiques
        traffic_analysis_state.update({
            "total_flows": 0,
            "normal_flows": 0,
            "threat_flows": 0,
            "current_throughput": 0,
            "packets_per_second": 0,
            "recent_detections": []
        })
        
        # Démarrer le thread de capture
        stop_capture_event.clear()
        capture_thread = threading.Thread(target=background_traffic_capture)
        capture_thread.daemon = True
        capture_thread.start()
        
        return {
            "status": "started",
            "message": "Analyse de trafic démarrée",
            "config": config.dict(),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Erreur démarrage analyse: {e}")
        traffic_analysis_state["active"] = False
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/stop-traffic-analysis")
async def stop_traffic_analysis():
    """Arrête l'analyse de trafic réseau"""
    global capture_thread, stop_capture_event
    
    try:
        if not traffic_analysis_state["active"]:
            raise HTTPException(status_code=400, detail="Aucune analyse en cours")
        
        logger.info("🛑 Arrêt de l'analyse de trafic demandé")
        
        # Arrêter le thread de capture
        stop_capture_event.set()
        
        if capture_thread and capture_thread.is_alive():
            capture_thread.join(timeout=5)  # Attendre 5 secondes max
        
        traffic_analysis_state["active"] = False
        
        return {
            "status": "stopped",
            "message": "Analyse de trafic arrêtée",
            "final_stats": {
                "total_flows": traffic_analysis_state["total_flows"],
                "normal_flows": traffic_analysis_state["normal_flows"],
                "threat_flows": traffic_analysis_state["threat_flows"],
                "duration": time.time() - traffic_analysis_state["start_time"] if traffic_analysis_state["start_time"] else 0
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Erreur arrêt analyse: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/traffic-status")
async def get_traffic_status():
    """Récupère le statut actuel de l'analyse de trafic"""
    try:
        return {
            "active": traffic_analysis_state["active"],
            "total_flows": traffic_analysis_state["total_flows"],
            "normal_flows": traffic_analysis_state["normal_flows"],
            "threat_flows": traffic_analysis_state["threat_flows"],
            "throughput": traffic_analysis_state["current_throughput"],
            "packets_per_second": traffic_analysis_state["packets_per_second"],
            "recent_detections": traffic_analysis_state["recent_detections"][:5],  # 5 dernières
            "config": traffic_analysis_state["config"],
            "start_time": traffic_analysis_state["start_time"],
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Erreur récupération statut: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/traffic-detections")
async def get_traffic_detections(limit: int = 20):
    """Récupère les détections récentes"""
    try:
        detections = traffic_analysis_state["recent_detections"][:limit]
        
        return {
            "detections": detections,
            "total": len(traffic_analysis_state["recent_detections"]),
            "active_analysis": traffic_analysis_state["active"],
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Erreur récupération détections: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/test-traffic-model")
async def test_traffic_model():
    """Test rapide du modèle d'analyse de trafic"""
    try:
        from agents.cybersecurity_agent.custom_model_loaders import NetworkAnalyzerXGBoost
        
        model = NetworkAnalyzerXGBoost()
        
        # Tests de base
        test_cases = [
            "normal web browsing traffic",
            "ddos attack high volume",
            "port scan reconnaissance", 
            "brute force ssh attempts"
        ]
        
        results = []
        for test_case in test_cases:
            prediction = model.predict([test_case])
            if prediction:
                results.append({
                    "input": test_case,
                    "prediction": prediction[0]
                })
        
        return {
            "status": "success",
            "model_loaded": True,
            "test_results": results,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Erreur test modèle: {e}")
        return {
            "status": "error",
            "model_loaded": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List
from agents.cybersecurity_agent.guardian_robot import guardian_robot

router = APIRouter()

@router.get("/guardian/status")
async def get_guardian_status():
    """Obtenir le statut du robot gardien"""
    return guardian_robot.get_status()

@router.get("/guardian/realtime")
async def get_realtime_data():
    """Données en temps réel pour le monitoring"""
    return guardian_robot.get_real_time_data()

@router.post("/guardian/start")
async def start_guardian():
    """Démarrer le robot gardien"""
    guardian_robot.start_guardian()
    return {"message": "Robot gardien démarré", "status": "active"}

@router.post("/guardian/stop")
async def stop_guardian():
    """Arrêter le robot gardien"""
    guardian_robot.stop_guardian()
    return {"message": "Robot gardien arrêté", "status": "stopped"}

@router.post("/guardian/add-website")
async def add_website(website_data: Dict[str, Any]):
    """Ajouter un site web à surveiller"""
    url = website_data.get("url")
    scan_depth = website_data.get("scan_depth", 2)
    
    if not url:
        raise HTTPException(status_code=400, detail="URL requise")
    
    guardian_robot.add_website_to_guard(url, scan_depth)
    return {"message": f"Site {url} ajouté à la surveillance"}

@router.get("/guardian/vulnerabilities")
async def get_vulnerabilities():
    """Obtenir toutes les vulnérabilités détectées"""
    all_vulns = []
    
    for scan_id, scan_data in guardian_robot.scan_results.items():
        for vuln in scan_data.get("vulnerabilities", []):
            vuln_data = vuln.copy()
            vuln_data["scan_id"] = scan_id
            vuln_data["website"] = scan_data["website"]
            vuln_data["scan_timestamp"] = scan_data["timestamp"]
            all_vulns.append(vuln_data)
    
    return {"vulnerabilities": all_vulns}

"""
Générateur de rapports pour l'agent de cybersécurité.
"""
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import json

logger = logging.getLogger(__name__)

class ReportGenerator:
    """
    Générateur de rapports de sécurité basés sur les résultats de scan.
    """
    
    def __init__(self):
        """Initialise le générateur de rapports."""
        pass
    
    def generate_text_report(self, scan_results: Dict[str, Any], url: str) -> str:
        """
        Génère un rapport textuel basé sur les résultats du scan.
        
        Args:
            scan_results: Résultats du scan
            url: URL scannée
            
        Returns:
            Rapport formaté en texte
        """
        if not scan_results.get("success", False):
            return f"Le scan de {url} a échoué: {scan_results.get('error', 'Erreur inconnue')}"
        
        vulnerabilities = scan_results.get("vulnerabilities", [])
        
        # Générer l'en-tête du rapport
        report = f"# Rapport de sécurité pour {url}\n\n"
        report += f"Date du scan: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        # Résumé des vulnérabilités
        report += f"## Résumé\n\n"
        report += f"Nombre total de vulnérabilités détectées: {len(vulnerabilities)}\n\n"
        
        # Compter les vulnérabilités par sévérité
        severity_counts = {"high": 0, "medium": 0, "low": 0, "info": 0}
        for vuln in vulnerabilities:
            severity = vuln.get("severity", "info").lower()
            if severity in severity_counts:
                severity_counts[severity] += 1
        
        report += "Répartition par sévérité:\n"
        report += f"- Haute: {severity_counts['high']}\n"
        report += f"- Moyenne: {severity_counts['medium']}\n"
        report += f"- Basse: {severity_counts['low']}\n"
        report += f"- Informative: {severity_counts['info']}\n\n"
        
        # Détails des vulnérabilités
        report += f"## Vulnérabilités détectées\n\n"
        
        if not vulnerabilities:
            report += "Aucune vulnérabilité détectée.\n\n"
        else:
            # Trier les vulnérabilités par sévérité
            severity_order = {"high": 0, "medium": 1, "low": 2, "info": 3}
            sorted_vulns = sorted(
                vulnerabilities,
                key=lambda v: severity_order.get(v.get("severity", "info").lower(), 4)
            )
            
            for i, vuln in enumerate(sorted_vulns, 1):
                severity = vuln.get("severity", "info").lower()
                name = vuln.get("name", "Vulnérabilité inconnue")
                description = vuln.get("description", "Aucune description disponible")
                
                report += f"### {i}. {name} (Sévérité: {severity.capitalize()})\n\n"
                report += f"{description}\n\n"
        
        # Recommandations générales
        report += f"## Recommandations générales\n\n"
        report += "1. Maintenez tous vos logiciels et composants à jour\n"
        report += "2. Configurez correctement les en-têtes de sécurité HTTP\n"
        report += "3. Implémentez une validation stricte des entrées utilisateur\n"
        report += "4. Utilisez des frameworks et bibliothèques sécurisés\n"
        report += "5. Effectuez des audits de sécurité réguliers\n\n"
        
        # Pied de page
        report += f"Ce rapport a été généré automatiquement par NextGen-Agent.\n"
        
        return report
    
    def generate_json_report(self, scan_results: Dict[str, Any], url: str) -> str:
        """
        Génère un rapport JSON basé sur les résultats du scan.
        
        Args:
            scan_results: Résultats du scan
            url: URL scannée
            
        Returns:
            Rapport formaté en JSON
        """
        report = {
            "url": url,
            "scan_date": datetime.now().isoformat(),
            "success": scan_results.get("success", False),
            "scan_id": scan_results.get("scan_id", ""),
            "vulnerabilities": scan_results.get("vulnerabilities", []),
            "summary": {
                "total_vulnerabilities": len(scan_results.get("vulnerabilities", [])),
                "severity_counts": {
                    "high": sum(1 for v in scan_results.get("vulnerabilities", []) if v.get("severity") == "high"),
                    "medium": sum(1 for v in scan_results.get("vulnerabilities", []) if v.get("severity") == "medium"),
                    "low": sum(1 for v in scan_results.get("vulnerabilities", []) if v.get("severity") == "low"),
                    "info": sum(1 for v in scan_results.get("vulnerabilities", []) if v.get("severity") == "info")
                }
            }
        }
        
        if not scan_results.get("success", False):
            report["error"] = scan_results.get("error", "Erreur inconnue")
        
        return json.dumps(report, indent=2)

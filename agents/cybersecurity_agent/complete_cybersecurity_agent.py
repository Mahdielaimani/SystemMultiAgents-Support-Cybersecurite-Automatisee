"""
Agent de Cybersécurité Complet - NextGen Agent
Intègre tous les composants de sécurité en une solution unifiée
"""
import asyncio
import logging
import json
import time
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from pathlib import Path

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CompleteCybersecurityAgent:
    """
    Agent de cybersécurité complet intégrant tous les composants
    """
    
    def __init__(self):
        """Initialisation de l'agent de cybersécurité"""
        logger.info("🔒 Initialisation de l'agent de cybersécurité complet...")
        
        # Composants principaux
        self.vulnerability_classifier = None
        self.web_scanner = None
        self.network_analyzer = None
        self.recommender = None
        self.report_generator = None
        
        # État de l'agent
        self.is_initialized = False
        self.capabilities = []
        
        # Statistiques
        self.stats = {
            "scans_performed": 0,
            "vulnerabilities_found": 0,
            "reports_generated": 0,
            "network_analyses": 0,
            "threats_detected": 0
        }
        
        # Historique des scans
        self.scan_history = []
        
        # Initialiser les composants
        self._initialize_components()
    
    def _initialize_components(self):
        """Initialise tous les composants de sécurité"""
        try:
            # 1. Classificateur de vulnérabilités
            self._init_vulnerability_classifier()
            
            # 2. Scanner web
            self._init_web_scanner()
            
            # 3. Analyseur réseau
            self._init_network_analyzer()
            
            # 4. Générateur de recommandations
            self._init_recommender()
            
            # 5. Générateur de rapports
            self._init_report_generator()
            
            self.is_initialized = True
            logger.info("✅ Agent de cybersécurité initialisé avec succès")
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de l'initialisation: {e}")
            self.is_initialized = False
    
    def _init_vulnerability_classifier(self):
        """Initialise le classificateur de vulnérabilités"""
        try:
            from agents.cybersecurity_agent.classifier import VulnerabilityClassifier
            model_path = "models/vulnerability_classifier"
            self.vulnerability_classifier = VulnerabilityClassifier(model_path)
            self.capabilities.append("vulnerability_classification")
            logger.info("✅ Classificateur de vulnérabilités initialisé")
        except Exception as e:
            logger.warning(f"⚠️ Classificateur non disponible: {e}")
    
    def _init_web_scanner(self):
        """Initialise le scanner web"""
        try:
            from agents.cybersecurity_agent.scanner import WebScanner
            self.web_scanner = WebScanner()
            self.capabilities.append("web_scanning")
            logger.info("✅ Scanner web initialisé")
        except Exception as e:
            logger.warning(f"⚠️ Scanner web non disponible: {e}")
    
    def _init_network_analyzer(self):
        """Initialise l'analyseur réseau"""
        try:
            from agents.cybersecurity_agent.network_analyzer import NetworkAnalyzer
            model_path = "models/network_analyzer.pkl"
            self.network_analyzer = NetworkAnalyzer(model_path)
            self.capabilities.append("network_analysis")
            logger.info("✅ Analyseur réseau initialisé")
        except Exception as e:
            logger.warning(f"⚠️ Analyseur réseau non disponible: {e}")
    
    def _init_recommender(self):
        """Initialise le générateur de recommandations"""
        try:
            from agents.cybersecurity_agent.recommender import SecurityRecommender
            self.recommender = SecurityRecommender()
            self.capabilities.append("security_recommendations")
            logger.info("✅ Générateur de recommandations initialisé")
        except Exception as e:
            logger.warning(f"⚠️ Générateur de recommandations non disponible: {e}")
    
    def _init_report_generator(self):
        """Initialise le générateur de rapports"""
        try:
            from agents.cybersecurity_agent.report import ReportGenerator
            self.report_generator = ReportGenerator()
            self.capabilities.append("report_generation")
            logger.info("✅ Générateur de rapports initialisé")
        except Exception as e:
            logger.warning(f"⚠️ Générateur de rapports non disponible: {e}")
    
    async def comprehensive_security_scan(self, target: str, scan_type: str = "full") -> Dict[str, Any]:
        """
        Effectue un scan de sécurité complet
        
        Args:
            target: URL ou adresse IP à scanner
            scan_type: Type de scan (basic, full, network)
            
        Returns:
            Résultats complets du scan
        """
        if not self.is_initialized:
            return {"error": "Agent non initialisé", "status": "error"}
        
        scan_id = f"scan_{int(time.time())}"
        scan_start = time.time()
        
        logger.info(f"🔍 Début du scan de sécurité: {target} (Type: {scan_type})")
        
        results = {
            "scan_id": scan_id,
            "target": target,
            "scan_type": scan_type,
            "timestamp": datetime.now().isoformat(),
            "status": "in_progress",
            "components": {},
            "summary": {},
            "recommendations": [],
            "report": ""
        }
        
        try:
            # 1. Scan web si disponible
            if self.web_scanner and scan_type in ["basic", "full"]:
                logger.info("🌐 Scan web en cours...")
                web_results = await self.web_scanner.scan_url(target)
                results["components"]["web_scan"] = web_results
                
                if web_results.get("success"):
                    self.stats["vulnerabilities_found"] += len(web_results.get("vulnerabilities", []))
            
            # 2. Classification de vulnérabilités si disponible
            if self.vulnerability_classifier and scan_type in ["full"]:
                logger.info("🔍 Classification des vulnérabilités...")
                vuln_classification = self.vulnerability_classifier.classify(target)
                results["components"]["vulnerability_classification"] = vuln_classification
            
            # 3. Analyse réseau si demandée
            if self.network_analyzer and scan_type in ["network", "full"]:
                logger.info("🌐 Analyse réseau...")
                # Simuler des données réseau pour la démo
                network_data = self._generate_sample_network_data()
                network_results = self.network_analyzer.analyze(network_data)
                results["components"]["network_analysis"] = network_results
                
                if network_results.get("is_attack"):
                    self.stats["threats_detected"] += 1
            
            # 4. Générer des recommandations
            if self.recommender:
                logger.info("📋 Génération des recommandations...")
                recommendations = self._generate_comprehensive_recommendations(results)
                results["recommendations"] = recommendations
            
            # 5. Générer le rapport
            if self.report_generator:
                logger.info("📄 Génération du rapport...")
                report = self._generate_comprehensive_report(results)
                results["report"] = report
                self.stats["reports_generated"] += 1
            
            # Finaliser les résultats
            scan_duration = time.time() - scan_start
            results["status"] = "completed"
            results["duration"] = scan_duration
            results["summary"] = self._generate_scan_summary(results)
            
            # Mettre à jour les statistiques
            self.stats["scans_performed"] += 1
            self.scan_history.append({
                "scan_id": scan_id,
                "target": target,
                "timestamp": datetime.now().isoformat(),
                "duration": scan_duration,
                "vulnerabilities": len(results.get("components", {}).get("web_scan", {}).get("vulnerabilities", []))
            })
            
            logger.info(f"✅ Scan terminé en {scan_duration:.2f}s")
            return results
            
        except Exception as e:
            logger.error(f"❌ Erreur lors du scan: {e}")
            results["status"] = "error"
            results["error"] = str(e)
            return results
    
    def _generate_sample_network_data(self) -> Dict[str, Any]:
        """Génère des données réseau d'exemple pour les tests"""
        import random
        
        return {
            "duration": random.uniform(0.1, 10.0),
            "protocol_type": random.choice(["tcp", "udp", "icmp"]),
            "service": random.choice(["http", "ftp", "smtp", "ssh"]),
            "flag": random.choice(["SF", "S0", "REJ"]),
            "src_bytes": random.randint(0, 10000),
            "dst_bytes": random.randint(0, 10000),
            "count": random.randint(1, 100),
            "srv_count": random.randint(1, 50)
        }
    
    def _generate_comprehensive_recommendations(self, scan_results: Dict[str, Any]) -> List[str]:
        """Génère des recommandations basées sur tous les résultats"""
        recommendations = []
        
        # Recommandations basées sur le scan web
        web_scan = scan_results.get("components", {}).get("web_scan", {})
        if web_scan.get("vulnerabilities"):
            for vuln in web_scan["vulnerabilities"]:
                if self.recommender:
                    vuln_type = vuln.get("name", "").lower()
                    if "content-security-policy" in vuln_type:
                        recs = self.recommender.get_recommendations("xss")
                        recommendations.extend(recs.get("recommendations", []))
                    elif "x-frame-options" in vuln_type:
                        recommendations.append("Configurer l'en-tête X-Frame-Options pour prévenir le clickjacking")
                    elif "strict-transport-security" in vuln_type:
                        recommendations.append("Activer HSTS pour sécuriser les connexions HTTPS")
        
        # Recommandations basées sur l'analyse réseau
        network_analysis = scan_results.get("components", {}).get("network_analysis", {})
        if network_analysis.get("is_attack"):
            recommendations.extend([
                "🚨 Trafic réseau suspect détecté - Investigation immédiate requise",
                "Analyser les logs réseau pour identifier la source",
                "Considérer le blocage temporaire du trafic suspect",
                "Renforcer la surveillance réseau"
            ])
        
        # Recommandations générales
        recommendations.extend([
            "Effectuer des scans de sécurité réguliers",
            "Maintenir tous les systèmes à jour",
            "Implémenter une politique de sécurité robuste",
            "Former les utilisateurs aux bonnes pratiques de sécurité"
        ])
        
        return list(set(recommendations))  # Supprimer les doublons
    
    def _generate_comprehensive_report(self, scan_results: Dict[str, Any]) -> str:
        """Génère un rapport complet"""
        if not self.report_generator:
            return "Générateur de rapports non disponible"
        
        # Utiliser le générateur de rapports existant pour le scan web
        web_scan = scan_results.get("components", {}).get("web_scan", {})
        if web_scan:
            base_report = self.report_generator.generate_text_report(web_scan, scan_results["target"])
        else:
            base_report = f"# Rapport de sécurité pour {scan_results['target']}\n\n"
        
        # Ajouter les autres analyses
        additional_sections = []
        
        # Section analyse réseau
        network_analysis = scan_results.get("components", {}).get("network_analysis", {})
        if network_analysis:
            additional_sections.append(f"""
## Analyse du Trafic Réseau

**Statut**: {'🚨 Menace détectée' if network_analysis.get('is_attack') else '✅ Trafic normal'}
**Type d'attaque**: {network_analysis.get('attack_type', 'Aucune')}
**Confiance**: {network_analysis.get('confidence', 'N/A')}
""")
        
        # Section recommandations
        if scan_results.get("recommendations"):
            additional_sections.append(f"""
## Recommandations Prioritaires

{chr(10).join(f"• {rec}" for rec in scan_results["recommendations"][:5])}
""")
        
        return base_report + "\n".join(additional_sections)
    
    def _generate_scan_summary(self, scan_results: Dict[str, Any]) -> Dict[str, Any]:
        """Génère un résumé du scan"""
        summary = {
            "total_vulnerabilities": 0,
            "severity_breakdown": {"high": 0, "medium": 0, "low": 0},
            "threats_detected": False,
            "components_scanned": len(scan_results.get("components", {})),
            "recommendations_count": len(scan_results.get("recommendations", []))
        }
        
        # Compter les vulnérabilités du scan web
        web_scan = scan_results.get("components", {}).get("web_scan", {})
        if web_scan.get("vulnerabilities"):
            summary["total_vulnerabilities"] = len(web_scan["vulnerabilities"])
            for vuln in web_scan["vulnerabilities"]:
                severity = vuln.get("severity", "low").lower()
                if severity in summary["severity_breakdown"]:
                    summary["severity_breakdown"][severity] += 1
        
        # Vérifier les menaces réseau
        network_analysis = scan_results.get("components", {}).get("network_analysis", {})
        if network_analysis.get("is_attack"):
            summary["threats_detected"] = True
        
        return summary
    
    async def quick_vulnerability_check(self, text_or_url: str) -> Dict[str, Any]:
        """Vérification rapide de vulnérabilité"""
        if not self.vulnerability_classifier:
            return {"error": "Classificateur non disponible", "status": "error"}
        
        try:
            result = self.vulnerability_classifier.classify(text_or_url)
            return {
                "status": "success",
                "vulnerability_type": result.get("label", "unknown"),
                "confidence": result.get("score", 0.0),
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {"error": str(e), "status": "error"}
    
    async def analyze_network_traffic(self, network_features: Dict[str, Any]) -> Dict[str, Any]:
        """Analyse du trafic réseau"""
        if not self.network_analyzer:
            return {"error": "Analyseur réseau non disponible", "status": "error"}
        
        try:
            result = self.network_analyzer.analyze(network_features)
            self.stats["network_analyses"] += 1
            
            if result.get("is_attack"):
                self.stats["threats_detected"] += 1
            
            return {
                "status": "success",
                "is_attack": result.get("is_attack", False),
                "attack_type": result.get("attack_type", "Normal"),
                "confidence": result.get("confidence", 0.0),
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {"error": str(e), "status": "error"}
    
    def get_agent_status(self) -> Dict[str, Any]:
        """Retourne le statut de l'agent"""
        return {
            "agent_name": "CompleteCybersecurityAgent",
            "version": "2.0.0",
            "is_initialized": self.is_initialized,
            "capabilities": self.capabilities,
            "stats": self.stats,
            "scan_history_count": len(self.scan_history),
            "timestamp": datetime.now().isoformat()
        }
    
    def get_recent_scans(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Retourne les scans récents"""
        return self.scan_history[-limit:] if self.scan_history else []

# Instance globale
cybersecurity_agent = CompleteCybersecurityAgent()

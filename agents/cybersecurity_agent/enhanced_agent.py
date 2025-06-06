
from typing import Dict, Any, List, Optional
import os
import json
import time
import asyncio
import threading
import requests
from datetime import datetime
from urllib.parse import urlparse
import re
from bs4 import BeautifulSoup
from agents.base_agent import BaseAgent
from utils.logger import get_logger

logger = get_logger("cybersecurity_agent_pentest")

# Configuration
SCAN_INTERVAL = 300  # 5 minutes
MAX_URLS_TO_SCAN = 10
HUGGINGFACE_USERNAME = os.getenv("HUGGINGFACE_USERNAME", "")
HUGGINGFACE_TOKEN = os.getenv("HUGGINGFACE_TOKEN", "")

class EnhancedCybersecurityAgent:
    """
    Agent de cybersécurité amélioré avec fonctionnalités de pentesting
    """
    
    def __init__(self):
        self.name = "enhanced_cybersecurity_agent"
        self.scan_results = {}
        self.last_scan_time = {}
        self.scanning = False
        self.scan_thread = None
        self.vulnerability_patterns = self._load_vulnerability_patterns()
        
        # Démarrer le thread de scan périodique
        self._start_periodic_scan()
    
    def _load_vulnerability_patterns(self) -> Dict[str, List[str]]:
        """Charger les patterns de vulnérabilités"""
        return {
            "xss": [
                r"<script>.*?</script>",
                r"javascript:",
                r"on(load|click|mouseover|error)=",
                r"alert\s*\(",
            ],
            "sql_injection": [
                r"'.*?OR.*?='",
                r"--.*?",
                r"#.*?",
                r"UNION.*?SELECT",
                r"DROP.*?TABLE",
            ],
            "open_redirect": [
                r"redirect=",
                r"url=",
                r"return_to=",
                r"next=",
            ],
            "file_inclusion": [
                r"include.*?",
                r"require.*?",
                r"file=",
                r"path=",
                r"\.\./",
            ],
            "information_disclosure": [
                r"phpinfo",
                r"\.git/",
                r"\.env",
                r"\.config",
                r"error in",
                r"warning in",
                r"stack trace",
                r"debug"
            ]
        }
    
    def _start_periodic_scan(self):
        """Démarrer le scan périodique"""
        def run_periodic_scan():
            while True:
                try:
                    # Vérifier s'il y a des URLs à scanner
                    if self.scan_results:
                        urls_to_scan = []
                        current_time = time.time()
                        
                        # Trouver les URLs qui doivent être scannées
                        for url, last_scan in self.last_scan_time.items():
                            if current_time - last_scan > SCAN_INTERVAL:
                                urls_to_scan.append(url)
                        
                        # Scanner les URLs
                        if urls_to_scan:
                            logger.info(f"🔍 Scan périodique de {len(urls_to_scan)} URLs")
                            for url in urls_to_scan[:MAX_URLS_TO_SCAN]:
                                self.scan_url(url)
                
                except Exception as e:
                    logger.error(f"❌ Erreur lors du scan périodique: {e}")
                
                # Attendre avant le prochain scan
                time.sleep(60)  # Vérifier toutes les minutes
        
        # Démarrer le thread
        self.scan_thread = threading.Thread(target=run_periodic_scan, daemon=True)
        self.scan_thread.start()
        logger.info("✅ Thread de scan périodique démarré")
    
    def scan_url(self, url: str, scan_type: str = "basic") -> Dict[str, Any]:
        """Scanner une URL pour détecter des vulnérabilités"""
        try:
            logger.info(f"🔍 Scan de {url} (type: {scan_type})")
            
            # Mettre à jour le temps de scan
            self.last_scan_time[url] = time.time()
            
            # Initialiser le résultat
            scan_id = f"scan_{int(time.time())}_{hash(url) % 10000}"
            result = {
                "scan_id": scan_id,
                "url": url,
                "scan_type": scan_type,
                "timestamp": datetime.now().isoformat(),
                "vulnerabilities": [],
                "status": "in_progress"
            }
            
            # Stocker le résultat initial
            self.scan_results[scan_id] = result
            
            # Effectuer le scan
            if scan_type == "basic":
                self._perform_basic_scan(url, scan_id)
            elif scan_type == "full":
                self._perform_full_scan(url, scan_id)
            else:
                self._perform_basic_scan(url, scan_id)
            
            # Mettre à jour le statut
            self.scan_results[scan_id]["status"] = "completed"
            
            # Calculer le niveau de risque
            self._calculate_risk_level(scan_id)
            
            return self.scan_results[scan_id]
            
        except Exception as e:
            logger.error(f"❌ Erreur lors du scan de {url}: {e}")
            
            # Créer un résultat d'erreur
            error_result = {
                "scan_id": f"error_{int(time.time())}",
                "url": url,
                "scan_type": scan_type,
                "timestamp": datetime.now().isoformat(),
                "status": "error",
                "error": str(e)
            }
            
            return error_result
    
    def _perform_basic_scan(self, url: str, scan_id: str):
        """Effectuer un scan basique"""
        try:
            # Récupérer la page
            response = requests.get(url, timeout=10, verify=False)
            content = response.text
            
            # Analyser les en-têtes
            self._analyze_headers(response.headers, scan_id)
            
            # Analyser le contenu
            self._analyze_content(content, scan_id)
            
            # Analyser les formulaires
            self._analyze_forms(content, url, scan_id)
            
        except Exception as e:
            logger.error(f"❌ Erreur lors du scan basique de {url}: {e}")
            self.scan_results[scan_id]["vulnerabilities"].append({
                "type": "error",
                "severity": "low",
                "description": f"Erreur lors du scan: {str(e)}",
                "location": url
            })
    
    def _perform_full_scan(self, url: str, scan_id: str):
        """Effectuer un scan complet"""
        try:
            # Effectuer d'abord un scan basique
            self._perform_basic_scan(url, scan_id)
            
            # Tester les vulnérabilités courantes
            self._test_common_vulnerabilities(url, scan_id)
            
        except Exception as e:
            logger.error(f"❌ Erreur lors du scan complet de {url}: {e}")
            self.scan_results[scan_id]["vulnerabilities"].append({
                "type": "error",
                "severity": "low",
                "description": f"Erreur lors du scan complet: {str(e)}",
                "location": url
            })
    
    def _analyze_headers(self, headers: Dict[str, str], scan_id: str):
        """Analyser les en-têtes HTTP"""
        # Vérifier les en-têtes de sécurité
        security_headers = {
            "Strict-Transport-Security": "L'en-tête HSTS est manquant",
            "Content-Security-Policy": "L'en-tête CSP est manquant",
            "X-Content-Type-Options": "L'en-tête X-Content-Type-Options est manquant",
            "X-Frame-Options": "L'en-tête X-Frame-Options est manquant",
            "X-XSS-Protection": "L'en-tête X-XSS-Protection est manquant"
        }
        
        for header, message in security_headers.items():
            if header not in headers:
                self.scan_results[scan_id]["vulnerabilities"].append({
                    "type": "missing_security_header",
                    "severity": "medium",
                    "description": message,
                    "location": "HTTP Headers"
                })
    
    def _analyze_content(self, content: str, scan_id: str, location: str = None):
        """Analyser le contenu HTML"""
        # Vérifier les patterns de vulnérabilités
        for vuln_type, patterns in self.vulnerability_patterns.items():
            for pattern in patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                
                if matches:
                    severity = "high" if vuln_type in ["xss", "sql_injection"] else "medium"
                    
                    self.scan_results[scan_id]["vulnerabilities"].append({
                        "type": vuln_type,
                        "severity": severity,
                        "description": f"Potentielle vulnérabilité {vuln_type} détectée",
                        "location": location or "Page principale",
                        "evidence": matches[0] if matches else ""
                    })
    
    def _analyze_forms(self, content: str, base_url: str, scan_id: str):
        """Analyser les formulaires"""
        try:
            soup = BeautifulSoup(content, 'html.parser')
            forms = soup.find_all('form')
            
            for form in forms:
                # Vérifier la méthode
                method = form.get('method', '').lower()
                
                if method == 'get':
                    self.scan_results[scan_id]["vulnerabilities"].append({
                        "type": "insecure_form",
                        "severity": "low",
                        "description": "Formulaire utilisant la méthode GET",
                        "location": form.get('action', base_url)
                    })
                
                # Vérifier les champs sensibles
                password_fields = form.find_all('input', {'type': 'password'})
                
                if password_fields and not form.get('action', '').startswith('https://'):
                    self.scan_results[scan_id]["vulnerabilities"].append({
                        "type": "insecure_form",
                        "severity": "high",
                        "description": "Formulaire avec mot de passe sans HTTPS",
                        "location": form.get('action', base_url)
                    })
        except Exception as e:
            logger.error(f"❌ Erreur lors de l'analyse des formulaires: {e}")
    
    def _test_common_vulnerabilities(self, url: str, scan_id: str):
        """Tester les vulnérabilités courantes"""
        # Test de XSS réfléchi
        xss_payloads = [
            "<script>alert(1)</script>",
            "';alert(1);'",
            '"><script>alert(1)</script>'
        ]
        
        for payload in xss_payloads:
            try:
                # Construire l'URL avec le payload
                test_url = f"{url}?q={payload}"
                
                # Envoyer la requête
                response = requests.get(test_url, timeout=5, verify=False)
                
                # Vérifier si le payload est réfléchi
                if payload in response.text:
                    self.scan_results[scan_id]["vulnerabilities"].append({
                        "type": "reflected_xss",
                        "severity": "high",
                        "description": "XSS réfléchi potentiel détecté",
                        "location": test_url,
                        "evidence": payload
                    })
                    
                    # Un seul test positif suffit
                    break
                    
            except Exception as e:
                logger.error(f"❌ Erreur lors du test XSS sur {url}: {e}")
    
    def _calculate_risk_level(self, scan_id: str):
        """Calculer le niveau de risque global"""
        vulnerabilities = self.scan_results[scan_id]["vulnerabilities"]
        
        # Compter les vulnérabilités par sévérité
        severity_counts = {"high": 0, "medium": 0, "low": 0}
        
        for vuln in vulnerabilities:
            severity = vuln.get("severity", "low")
            severity_counts[severity] += 1
        
        # Calculer le niveau de risque
        if severity_counts["high"] > 0:
            risk_level = "high"
        elif severity_counts["medium"] > 0:
            risk_level = "medium"
        elif severity_counts["low"] > 0:
            risk_level = "low"
        else:
            risk_level = "info"
        
        # Mettre à jour le résultat
        self.scan_results[scan_id]["risk_level"] = risk_level
        self.scan_results[scan_id]["severity_counts"] = severity_counts
    
    async def process_message(self, message: str, session_id: str = None) -> str:
        """Traiter un message utilisateur"""
        try:
            # Extraire les URLs du message
            urls = re.findall(r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+', message)
            
            if urls:
                # Scanner la première URL
                result = self.scan_url(urls[0])
                
                # Construire la réponse
                response = f"J'ai scanné {urls[0]}.\n\n"
                
                if result.get("status") == "completed":
                    vulnerabilities = result.get("vulnerabilities", [])
                    risk_level = result.get("risk_level", "info")
                    
                    response += f"Niveau de risque: {risk_level.upper()}\n"
                    response += f"Vulnérabilités détectées: {len(vulnerabilities)}\n\n"
                    
                    if vulnerabilities:
                        response += "Principales vulnérabilités:\n"
                        
                        # Afficher les 5 premières vulnérabilités
                        for i, vuln in enumerate(vulnerabilities[:5]):
                            response += f"{i+1}. {vuln.get('type', 'unknown')} ({vuln.get('severity', 'low')}): {vuln.get('description', '')}\n"
                    else:
                        response += "Aucune vulnérabilité détectée.\n"
                    
                    response += f"\nID du scan: {result.get('scan_id', 'unknown')}"
                else:
                    response += f"Erreur lors du scan: {result.get('error', 'unknown')}"
                
                return response
            else:
                # Analyser le message pour comprendre l'intention
                if "scan" in message.lower() or "sécurité" in message.lower() or "vulnérabilité" in message.lower():
                    return "Veuillez fournir une URL à scanner. Par exemple: https://example.com"
                else:
                    return "Je suis l'agent de cybersécurité. Je peux scanner des sites web pour détecter des vulnérabilités. Envoyez-moi une URL pour commencer."
            
        except Exception as e:
            logger.error(f"❌ Erreur lors du traitement du message: {e}")
            return f"Je suis désolé, j'ai rencontré une erreur technique. Veuillez réessayer."
    
    async def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Traiter une requête générique"""
        try:
            message = request.get("message", "")
            session_id = request.get("session_id")
            
            response = await self.process_message(message, session_id)
            
            return {
                "response": response,
                "status": "success",
                "agent": self.name,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"❌ Erreur lors du traitement de la requête: {e}")
            return {
                "error": str(e),
                "status": "error",
                "agent": self.name,
                "timestamp": datetime.now().isoformat()
            }

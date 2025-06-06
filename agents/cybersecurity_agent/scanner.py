"""
Scanner web pour l'agent de cybersécurité.
"""
import logging
from typing import Dict, Any, List, Optional
import requests
import asyncio
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

class WebScanner:
    """
    Scanner web qui effectue des tests de sécurité sur les sites web.
    """
    
    def __init__(self, zap_api_key: str = "", zap_proxy: str = "localhost:8080"):
        """
        Initialise le scanner web.
        
        Args:
            zap_api_key: Clé API pour OWASP ZAP
            zap_proxy: Adresse du proxy ZAP
        """
        self.zap_api_key = zap_api_key
        self.zap_proxy = zap_proxy
        self.zap_available = self._check_zap_availability()
    
    def _check_zap_availability(self) -> bool:
        """
        Vérifie si OWASP ZAP est disponible.
        
        Returns:
            True si ZAP est disponible, False sinon
        """
        if not self.zap_api_key:
            logger.warning("No ZAP API key provided")
            return False
        
        try:
            # Tenter de se connecter à l'API ZAP
            zap_url = f"http://{self.zap_proxy}/JSON/core/view/version/"
            response = requests.get(
                zap_url,
                params={"apikey": self.zap_api_key},
                timeout=5
            )
            
            if response.status_code == 200:
                logger.info("OWASP ZAP is available")
                return True
            else:
                logger.warning(f"OWASP ZAP returned status code {response.status_code}")
                return False
        
        except Exception as e:
            logger.warning(f"OWASP ZAP is not available: {str(e)}")
            return False
    
    async def scan_url(self, url: str) -> Dict[str, Any]:
        """
        Effectue un scan de sécurité sur une URL.
        
        Args:
            url: URL à scanner
            
        Returns:
            Résultats du scan
        """
        # Vérifier que l'URL est valide
        try:
            parsed_url = urlparse(url)
            if not parsed_url.scheme or not parsed_url.netloc:
                return {
                    "success": False,
                    "error": "URL invalide",
                    "vulnerabilities": []
                }
        except Exception:
            return {
                "success": False,
                "error": "URL invalide",
                "vulnerabilities": []
            }
        
        # Si ZAP est disponible, utiliser ZAP pour le scan
        if self.zap_available:
            return await self._scan_with_zap(url)
        
        # Sinon, effectuer un scan basique
        return await self._basic_scan(url)
    
    async def _scan_with_zap(self, url: str) -> Dict[str, Any]:
        """
        Effectue un scan avec OWASP ZAP.
        
        Args:
            url: URL à scanner
            
        Returns:
            Résultats du scan
        """
        # Cette méthode serait implémentée pour interagir avec l'API ZAP
        # Pour cet exemple, nous simulons un scan
        
        # Simuler un délai pour le scan
        await asyncio.sleep(5)
        
        # Simuler des résultats
        return {
            "success": True,
            "scan_id": "zap_scan_123",
            "vulnerabilities": [
                {
                    "name": "Absence d'en-tête X-Content-Type-Options",
                    "severity": "low",
                    "description": "L'en-tête X-Content-Type-Options n'est pas défini."
                },
                {
                    "name": "Absence d'en-tête Content-Security-Policy",
                    "severity": "medium",
                    "description": "L'en-tête Content-Security-Policy n'est pas défini."
                }
            ]
        }
    
    async def _basic_scan(self, url: str) -> Dict[str, Any]:
        """
        Effectue un scan basique sans OWASP ZAP.
        
        Args:
            url: URL à scanner
            
        Returns:
            Résultats du scan
        """
        try:
            # Effectuer une requête GET sur l'URL
            response = requests.get(url, timeout=10)
            
            # Analyser les en-têtes de sécurité
            headers = response.headers
            vulnerabilities = []
            
            # Vérifier l'en-tête X-Content-Type-Options
            if "X-Content-Type-Options" not in headers:
                vulnerabilities.append({
                    "name": "Absence d'en-tête X-Content-Type-Options",
                    "severity": "low",
                    "description": "L'en-tête X-Content-Type-Options n'est pas défini, ce qui peut permettre des attaques MIME sniffing."
                })
            
            # Vérifier l'en-tête Content-Security-Policy
            if "Content-Security-Policy" not in headers:
                vulnerabilities.append({
                    "name": "Absence d'en-tête Content-Security-Policy",
                    "severity": "medium",
                    "description": "L'en-tête Content-Security-Policy n'est pas défini, ce qui peut permettre des attaques XSS."
                })
            
            # Vérifier l'en-tête X-Frame-Options
            if "X-Frame-Options" not in headers:
                vulnerabilities.append({
                    "name": "Absence d'en-tête X-Frame-Options",
                    "severity": "medium",
                    "description": "L'en-tête X-Frame-Options n'est pas défini, ce qui peut permettre des attaques de clickjacking."
                })
            
            # Vérifier l'en-tête Strict-Transport-Security
            if "Strict-Transport-Security" not in headers and url.startswith("https"):
                vulnerabilities.append({
                    "name": "Absence d'en-tête Strict-Transport-Security",
                    "severity": "medium",
                    "description": "L'en-tête Strict-Transport-Security n'est pas défini, ce qui peut permettre des attaques de downgrade HTTPS."
                })
            
            return {
                "success": True,
                "scan_id": "basic_scan_123",
                "vulnerabilities": vulnerabilities
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "vulnerabilities": []
            }

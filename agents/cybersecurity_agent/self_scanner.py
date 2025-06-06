import asyncio
import logging
import requests
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from datetime import datetime

# Configuration du logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SelfScanningRobot:
    """Robot qui scanne la plateforme NextGen AI Assistant elle-même"""
    
    def __init__(self, base_url="http://localhost:3000"):
        self.base_url = base_url
        self.visited_urls = set()
        self.vulnerabilities = []
        self.pages = []
        self.is_scanning = False
        self.current_page = None
        self.scan_results = {
            "start_time": None,
            "end_time": None,
            "pages_scanned": 0,
            "vulnerabilities_found": 0,
            "status": "idle"
        }
        logger.info(f"Robot Guardian initialisé pour scanner: {self.base_url}")
    
    async def start_scan(self, scan_mode="passive"):
        """Démarre le scan de la plateforme"""
        if self.is_scanning:
            logger.warning("Un scan est déjà en cours")
            return False
        
        self.is_scanning = True
        self.scan_results["start_time"] = datetime.now().isoformat()
        self.scan_results["status"] = "scanning"
        logger.info(f"Démarrage du scan en mode {scan_mode}")
        
        try:
            # Découverte des pages
            await self.discover_pages()
            
            # Scan de chaque page
            for page in self.pages:
                self.current_page = page
                logger.info(f"Scan de la page: {page}")
                
                # Simulation de marche du robot
                await asyncio.sleep(1)  # Simule le déplacement
                
                # Analyse de la page
                await self.analyze_page(page, scan_mode)
                
                self.scan_results["pages_scanned"] += 1
            
            # Scan terminé
            self.scan_results["end_time"] = datetime.now().isoformat()
            self.scan_results["status"] = "completed"
            self.scan_results["vulnerabilities_found"] = len(self.vulnerabilities)
            logger.info(f"Scan terminé. {len(self.vulnerabilities)} vulnérabilités trouvées.")
            
            return {
                "scan_results": self.scan_results,
                "vulnerabilities": self.vulnerabilities
            }
            
        except Exception as e:
            logger.error(f"Erreur pendant le scan: {str(e)}")
            self.scan_results["status"] = "error"
            return False
        finally:
            self.is_scanning = False
    
    async def discover_pages(self):
        """Découvre les pages de la plateforme"""
        try:
            response = requests.get(self.base_url)
            if response.status_code != 200:
                logger.error(f"Impossible d'accéder à {self.base_url}: {response.status_code}")
                return
            
            # Ajouter la page d'accueil
            self.pages.append(self.base_url)
            self.visited_urls.add(self.base_url)
            
            # Extraire les liens
            soup = BeautifulSoup(response.text, 'html.parser')
            links = soup.find_all('a', href=True)
            
            # Ajouter les routes connues de l'application
            known_routes = [
                "/", 
                "/api/chat",
                "/api/health",
                "/dashboard",
                "/settings",
                "/profile",
                "/login",
                "/register"
            ]
            
            # Ajouter les liens trouvés
            for link in links:
                href = link['href']
                if href.startswith('/') and not href.startswith('//'):
                    full_url = urljoin(self.base_url, href)
                    if full_url not in self.visited_urls:
                        self.pages.append(full_url)
                        self.visited_urls.add(full_url)
            
            # Ajouter les routes connues
            for route in known_routes:
                full_url = urljoin(self.base_url, route)
                if full_url not in self.visited_urls:
                    self.pages.append(full_url)
                    self.visited_urls.add(full_url)
            
            logger.info(f"Découverte terminée: {len(self.pages)} pages trouvées")
            
        except Exception as e:
            logger.error(f"Erreur pendant la découverte des pages: {str(e)}")
    
    async def analyze_page(self, url, scan_mode):
        """Analyse une page pour détecter des vulnérabilités"""
        try:
            response = requests.get(url)
            if response.status_code != 200:
                logger.warning(f"Impossible d'accéder à {url}: {response.status_code}")
                return
            
            # Analyse passive (observation)
            self._check_headers(url, response)
            self._check_content_security(url, response)
            
            # Analyse active (tests d'intrusion) si activée
            if scan_mode == "active":
                await self._test_xss_vulnerabilities(url)
                await self._test_open_redirects(url)
                await self._test_api_security(url)
            
        except Exception as e:
            logger.error(f"Erreur pendant l'analyse de {url}: {str(e)}")
    
    def _check_headers(self, url, response):
        """Vérifie les en-têtes de sécurité"""
        security_headers = {
            'Strict-Transport-Security': 'HSTS non configuré',
            'Content-Security-Policy': 'CSP non configuré',
            'X-Content-Type-Options': 'X-Content-Type-Options non configuré',
            'X-Frame-Options': 'X-Frame-Options non configuré',
            'X-XSS-Protection': 'X-XSS-Protection non configuré'
        }
        
        for header, message in security_headers.items():
            if header not in response.headers:
                self._add_vulnerability(
                    url=url,
                    type="En-tête de sécurité manquant",
                    description=message,
                    severity="medium"
                )
    
    def _check_content_security(self, url, response):
        """Vérifie la sécurité du contenu"""
        # Vérifier si des scripts inline sont utilisés
        soup = BeautifulSoup(response.text, 'html.parser')
        inline_scripts = soup.find_all('script', src=None)
        
        if inline_scripts and len(inline_scripts) > 0:
            self._add_vulnerability(
                url=url,
                type="Scripts inline",
                description="Des scripts inline sont utilisés, ce qui peut être risqué sans CSP strict",
                severity="low"
            )
    
    async def _test_xss_vulnerabilities(self, url):
        """Teste les vulnérabilités XSS (simulation)"""
        # Simulation de test XSS
        parsed_url = urlparse(url)
        if parsed_url.path.endswith('/api/chat') or 'chat' in parsed_url.path:
            self._add_vulnerability(
                url=url,
                type="Potentiel XSS",
                description="L'API de chat pourrait être vulnérable aux attaques XSS si l'entrée utilisateur n'est pas correctement échappée",
                severity="high",
                payload="<script>alert('XSS')</script>"
            )
    
    async def _test_open_redirects(self, url):
        """Teste les redirections ouvertes (simulation)"""
        # Simulation de test de redirection
        if 'login' in url or 'redirect' in url:
            self._add_vulnerability(
                url=url,
                type="Redirection ouverte",
                description="La page pourrait être vulnérable aux redirections ouvertes",
                severity="medium",
                payload="?redirect=https://attacker.com"
            )
    
    async def _test_api_security(self, url):
        """Teste la sécurité des API (simulation)"""
        if '/api/' in url:
            self._add_vulnerability(
                url=url,
                type="Sécurité API",
                description="L'API pourrait ne pas implémenter de limitation de débit (rate limiting)",
                severity="medium"
            )
    
    def _add_vulnerability(self, url, type, description, severity, payload=None):
        """Ajoute une vulnérabilité détectée"""
        vuln = {
            "id": f"VULN-{len(self.vulnerabilities) + 1}",
            "url": url,
            "type": type,
            "description": description,
            "severity": severity,
            "timestamp": datetime.now().isoformat()
        }
        
        if payload:
            vuln["payload"] = payload
        
        self.vulnerabilities.append(vuln)
        logger.warning(f"Vulnérabilité détectée: {type} sur {url}")
    
    def get_status(self):
        """Retourne le statut actuel du robot"""
        return {
            "is_scanning": self.is_scanning,
            "current_page": self.current_page,
            "scan_results": self.scan_results,
            "vulnerabilities_count": len(self.vulnerabilities)
        }
    
    async def simulate_attack(self, attack_type="xss"):
        """Simule une attaque sur la plateforme"""
        attack_types = {
            "xss": {
                "name": "Cross-Site Scripting (XSS)",
                "description": "Tentative d'injection de script malveillant",
                "severity": "high"
            },
            "sqli": {
                "name": "SQL Injection",
                "description": "Tentative d'injection SQL pour accéder à la base de données",
                "severity": "critical"
            },
            "bruteforce": {
                "name": "Brute Force",
                "description": "Tentative de connexion par force brute",
                "severity": "medium"
            }
        }
        
        if attack_type not in attack_types:
            logger.error(f"Type d'attaque inconnu: {attack_type}")
            return False
        
        attack = attack_types[attack_type]
        logger.warning(f"SIMULATION D'ATTAQUE: {attack['name']} - {attack['description']}")
        
        # Simuler une défense
        await asyncio.sleep(2)  # Temps de réaction
        
        defense_result = {
            "attack": attack['name'],
            "timestamp": datetime.now().isoformat(),
            "blocked": True,
            "details": f"Attaque {attack['name']} bloquée par le Robot Guardian"
        }
        
        logger.info(f"Attaque {attack['name']} bloquée avec succès")
        return defense_result

# Exemple d'utilisation
async def main():
    robot = SelfScanningRobot()
    results = await robot.start_scan(scan_mode="active")
    print(f"Scan terminé avec {len(robot.vulnerabilities)} vulnérabilités")
    
    # Simuler une attaque
    defense = await robot.simulate_attack("xss")
    print(f"Défense: {defense}")

if __name__ == "__main__":
    asyncio.run(main())

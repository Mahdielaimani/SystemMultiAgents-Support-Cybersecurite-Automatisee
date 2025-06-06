"""
Intégration avec crawl4ai pour l'extraction de contenu web.
https://github.com/unclecode/crawl4ai
"""
import logging
import os
import json
import subprocess
from typing import Dict, Any, List, Optional, Union
import tempfile
import shutil

logger = logging.getLogger(__name__)

class Crawl4AIIntegration:
    """
    Intégration avec l'outil crawl4ai pour extraire du contenu web
    et l'ajouter à la base de connaissances.
    """
    
    def __init__(self, output_dir: str = "data/crawled"):
        """
        Initialise l'intégration avec crawl4ai.
        
        Args:
            output_dir: Répertoire de sortie pour les données extraites
        """
        self.output_dir = output_dir
        self._ensure_output_dir()
        self._check_crawl4ai_installation()
    
    def _ensure_output_dir(self):
        """Assure que le répertoire de sortie existe."""
        os.makedirs(self.output_dir, exist_ok=True)
        logger.info(f"Output directory ensured: {self.output_dir}")
    
    def _check_crawl4ai_installation(self):
        """Vérifie si crawl4ai est installé."""
        try:
            result = subprocess.run(
                ["pip", "show", "crawl4ai"],
                capture_output=True,
                text=True,
                check=False
            )
            
            if result.returncode != 0:
                logger.warning("crawl4ai is not installed. Please install it with: pip install crawl4ai")
                logger.warning("You can find more information at: https://github.com/unclecode/crawl4ai")
                return
            
            logger.info("crawl4ai is installed")
        except Exception as e:
            logger.error(f"Error checking crawl4ai installation: {str(e)}")
    
    async def crawl_website(self, url: str, depth: int = 2, max_pages: int = 50) -> Dict[str, Any]:
        """
        Extrait le contenu d'un site web en utilisant crawl4ai.
        
        Args:
            url: URL du site web à extraire
            depth: Profondeur maximale de crawl
            max_pages: Nombre maximum de pages à extraire
            
        Returns:
            Résultats de l'extraction
        """
        try:
            # Créer un répertoire temporaire pour les résultats
            temp_dir = tempfile.mkdtemp()
            output_file = os.path.join(temp_dir, "crawl_results.json")
            
            # Construire la commande crawl4ai
            cmd = [
                "crawl4ai",
                "crawl",
                "--url", url,
                "--depth", str(depth),
                "--max-pages", str(max_pages),
                "--output", output_file,
                "--format", "json"
            ]
            
            # Exécuter la commande
            logger.info(f"Starting crawl4ai for {url} with depth {depth} and max_pages {max_pages}")
            process = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=False
            )
            
            if process.returncode != 0:
                logger.error(f"crawl4ai failed: {process.stderr}")
                return {"success": False, "error": process.stderr}
            
            # Lire les résultats
            if os.path.exists(output_file):
                with open(output_file, 'r', encoding='utf-8') as f:
                    results = json.load(f)
                
                # Copier les résultats dans le répertoire de sortie
                site_dir = os.path.join(self.output_dir, self._get_domain_from_url(url))
                os.makedirs(site_dir, exist_ok=True)
                
                result_file = os.path.join(site_dir, f"crawl_{int(time.time())}.json")
                shutil.copy(output_file, result_file)
                
                # Nettoyer le répertoire temporaire
                shutil.rmtree(temp_dir)
                
                return {
                    "success": True,
                    "pages_crawled": len(results),
                    "output_file": result_file,
                    "results": results
                }
            else:
                logger.error(f"Output file not found: {output_file}")
                return {"success": False, "error": "Output file not found"}
        
        except Exception as e:
            logger.error(f"Error crawling website: {str(e)}")
            return {"success": False, "error": str(e)}
        finally:
            # S'assurer que le répertoire temporaire est supprimé
            if 'temp_dir' in locals() and os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
    
    def _get_domain_from_url(self, url: str) -> str:
        """
        Extrait le domaine d'une URL.
        
        Args:
            url: URL à analyser
            
        Returns:
            Domaine extrait
        """
        from urllib.parse import urlparse
        parsed_url = urlparse(url)
        return parsed_url.netloc.replace(".", "_")
    
    async def extract_for_security_analysis(self, url: str) -> Dict[str, Any]:
        """
        Extrait le contenu d'un site web pour une analyse de sécurité.
        
        Args:
            url: URL du site web à analyser
            
        Returns:
            Résultats de l'analyse
        """
        # Extraire le contenu avec une profondeur limitée
        crawl_results = await self.crawl_website(url, depth=1, max_pages=10)
        
        if not crawl_results.get("success", False):
            return crawl_results
        
        # Analyser les résultats pour des problèmes de sécurité
        security_issues = []
        
        for page in crawl_results.get("results", []):
            # Vérifier les formulaires non sécurisés
            if "http:" in url and "<form" in page.get("content", ""):
                security_issues.append({
                    "type": "insecure_form",
                    "url": page.get("url", ""),
                    "description": "Formulaire non sécurisé détecté sur une page HTTP"
                })
            
            # Vérifier les scripts externes
            if "<script src=\"http:" in page.get("content", ""):
                security_issues.append({
                    "type": "insecure_script",
                    "url": page.get("url", ""),
                    "description": "Script externe non sécurisé détecté"
                })
        
        return {
            "success": True,
            "url": url,
            "security_issues": security_issues,
            "pages_analyzed": len(crawl_results.get("results", [])),
            "raw_results": crawl_results
        }
    
    async def extract_for_knowledge_base(self, url: str, depth: int = 3, max_pages: int = 100) -> Dict[str, Any]:
        """
        Extrait le contenu d'un site web pour l'ajouter à la base de connaissances.
        
        Args:
            url: URL du site web à extraire
            depth: Profondeur maximale de crawl
            max_pages: Nombre maximum de pages à extraire
            
        Returns:
            Résultats de l'extraction
        """
        # Extraire le contenu avec une profondeur plus importante
        crawl_results = await self.crawl_website(url, depth=depth, max_pages=max_pages)
        
        if not crawl_results.get("success", False):
            return crawl_results
        
        # Préparer les documents pour la base de connaissances
        documents = []
        
        for page in crawl_results.get("results", []):
            # Extraire le contenu textuel
            content = page.get("content", "")
            title = page.get("title", "")
            page_url = page.get("url", "")
            
            # Créer un document
            document = {
                "content": content,
                "metadata": {
                    "source": page_url,
                    "title": title,
                    "crawled_at": datetime.now().isoformat()
                }
            }
            
            documents.append(document)
        
        return {
            "success": True,
            "url": url,
            "documents": documents,
            "pages_extracted": len(documents),
            "raw_results": crawl_results
        }

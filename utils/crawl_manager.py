"""
Module pour gérer le crawling de sites web avec crawl4ai.
"""
import os
import json
import subprocess
from typing import List, Dict, Any, Optional, Union
import requests

from config.logging_config import get_logger
from config.settings import settings

logger = get_logger("crawl_manager")

class Crawl4AIManager:
    """
    Gestionnaire pour l'outil crawl4ai.
    
    Cette classe permet d'utiliser crawl4ai pour extraire des informations
    de sites web et les préparer pour l'ingestion dans la base de connaissances.
    """
    
    def __init__(self, output_dir: str = "data/crawled_data"):
        """
        Initialise le gestionnaire crawl4ai.
        
        Args:
            output_dir: Répertoire de sortie pour les données crawlées
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        # Vérifier si crawl4ai est installé
        try:
            subprocess.run(["crawl4ai", "--version"], capture_output=True, text=True)
            self.is_installed = True
            logger.info("crawl4ai est installé")
        except FileNotFoundError:
            self.is_installed = False
            logger.warning("crawl4ai n'est pas installé. Exécutez 'pip install crawl4ai'")
    
    def install_crawl4ai(self) -> bool:
        """
        Installe crawl4ai s'il n'est pas déjà installé.
        
        Returns:
            True si l'installation a réussi, False sinon
        """
        if self.is_installed:
            logger.info("crawl4ai est déjà installé")
            return True
        
        try:
            logger.info("Installation de crawl4ai...")
            subprocess.run(["pip", "install", "crawl4ai"], check=True)
            self.is_installed = True
            logger.info("crawl4ai a été installé avec succès")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Erreur lors de l'installation de crawl4ai: {e}")
            return False
    
    def crawl_url(self, url: str, depth: int = 2, output_format: str = "json") -> str:
        """
        Crawle une URL avec crawl4ai.
        
        Args:
            url: URL à crawler
            depth: Profondeur du crawling
            output_format: Format de sortie (json, md, txt)
            
        Returns:
            Chemin du fichier de sortie
        """
        if not self.is_installed:
            if not self.install_crawl4ai():
                logger.error("Impossible d'installer crawl4ai")
                return ""
        
        # Créer un nom de fichier basé sur l'URL
        import hashlib
        url_hash = hashlib.md5(url.encode()).hexdigest()[:10]
        output_file = os.path.join(self.output_dir, f"crawled_{url_hash}.{output_format}")
        
        try:
            logger.info(f"Crawling de {url} avec une profondeur de {depth}...")
            
            # Exécuter crawl4ai
            cmd = [
                "crawl4ai",
                "crawl",
                "--url", url,
                "--depth", str(depth),
                "--output", output_file,
                "--format", output_format
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info(f"Crawling terminé avec succès. Résultats enregistrés dans {output_file}")
                return output_file
            else:
                logger.error(f"Erreur lors du crawling: {result.stderr}")
                return ""
        except Exception as e:
            logger.error(f"Exception lors du crawling: {e}")
            return ""
    
    def crawl_multiple_urls(self, base_url: str, paths: List[str], depth: int = 1) -> List[str]:
        """
        Crawle plusieurs chemins d'un site web.
        
        Args:
            base_url: URL de base du site
            paths: Liste des chemins relatifs à crawler
            depth: Profondeur du crawling
            
        Returns:
            Liste des chemins des fichiers de sortie
        """
        output_files = []
        
        for path in paths:
            # Construire l'URL complète
            if path.startswith("http"):
                url = path
            else:
                # S'assurer que le chemin commence par /
                if not path.startswith("/"):
                    path = f"/{path}"
                url = f"{base_url.rstrip('/')}{path}"
            
            # Crawler l'URL
            output_file = self.crawl_url(url, depth)
            if output_file:
                output_files.append(output_file)
        
        return output_files
    
    def process_crawled_data(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Traite les données crawlées pour l'ingestion.
        
        Args:
            file_path: Chemin du fichier de données crawlées
            
        Returns:
            Liste de documents formatés pour l'ingestion
        """
        if not os.path.exists(file_path):
            logger.error(f"Le fichier {file_path} n'existe pas")
            return []
        
        documents = []
        
        try:
            # Déterminer le format du fichier
            _, ext = os.path.splitext(file_path)
            
            if ext == ".json":
                # Charger les données JSON
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                
                # Traiter les données selon la structure de crawl4ai
                if isinstance(data, list):
                    for item in data:
                        if "content" in item and "url" in item:
                            documents.append({
                                "text": item["content"],
                                "metadata": {
                                    "source": item["url"],
                                    "title": item.get("title", ""),
                                    "type": "crawled",
                                    "timestamp": item.get("timestamp", "")
                                }
                            })
                elif isinstance(data, dict):
                    if "pages" in data:
                        for page in data["pages"]:
                            if "content" in page and "url" in page:
                                documents.append({
                                    "text": page["content"],
                                    "metadata": {
                                        "source": page["url"],
                                        "title": page.get("title", ""),
                                        "type": "crawled",
                                        "timestamp": page.get("timestamp", "")
                                    }
                                })
            elif ext == ".md" or ext == ".txt":
                # Charger le contenu du fichier texte
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                
                # Créer un document unique
                documents.append({
                    "text": content,
                    "metadata": {
                        "source": file_path,
                        "title": os.path.basename(file_path),
                        "type": "crawled",
                        "timestamp": str(os.path.getmtime(file_path))
                    }
                })
            
            logger.info(f"Traité {len(documents)} documents depuis {file_path}")
            return documents
        except Exception as e:
            logger.error(f"Erreur lors du traitement de {file_path}: {e}")
            return []

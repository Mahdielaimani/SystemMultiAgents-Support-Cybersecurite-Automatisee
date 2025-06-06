"""
Script pour ingérer toutes les données dans la base de connaissances.
"""
import os
import json
from typing import List, Dict, Any

from config.logging_config import get_logger
from data.vector_db.chroma_manager import ChromaManager
from utils.crawl_manager import Crawl4AIManager
from agents.support_agent.embedding import split_documents
from langchain_core.documents import Document

logger = get_logger("data_ingestion")

def load_metadata(file_path: str = "data/metadata/company_info.json") -> List[Dict[str, Any]]:
    """
    Charge les métadonnées de l'entreprise.
    
    Args:
        file_path: Chemin du fichier de métadonnées
        
    Returns:
        Liste de documents formatés pour l'ingestion
    """
    if not os.path.exists(file_path):
        logger.error(f"Le fichier {file_path} n'existe pas")
        return []
    
    documents = []
    
    try:
        # Charger les données JSON
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        # Traiter les informations de l'entreprise
        if "company" in data:
            company_info = data["company"]
            company_text = f"""
            # {company_info.get('name', 'Entreprise')}
            
            {company_info.get('description', '')}
            
            - Fondée en: {company_info.get('founded', '')}
            - Siège social: {company_info.get('headquarters', '')}
            - Site web: {company_info.get('website', '')}
            """
            
            documents.append({
                "id": "company_info",
                "text": company_text,
                "metadata": {
                    "source": file_path,
                    "category": "company",
                    "type": "metadata"
                }
            })
        
        # Traiter les informations sur les produits
        if "products" in data:
            for i, product in enumerate(data["products"]):
                product_text = f"""
                # {product.get('name', f'Produit {i+1}')}
                
                {product.get('description', '')}
                
                ## Fonctionnalités
                
                {chr(10).join(['- ' + feature for feature in product.get('features', [])])}
                """
                
                documents.append({
                    "id": f"product_info_{i}",
                    "text": product_text,
                    "metadata": {
                        "source": file_path,
                        "category": "product",
                        "product_name": product.get('name', ''),
                        "type": "metadata"
                    }
                })
        
        # Traiter les informations de support
        if "support" in data:
            support_info = data["support"]
            support_text = f"""
            # Support
            
            - Email: {support_info.get('email', '')}
            - Téléphone: {support_info.get('phone', '')}
            - Heures d'ouverture: {support_info.get('hours', '')}
            - FAQ: {support_info.get('faq_url', '')}
            - Documentation: {support_info.get('documentation_url', '')}
            """
            
            documents.append({
                "id": "support_info",
                "text": support_text,
                "metadata": {
                    "source": file_path,
                    "category": "support",
                    "type": "metadata"
                }
            })
        
        # Traiter les problèmes courants
        if "common_issues" in data:
            for i, issue in enumerate(data["common_issues"]):
                issue_text = f"""
                # {issue.get('issue', f'Problème {i+1}')}
                
                {issue.get('solution', '')}
                """
                
                documents.append({
                    "id": f"common_issue_{i}",
                    "text": issue_text,
                    "metadata": {
                        "source": file_path,
                        "category": "faq",
                        "type": "metadata"
                    }
                })
        
        logger.info(f"Chargé {len(documents)} documents depuis les métadonnées")
        return documents
    except Exception as e:
        logger.error(f"Erreur lors du chargement des métadonnées: {e}")
        return []

def crawl_website(base_url: str, paths: List[str]) -> List[Dict[str, Any]]:
    """
    Crawle un site web et prépare les données pour l'ingestion.
    
    Args:
        base_url: URL de base du site
        paths: Liste des chemins à crawler
        
    Returns:
        Liste de documents formatés pour l'ingestion
    """
    documents = []
    
    # Initialiser le gestionnaire de crawling
    crawl_manager = Crawl4AIManager()
    
    # Crawler les URLs
    output_files = crawl_manager.crawl_multiple_urls(base_url, paths)
    
    # Traiter les données crawlées
    for file_path in output_files:
        docs = crawl_manager.process_crawled_data(file_path)
        documents.extend(docs)
    
    logger.info(f"Crawlé et traité {len(documents)} documents depuis {base_url}")
    return documents

def main():
    """
    Fonction principale pour ingérer toutes les données.
    """
    logger.info("Début de l'ingestion de toutes les données")
    
    # Charger les métadonnées
    metadata_docs = load_metadata()
    
    # Crawler le site web
    base_url = "https://netguardian.ai"  # Remplacer par l'URL réelle
    paths = ["/faq", "/contact", "/about", "/products", "/documentation"]
    crawled_docs = crawl_website(base_url, paths)
    
    # Combiner tous les documents
    all_docs = metadata_docs + crawled_docs
    
    if not all_docs:
        logger.error("Aucun document à ingérer")
        return
    
    # Initialiser le gestionnaire ChromaDB
    chroma_manager = ChromaManager()
    
    # Ajouter les documents à ChromaDB
    collection_name = "support_knowledge_base"
    success = chroma_manager.add_documents(collection_name, all_docs)
    
    if success:
        logger.info(f"Ingestion réussie : {len(all_docs)} documents ajoutés à {collection_name}")
    else:
        logger.error("Échec de l'ingestion")

if __name__ == "__main__":
    main()

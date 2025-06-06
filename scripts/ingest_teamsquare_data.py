"""
Script pour ingérer les données spécifiques à TeamSquare.
"""
import os
import json
import logging
import asyncio
from typing import Dict, Any

from config.logging_config import get_logger
from data.knowledge_extraction.teamsquare_extractor import TeamSquareKnowledgeExtractor
from data.vector_db.chroma_manager import ChromaManager
from agents.support_agent.bge_embeddings import BGEEmbeddings

logger = get_logger("teamsquare_ingestion")

async def ingest_teamsquare_data():
    """
    Ingère les données spécifiques à TeamSquare dans la base de connaissances.
    """
    logger.info("Début de l'ingestion des données TeamSquare")
    
    # Extraire les connaissances
    extractor = TeamSquareKnowledgeExtractor()
    knowledge_base = extractor.extract_all()
    
    # Sauvegarder la base de connaissances
    output_file = "data/knowledge_base/teamsquare_knowledge.json"
    success = extractor.save_knowledge_base(output_file)
    
    if not success:
        logger.error("Échec de la sauvegarde de la base de connaissances")
        return
    
    # Préparer les documents pour ChromaDB
    documents = []
    
    # Ajouter les informations sur l'entreprise
    company_info = knowledge_base["company"]
    company_text = f"""
    # {company_info['name']}
    
    {company_info['description']}
    
    Slogan: {company_info['slogan']}
    Score de satisfaction: {company_info['satisfaction_score']}
    Site web: {company_info['website']}
    
    ## Bureaux
    """
    
    for location in company_info["locations"]:
        company_text += f"- {location['city']}: {location['address']}, {location['postal_code']}, Tél: {location['phone']}\n"
    
    documents.append({
        "id": "company_info",
        "content": company_text,
        "metadata": {
            "source": "teamsquare_config",
            "category": "company",
            "type": "info"
        }
    })
    
    # Ajouter les services
    for i, service in enumerate(knowledge_base["services"]):
        service_text = f"""
        # {service['name']}
        
        {service['description']}
        
        ## Sous-services
        """
        
        for sub_service in service.get("sub_services", []):
            service_text += f"- {sub_service}\n"
        
        documents.append({
            "id": f"service_{i}",
            "content": service_text,
            "metadata": {
                "source": "teamsquare_config",
                "category": "service",
                "service_name": service['name'],
                "type": "info"
            }
        })
    
    # Ajouter la vision et les valeurs
    vision = knowledge_base["vision"]
    vision_text = f"""
    # Vision et Valeurs de TeamSquare
    
    ## Mission
    {vision['mission']}
    
    ## Valeurs
    """
    
    for value in vision["values"]:
        vision_text += f"- {value}\n"
    
    vision_text += f"\n## Approche\n{vision['approach']}"
    
    documents.append({
        "id": "vision_values",
        "content": vision_text,
        "metadata": {
            "source": "teamsquare_config",
            "category": "vision",
            "type": "info"
        }
    })
    
    # Ajouter les partenaires
    partners_text = "# Partenaires de TeamSquare\n\n"
    
    for partner in knowledge_base["partners"]:
        partners_text += f"## {partner['name']}\n"
        partners_text += f"Type: {partner['type']}\n"
        partners_text += f"Description: {partner['description']}\n\n"
    
    documents.append({
        "id": "partners",
        "content": partners_text,
        "metadata": {
            "source": "teamsquare_config",
            "category": "partners",
            "type": "info"
        }
    })
    
    # Ajouter la FAQ
    for i, faq_item in enumerate(knowledge_base.get("faq", [])):
        faq_text = f"""
        # {faq_item['question']}
        
        {faq_item['answer']}
        """
        
        documents.append({
            "id": f"faq_{i}",
            "content": faq_text,
            "metadata": {
                "source": "teamsquare_faq",
                "category": "faq",
                "question": faq_item['question'],
                "type": "faq"
            }
        })
    
    # Initialiser ChromaDB
    chroma_manager = ChromaManager(
        persist_directory="data/vector_db",
        embedding_model="BAAI/bge-large-en-v1.5"
    )
    
    # Ajouter les documents à ChromaDB
    collection_name = "teamsquare_knowledge"
    result = await chroma_manager.add_documents(collection_name, documents)
    
    if result.get("success", False):
        logger.info(f"Ingestion réussie : {len(documents)} documents ajoutés à {collection_name}")
    else:
        logger.error(f"Échec de l'ingestion dans ChromaDB: {result.get('error', 'Unknown error')}")
    
    logger.info("Fin de l'ingestion des données TeamSquare")

if __name__ == "__main__":
    asyncio.run(ingest_teamsquare_data())

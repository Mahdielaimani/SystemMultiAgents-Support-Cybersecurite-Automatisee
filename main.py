#!/usr/bin/env python3
"""
Point d'entrée principal pour le système NextGen-Agent.
"""
import asyncio
import logging
import argparse
import os
import sys
from dotenv import load_dotenv

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config.settings import load_settings
from core.system import NextGenSystem
from api.server import setup_api_routes
from utils.model_loader import ModelLoader

# Charger les variables d'environnement
load_dotenv()

# Configurer le logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('nextgen_agent.log')
    ]
)

logger = logging.getLogger(__name__)

async def main():
    """Fonction principale pour démarrer le système."""
    parser = argparse.ArgumentParser(description='NextGen-Agent System')
    parser.add_argument('--mode', type=str, default='api', choices=['api', 'cli', 'ui'],
                        help='Mode de fonctionnement (api, cli, ui)')
    parser.add_argument('--host', type=str, default='127.0.0.1',
                        help='Hôte pour le serveur API')
    parser.add_argument('--port', type=int, default=8000,
                        help='Port pour le serveur API')
    parser.add_argument('--check-models', action='store_true',
                        help='Vérifier la disponibilité des modèles')
    
    args = parser.parse_args()
    
    # Charger les paramètres
    settings = load_settings()
    
    # Vérifier les modèles si demandé
    if args.check_models:
        logger.info("Vérification des modèles...")
        model_loader = ModelLoader()
        
        try:
            # Vérifier le classificateur d'intentions
            try:
                intent_model, _, _ = model_loader.load_intent_classifier()
                logger.info("Classificateur d'intentions disponible.")
            except FileNotFoundError:
                logger.warning("Classificateur d'intentions non disponible.")
            
            # Vérifier le classificateur de vulnérabilités
            try:
                vuln_model, _, _ = model_loader.load_vulnerability_classifier()
                logger.info("Classificateur de vulnérabilités disponible.")
            except FileNotFoundError:
                logger.warning("Classificateur de vulnérabilités non disponible.")
            
            # Vérifier le modèle d'embeddings
            try:
                embedding_model = model_loader.load_embedding_model()
                logger.info("Modèle d'embeddings disponible.")
            except FileNotFoundError:
                logger.warning("Modèle d'embeddings non disponible.")
                
        except Exception as e:
            logger.error(f"Erreur lors de la vérification des modèles: {str(e)}")
    
    # Initialiser le système
    system = NextGenSystem(settings)
    await system.initialize_resources()
    logger.info("NextGen-Agent system initialized")
    
    try:
        if args.mode == 'api':
            # Mode API
            app = FastAPI(title="NextGen-Agent API", version="1.0.0")
            
            # Configurer CORS
            app.add_middleware(
                CORSMiddleware,
                allow_origins=["*"],
                allow_credentials=True,
                allow_methods=["*"],
                allow_headers=["*"],
            )
            
            # Configurer les routes API
            setup_api_routes(app, system)
            
            # Démarrer le serveur
            logger.info(f"Starting API server on {args.host}:{args.port}")
            uvicorn.run(app, host=args.host, port=args.port)
        
        elif args.mode == 'cli':
            # Mode CLI
            logger.info("Starting CLI mode")
            session_id = "cli_session"
            
            print("NextGen-Agent CLI")
            print("Tapez 'exit' pour quitter")
            
            while True:
                query = input("\nVous: ")
                if query.lower() == 'exit':
                    break
                
                response = await system.process_query(query, session_id)
                print(f"\nAssistant: {response['content']}")
        
        elif args.mode == 'ui':
            # Mode UI
            logger.info("Starting UI mode")
            # Logique pour démarrer l'interface utilisateur
            # ...
    
    except KeyboardInterrupt:
        logger.info("Shutting down...")
    finally:
        # Libérer les ressources
        await system.shutdown()
        logger.info("NextGen-Agent system shut down")

if __name__ == "__main__":
    asyncio.run(main())

"""
Configuration du système de logging pour NetGuardian.
"""
import logging
import os
import sys
from pathlib import Path
from typing import Optional

def setup_logging(log_level: Optional[str] = None) -> logging.Logger:
    """
    Configure le système de logging.
    
    Args:
        log_level: Niveau de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        
    Returns:
        Logger configuré
    """
    # Créer le répertoire de logs s'il n'existe pas
    log_dir = Path("./data/logs/app_logs")
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Déterminer le niveau de logging
    if log_level is None:
        log_level = os.getenv("LOG_LEVEL", "INFO")
    
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    
    # Configuration de base
    logging.basicConfig(
        level=numeric_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(log_dir / "netguardian.log")
        ]
    )
    
    # Créer et configurer le logger
    logger = logging.getLogger("netguardian")
    logger.setLevel(numeric_level)
    
    # Réduire le niveau de verbosité des loggers tiers
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("chromadb").setLevel(logging.WARNING)
    logging.getLogger("neo4j").setLevel(logging.WARNING)
    
    return logger

def get_logger(name: str) -> logging.Logger:
    """
    Obtient un logger pour un module spécifique.
    
    Args:
        name: Nom du module
        
    Returns:
        Logger configuré pour le module
    """
    return logging.getLogger(f"netguardian.{name}")

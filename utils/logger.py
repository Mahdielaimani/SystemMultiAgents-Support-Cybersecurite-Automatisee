"""
Module de logging pour NextGen-Agent.
Configuration de structlog pour un logging structuré.
"""
import os
import sys
import logging
from pathlib import Path
import structlog

# Configuration du répertoire de logs
LOG_DIR = os.getenv("LOG_DIR", "./logs")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

# Créer le répertoire de logs s'il n'existe pas
Path(LOG_DIR).mkdir(exist_ok=True, parents=True)

# Configuration de base du logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=getattr(logging, LOG_LEVEL),
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(os.path.join(LOG_DIR, "nextgen_agent.log"))
    ]
)

# Configuration de structlog
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

def get_logger(name):
    """
    Retourne un logger structuré pour le module spécifié.
    
    Args:
        name: Nom du module (généralement __name__)
        
    Returns:
        Logger structuré
    """
    return structlog.get_logger(name)

# Exporter le logger pour compatibilité avec les imports existants
logger = get_logger("nextgen_agent")

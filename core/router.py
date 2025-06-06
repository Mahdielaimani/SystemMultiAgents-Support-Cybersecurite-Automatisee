"""
Module de routage pour NextGen-Agent.
"""
from typing import Dict, List, Any, Optional
import random
from utils.logger import get_logger

logger = get_logger(__name__)

class Router:
    """
    Routeur pour diriger les requêtes vers les agents appropriés.
    Version simplifiée pour le démarrage initial.
    """
    
    def __init__(self):
        """Initialise le routeur."""
        self.agents = {
            "support": "SupportAgent",
            "security": "CybersecurityAgent",
            "general": "GeneralAgent"
        }
        logger.info("Router initialisé avec succès")
    
    async def route_request(self, agent_type: str, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Route une requête vers l'agent approprié.
        
        Args:
            agent_type: Type d'agent
            request: Requête à router
            
        Returns:
            Réponse de l'agent
        """
        if agent_type in self.agents:
            logger.info(f"Requête routée vers {agent_type}")
            # Simulation de réponse pour le moment
            return {
                "status": "success",
                "agent": agent_type,
                "response": f"Réponse simulée de l'agent {agent_type}",
                "request_id": random.randint(1000, 9999)
            }
        else:
            logger.warning(f"Agent {agent_type} non trouvé")
            return {
                "status": "error",
                "message": f"Agent {agent_type} non trouvé"
            }
    
    def get_available_agents(self) -> List[str]:
        """
        Retourne la liste des agents disponibles.
        
        Returns:
            Liste des agents disponibles
        """
        return list(self.agents.keys())
    
    def get_agent_info(self, agent_type: str) -> Optional[Dict[str, Any]]:
        """
        Retourne les informations sur un agent.
        
        Args:
            agent_type: Type d'agent
            
        Returns:
            Informations sur l'agent
        """
        if agent_type in self.agents:
            return {
                "name": agent_type,
                "class": self.agents[agent_type],
                "description": f"Agent {agent_type} pour NextGen-Agent"
            }
        return None

"""
Classe de base pour tous les agents.
"""
from typing import Dict, Any, Optional
from abc import ABC, abstractmethod
import uuid

class BaseAgent(ABC):
    """Classe de base pour tous les agents."""
    
    def __init__(self, name: str):
        self.name = name
        self.agent_id = str(uuid.uuid4())
        self.status = "initialized"
    
    @abstractmethod
    async def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Traite une requête."""
        pass
    
    def format_response(self, content: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """Formate une réponse standard."""
        return {
            "content": content,
            "agent": self.name,
            "agent_id": self.agent_id,
            "metadata": metadata or {},
            "timestamp": self._get_timestamp()
        }
    
    def _get_timestamp(self) -> str:
        """Retourne un timestamp ISO."""
        from datetime import datetime
        return datetime.now().isoformat()
    
    async def initialize(self):
        """Initialise l'agent."""
        self.status = "ready"
    
    async def shutdown(self):
        """Arrête l'agent."""
        self.status = "stopped"

"""
Model Context Protocol (MCP) implementation for agent communication.
"""
import asyncio
import json
import uuid
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class MCPMessageType(Enum):
    """Types de messages MCP."""
    REQUEST = "request"
    RESPONSE = "response"
    NOTIFICATION = "notification"
    ERROR = "error"

@dataclass
class MCPMessage:
    """Message MCP standard."""
    id: str
    type: MCPMessageType
    method: str
    params: Dict[str, Any]
    result: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None
    timestamp: Optional[str] = None

class MCPServer:
    """Serveur MCP pour la communication entre agents."""
    
    def __init__(self):
        self.handlers: Dict[str, Callable] = {}
        self.clients: Dict[str, Any] = {}
        self.running = False
        
    def register_handler(self, method: str, handler: Callable):
        """Enregistre un handler pour une méthode."""
        self.handlers[method] = handler
        logger.info(f"Handler enregistré pour méthode: {method}")
    
    def register_client(self, client_id: str, client: Any):
        """Enregistre un client (agent)."""
        self.clients[client_id] = client
        logger.info(f"Client enregistré: {client_id}")
    
    async def send_message(self, client_id: str, message: MCPMessage) -> MCPMessage:
        """Envoie un message à un client."""
        try:
            if client_id not in self.clients:
                raise ValueError(f"Client {client_id} non trouvé")
            
            # Traiter le message
            if message.method in self.handlers:
                handler = self.handlers[message.method]
                result = await handler(message.params)
                
                response = MCPMessage(
                    id=message.id,
                    type=MCPMessageType.RESPONSE,
                    method=message.method,
                    params={},
                    result=result
                )
                return response
            else:
                error_response = MCPMessage(
                    id=message.id,
                    type=MCPMessageType.ERROR,
                    method=message.method,
                    params={},
                    error={"code": -32601, "message": f"Méthode {message.method} non trouvée"}
                )
                return error_response
                
        except Exception as e:
            logger.error(f"Erreur lors de l'envoi du message: {e}")
            error_response = MCPMessage(
                id=message.id,
                type=MCPMessageType.ERROR,
                method=message.method,
                params={},
                error={"code": -32603, "message": str(e)}
            )
            return error_response

class MCPClient:
    """Client MCP pour les agents."""
    
    def __init__(self, client_id: str, server: MCPServer):
        self.client_id = client_id
        self.server = server
        self.server.register_client(client_id, self)
    
    async def call_method(self, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Appelle une méthode via MCP."""
        message = MCPMessage(
            id=str(uuid.uuid4()),
            type=MCPMessageType.REQUEST,
            method=method,
            params=params
        )
        
        response = await self.server.send_message(self.client_id, message)
        
        if response.error:
            raise Exception(f"Erreur MCP: {response.error}")
        
        return response.result or {}

# Instance globale du serveur MCP
mcp_server = MCPServer()

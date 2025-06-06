
from typing import Dict, Any, Optional
from agents.base_agent import BaseAgent
from utils.logger import logger

class SimpleSupportAgent(BaseAgent):
    """Agent de support simple sans OpenAI"""
    
    def __init__(self):
        super().__init__()
        self.name = "simple_support_agent"
        self.responses = {
            "teamsquare": "TeamSquare est une plateforme de collaboration d'équipe innovante.",
            "bonjour": "Bonjour ! Je suis votre assistant IA. Comment puis-je vous aider ?",
            "aide": "Je peux vous aider avec des questions sur TeamSquare et le support technique.",
            "default": "Je suis un assistant IA simple. Posez-moi des questions sur TeamSquare !"
        }
    
    async def process_message(self, message: str, session_id: str = None) -> str:
        """Traite un message sans OpenAI"""
        try:
            message_lower = message.lower()
            
            # Recherche de mots-clés
            for keyword, response in self.responses.items():
                if keyword in message_lower:
                    return response
            
            return self.responses["default"]
            
        except Exception as e:
            logger.error(f"Erreur: {e}")
            return "Désolé, une erreur s'est produite."
    
    async def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Traite une requête"""
        try:
            message = request.get("message", "")
            response = await self.process_message(message)
            
            return {
                "response": response,
                "status": "success",
                "agent": self.name
            }
        except Exception as e:
            return {"error": str(e), "status": "error"}

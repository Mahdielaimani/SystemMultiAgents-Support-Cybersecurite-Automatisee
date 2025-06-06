"""
Système central de coordination pour NextGen-Agent.
Orchestre les interactions entre les différents agents et composants.
"""
import logging
from typing import Dict, Any, List, Optional

from core.event_bus import EventBus
from core.router import IntentRouter
from core.memory import ConversationMemory
from agents.support_agent.agent import SupportAgent
from agents.cybersecurity_agent.agent import CybersecurityAgent
from config.settings import Settings

logger = logging.getLogger(__name__)

class NextGenSystem:
    """Système central qui coordonne tous les agents et composants."""
    
    def __init__(self, settings: Settings):
        """
        Initialise le système NextGen.
        
        Args:
            settings: Configuration globale du système
        """
        self.settings = settings
        self.event_bus = EventBus()
        self.memory = ConversationMemory()
        
        # Initialiser le routeur d'intentions
        self.router = IntentRouter(settings.router)
        
        # Initialiser les agents
        self.support_agent = SupportAgent(
            settings=settings.support_agent,
            event_bus=self.event_bus,
            memory=self.memory
        )
        
        self.cybersecurity_agent = CybersecurityAgent(
            settings=settings.cybersecurity_agent,
            event_bus=self.event_bus,
            memory=self.memory
        )
        
        # Enregistrer les événements
        self._register_events()
        
        logger.info("NextGen System initialized successfully")
    
    def _register_events(self):
        """Enregistre les gestionnaires d'événements pour la communication inter-agents."""
        # Support agent écoute les événements de sécurité pour enrichir ses réponses
        self.event_bus.subscribe(
            "security_alert", 
            self.support_agent.handle_security_event
        )
        
        # Cybersecurity agent écoute les requêtes utilisateur pour analyse passive
        self.event_bus.subscribe(
            "user_message", 
            self.cybersecurity_agent.analyze_user_message
        )
        
        # Cybersecurity agent écoute les demandes de scan
        self.event_bus.subscribe(
            "scan_request", 
            self.cybersecurity_agent.handle_scan_request
        )
    
    async def process_query(self, query: str, session_id: str, 
                           metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Traite une requête utilisateur et retourne une réponse.
        
        Args:
            query: Texte de la requête utilisateur
            session_id: Identifiant de session unique
            metadata: Métadonnées additionnelles (contexte, préférences, etc.)
            
        Returns:
            Réponse formatée avec le contenu et les métadonnées
        """
        # Enregistrer le message dans la mémoire
        self.memory.add_user_message(session_id, query)
        
        # Publier l'événement pour analyse passive
        self.event_bus.publish("user_message", {
            "text": query,
            "session_id": session_id,
            "metadata": metadata or {}
        })
        
        # Déterminer l'intention et router vers l'agent approprié
        intent = await self.router.classify_intent(query)
        logger.info(f"Classified intent: {intent} for query: {query[:50]}...")
        
        # Router vers l'agent approprié
        if intent == "cybersecurity_question":
            response = await self.cybersecurity_agent.process(query, session_id, metadata)
        else:  # Par défaut, utiliser l'agent de support
            response = await self.support_agent.process(query, session_id, metadata)
        
        # Enregistrer la réponse dans la mémoire
        self.memory.add_assistant_message(session_id, response["content"])
        
        return response
    
    async def initialize_resources(self):
        """Initialise les ressources nécessaires au démarrage du système."""
        await self.support_agent.initialize()
        await self.cybersecurity_agent.initialize()
        logger.info("All agents initialized successfully")
    
    async def shutdown(self):
        """Libère les ressources lors de l'arrêt du système."""
        await self.support_agent.shutdown()
        await self.cybersecurity_agent.shutdown()
        logger.info("All agents shut down successfully")

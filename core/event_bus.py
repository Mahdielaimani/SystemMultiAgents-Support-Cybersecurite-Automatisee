"""
Bus d'événements pour la communication entre les composants du système.
Implémente un modèle publish-subscribe pour découpler les composants.
"""
import asyncio
import logging
from typing import Dict, Any, Callable, List, Set

logger = logging.getLogger(__name__)

class EventBus:
    """
    Bus d'événements pour la communication asynchrone entre les composants.
    Permet aux composants de s'abonner à des événements et de publier des événements.
    """
    
    def __init__(self):
        """Initialise le bus d'événements avec des dictionnaires vides."""
        self._subscribers: Dict[str, Set[Callable]] = {}
        self._event_history: List[Dict[str, Any]] = []
        self._max_history = 100  # Nombre maximum d'événements à conserver
    
    def subscribe(self, event_type: str, callback: Callable):
        """
        Abonne une fonction de rappel à un type d'événement.
        
        Args:
            event_type: Type d'événement à écouter
            callback: Fonction à appeler lorsque l'événement est publié
        """
        if event_type not in self._subscribers:
            self._subscribers[event_type] = set()
        
        self._subscribers[event_type].add(callback)
        logger.debug(f"Subscribed to event: {event_type}")
    
    def unsubscribe(self, event_type: str, callback: Callable):
        """
        Désabonne une fonction de rappel d'un type d'événement.
        
        Args:
            event_type: Type d'événement
            callback: Fonction à désabonner
        """
        if event_type in self._subscribers and callback in self._subscribers[event_type]:
            self._subscribers[event_type].remove(callback)
            logger.debug(f"Unsubscribed from event: {event_type}")
    
    def publish(self, event_type: str, data: Dict[str, Any] = None):
        """
        Publie un événement de manière synchrone.
        
        Args:
            event_type: Type d'événement à publier
            data: Données associées à l'événement
        """
        if data is None:
            data = {}
        
        event = {"type": event_type, "data": data}
        self._add_to_history(event)
        
        if event_type not in self._subscribers:
            return
        
        for callback in self._subscribers[event_type]:
            try:
                callback(data)
            except Exception as e:
                logger.error(f"Error in event handler for {event_type}: {str(e)}")
    
    async def publish_async(self, event_type: str, data: Dict[str, Any] = None):
        """
        Publie un événement de manière asynchrone.
        
        Args:
            event_type: Type d'événement à publier
            data: Données associées à l'événement
        """
        if data is None:
            data = {}
        
        event = {"type": event_type, "data": data}
        self._add_to_history(event)
        
        if event_type not in self._subscribers:
            return
        
        tasks = []
        for callback in self._subscribers[event_type]:
            if asyncio.iscoroutinefunction(callback):
                tasks.append(asyncio.create_task(callback(data)))
            else:
                try:
                    callback(data)
                except Exception as e:
                    logger.error(f"Error in event handler for {event_type}: {str(e)}")
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
    
    def _add_to_history(self, event: Dict[str, Any]):
        """
        Ajoute un événement à l'historique.
        
        Args:
            event: Événement à ajouter
        """
        self._event_history.append(event)
        if len(self._event_history) > self._max_history:
            self._event_history.pop(0)
    
    def get_recent_events(self, event_type: str = None, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Récupère les événements récents, éventuellement filtrés par type.
        
        Args:
            event_type: Type d'événement à filtrer (optionnel)
            limit: Nombre maximum d'événements à retourner
            
        Returns:
            Liste des événements récents
        """
        if event_type:
            filtered = [e for e in self._event_history if e["type"] == event_type]
            return filtered[-limit:]
        else:
            return self._event_history[-limit:]

from core.intent_router import IntentRouter
from core.conversation_memory import ConversationMemory
from core.knowledge_graph_manager import KnowledgeGraphManager
from agents.support_agent.agent import SupportAgent
from agents.security_agent.agent import SecurityAgent
from agents.pentest_agent.agent import PentestAgent
from agents.teamsquare_agent.agent import TeamSquareAgent
from config import settings

class Orchestrator:
    """
    Orchestre les différents agents et gère la conversation.
    """

    def __init__(self, settings_obj=None):
        """
        Initialise l'orchestrateur.
        
        Args:
            settings_obj: Objet de configuration (utilise les paramètres globaux par défaut)
        """
        self.settings = settings_obj or settings
        self.router = IntentRouter()
        self.memory = ConversationMemory()
        self.graph_manager = KnowledgeGraphManager()
        
        # Initialiser les agents
        self.agents = {
            "support": SupportAgent(),
            "security": SecurityAgent(),
            "pentest": PentestAgent(),
            "teamsquare": TeamSquareAgent()  # Nouvel agent TeamSquare
        }

    def receive_input(self, user_input):
        """
        Reçoit l'entrée de l'utilisateur et la traite.
        """
        # 1. Déterminer l'intention de l'utilisateur
        intent = self.router.determine_intent(user_input)

        # 2. Sélectionner l'agent approprié en fonction de l'intention
        agent = self.select_agent(intent)

        # 3. Envoyer l'entrée à l'agent sélectionné
        response = agent.receive_input(user_input)

        # 4. Mettre à jour la mémoire de conversation
        self.memory.add_message(user_input, "user")
        self.memory.add_message(response, agent.name)

        return response

    def select_agent(self, intent):
        """
        Sélectionne l'agent approprié en fonction de l'intention.
        """
        # Logique de sélection d'agent (peut être basée sur l'intention, des règles, etc.)
        if intent in self.agents:
            return self.agents[intent]
        else:
            # Agent par défaut (par exemple, l'agent de support)
            return self.agents["support"]

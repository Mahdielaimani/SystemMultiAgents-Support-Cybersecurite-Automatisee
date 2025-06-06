
from typing import Dict, Any, Optional
try:
    from agents.cybersecurity_agent.enhanced_agent import EnhancedCybersecurityAgent
    # Utiliser l'agent amélioré
    CybersecurityAgent = EnhancedCybersecurityAgent
except ImportError as e:
    print(f"Erreur import agent amélioré: {e}")
    # Fallback vers l'agent de base
    from agents.base_agent import BaseAgent
    CybersecurityAgent = BaseAgent

import asyncio
"""
Agent TeamSquare - Version basique
"""

class TeamSquareAgent:
    def __init__(self):
        self.name = "TeamSquare Agent"
    
    async def process_message(self, message: str, context=None) -> str:
        return "Je suis l'agent TeamSquare. Comment puis-je vous aider ?"

def create_agent():
    return TeamSquareAgent()

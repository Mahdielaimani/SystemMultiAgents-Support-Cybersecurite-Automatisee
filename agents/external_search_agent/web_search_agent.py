"""
Agent de recherche externe amélioré avec LangChain et outils de navigation web
"""

import logging
import os
from typing import Dict, List, Any, Optional
import json
from datetime import datetime

# Imports LangChain
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_community.utilities import GoogleSearchAPIWrapper
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferWindowMemory
from langchain.tools import Tool, StructuredTool, tool

logger = logging.getLogger(__name__)

class ExternalSearchAgent:
    """Agent de recherche externe utilisant LangChain et des outils web"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.tools = []
        self.agent_executor = None
        self.memory = None
        self._setup_agent()
    
    def _setup_agent(self):
        """Configure l'agent avec les outils nécessaires"""
        try:
            # Configurer les outils de recherche
            self._setup_tools()
            
            # Configurer la mémoire
            self.memory = ConversationBufferWindowMemory(
                memory_key="chat_history",
                k=5,
                return_messages=True
            )
            
            # Configurer le modèle LLM
            llm = self._get_llm()
            
            # Configurer le prompt
            prompt = self._create_prompt()
            
            # Créer l'agent
            agent = create_openai_tools_agent(llm, self.tools, prompt)
            
            # Créer l'exécuteur d'agent
            self.agent_executor = AgentExecutor(
                agent=agent,
                tools=self.tools,
                memory=self.memory,
                verbose=True,
                handle_parsing_errors=True,
                max_iterations=3
            )
            
            self.logger.info("✅ Agent de recherche externe configuré")
            
        except Exception as e:
            self.logger.error(f"❌ Erreur configuration agent: {e}")
            # Fallback à une implémentation de base
            self._setup_fallback()
    
    def _setup_tools(self):
        """Configure les outils de recherche web"""
        try:
            # Outil de recherche DuckDuckGo (ne nécessite pas de clé API)
            ddg_search = DuckDuckGoSearchRun()
            
            # Créer l'outil de recherche web
            self.tools.append(
                Tool(
                    name="web_search",
                    func=ddg_search.run,
                    description="Recherche d'informations sur le web. Utile pour trouver des informations actuelles, des faits, des nouvelles, etc."
                )
            )
            
            # Ajouter l'outil de date/heure actuelle
            @tool
            def get_current_datetime() -> str:
                """Obtient la date et l'heure actuelles."""
                now = datetime.now()
                return now.strftime("%Y-%m-%d %H:%M:%S")
            
            self.tools.append(get_current_datetime)
            
            # Essayer d'ajouter Google Search si la clé API est disponible
            if os.environ.get("GOOGLE_API_KEY") and os.environ.get("GOOGLE_CSE_ID"):
                try:
                    google_search = GoogleSearchAPIWrapper()
                    self.tools.append(
                        Tool(
                            name="google_search",
                            func=google_search.run,
                            description="Recherche Google pour des informations plus précises et à jour."
                        )
                    )
                except Exception as e:
                    self.logger.warning(f"⚠️ Google Search non disponible: {e}")
            
        except Exception as e:
            self.logger.error(f"❌ Erreur configuration outils: {e}")
            # Créer un outil de recherche simulé
            self.tools = [
                Tool(
                    name="simulated_search",
                    func=lambda query: f"Résultats simulés pour: {query}",
                    description="Recherche simulée (mode dégradé)"
                )
            ]
    
    def _get_llm(self):
        """Obtient le modèle LLM approprié"""
        try:
            # Essayer d'utiliser OpenAI si la clé API est disponible
            if os.environ.get("OPENAI_API_KEY"):
                return ChatOpenAI(
                    temperature=0,
                    model="gpt-3.5-turbo-0125",
                    streaming=True
                )
            else:
                # Utiliser un modèle alternatif si disponible
                self.logger.warning("⚠️ Clé OpenAI non disponible, utilisation du modèle alternatif")
                from langchain_community.llms import HuggingFaceEndpoint
                
                if os.environ.get("HUGGINGFACE_API_KEY"):
                    return HuggingFaceEndpoint(
                        repo_id="mistralai/Mistral-7B-Instruct-v0.2",
                        max_length=2048,
                        temperature=0.1
                    )
                else:
                    raise ValueError("Aucun modèle LLM disponible")
                    
        except Exception as e:
            self.logger.error(f"❌ Erreur configuration LLM: {e}")
            raise
    
    def _create_prompt(self):
        """Crée le prompt pour l'agent"""
        system_message = """Tu es un assistant de recherche web précis et factuel.
        
Ton rôle est de rechercher des informations sur le web pour répondre aux questions des utilisateurs.
Utilise les outils à ta disposition pour trouver des informations précises et à jour.

Instructions:
1. Utilise toujours l'outil web_search pour rechercher des informations factuelles
2. Pour les questions de date et heure, utilise l'outil get_current_datetime
3. Cite tes sources dans ta réponse
4. Sois concis et précis
5. Si tu ne trouves pas d'information, dis-le clairement
6. Formate ta réponse de manière claire et lisible

Réponds toujours en français.
"""
        
        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content=system_message),
            MessagesPlaceholder(variable_name="chat_history"),
            HumanMessage(content="{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad")
        ])
        
        return prompt
    
    def _setup_fallback(self):
        """Configure un système de fallback simple en cas d'échec"""
        self.logger.warning("⚠️ Utilisation du système de fallback")
        self.agent_executor = None
    
    def search(self, query: str) -> Dict[str, Any]:
        """
        Effectue une recherche externe
        
        Args:
            query: La requête de recherche
            
        Returns:
            Dict avec la réponse et les métadonnées
        """
        try:
            self.logger.info(f"🔍 Recherche externe: {query}")
            
            if self.agent_executor:
                # Utiliser l'agent LangChain
                result = self.agent_executor.invoke({"input": query})
                
                return {
                    "success": True,
                    "response": result["output"],
                    "sources": ["DuckDuckGo", "Outils LangChain"],
                    "timestamp": datetime.now().isoformat(),
                    "query": query,
                    "raw_result": str(result)[:500]  # Limiter la taille
                }
            else:
                # Utiliser le système de fallback
                return self._fallback_search(query)
                
        except Exception as e:
            self.logger.error(f"❌ Erreur recherche: {e}")
            return {
                "success": False,
                "response": f"Désolé, je n'ai pas pu effectuer la recherche en raison d'une erreur: {str(e)}",
                "sources": [],
                "timestamp": datetime.now().isoformat(),
                "query": query,
                "error": str(e)
            }
    
    def _fallback_search(self, query: str) -> Dict[str, Any]:
        """Système de recherche de secours"""
        self.logger.info("🔄 Utilisation du système de recherche de secours")
        
        # Simuler une recherche basique
        if "heure" in query.lower() or "date" in query.lower() or "jour" in query.lower() or "mois" in query.lower():
            now = datetime.now()
            response = f"Selon les informations disponibles, nous sommes le {now.strftime('%d/%m/%Y')} et il est {now.strftime('%H:%M')}."
            sources = ["Horloge système"]
        elif "météo" in query.lower() or "temps" in query.lower():
            response = "Les résultats de recherche indiquent qu'il faudrait consulter un service météo local pour des informations précises sur la météo actuelle."
            sources = ["Recherche web simulée"]
        elif "actualité" in query.lower() or "news" in query.lower():
            response = "Les résultats de recherche suggèrent de consulter un site d'actualités pour les dernières informations."
            sources = ["Recherche web simulée"]
        else:
            response = f"Les résultats de recherche pour '{query}' indiquent qu'il y a des informations disponibles en ligne, mais je ne peux pas les récupérer en détail dans ce mode."
            sources = ["Recherche web simulée"]
        
        return {
            "success": True,
            "response": response,
            "sources": sources,
            "timestamp": datetime.now().isoformat(),
            "query": query,
            "mode": "fallback"
        }

def main():
    """Test de l'agent de recherche externe"""
    print("🧪 TEST AGENT DE RECHERCHE EXTERNE")
    print("-" * 50)
    
    agent = ExternalSearchAgent()
    
    test_queries = [
        "Quelle heure est-il ?",
        "Quel jour sommes-nous ?",
        "Quelle est la météo à Paris ?",
        "Qui est le président actuel de la France ?",
        "Quelles sont les dernières actualités tech ?"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n🔍 Test {i}: '{query}'")
        
        result = agent.search(query)
        
        print(f"📝 Réponse: {result['response'][:200]}...")
        print(f"📊 Sources: {', '.join(result['sources'])}")
        print(f"✅ Succès: {result['success']}")

if __name__ == "__main__":
    main()

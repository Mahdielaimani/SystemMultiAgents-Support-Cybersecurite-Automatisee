"""
Agent de recherche externe simplifié utilisant DuckDuckGo
"""

import logging
import os
import sys
from datetime import datetime
from typing import Dict, List, Any
import requests
from bs4 import BeautifulSoup
import json

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimpleWebSearchAgent:
    """Agent de recherche externe simplifié"""
    
    def __init__(self):
        self.llm_manager = None
        self._init_llm_manager()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        logger.info("✅ Agent de recherche externe simplifié initialisé")
    
    def _init_llm_manager(self):
        """Initialiser le LLM"""
        try:
            from utils.hybrid_llm_manager_gemini import HybridLLMManagerGemini
            self.llm_manager = HybridLLMManagerGemini()
            logger.info("✅ LLM initialisé")
        except Exception as e:
            logger.error(f"❌ Erreur LLM: {e}")
            self.llm_manager = None
    
    def get_current_datetime(self) -> str:
        """Obtient la date et l'heure actuelles"""
        now = datetime.now()
        return f"Date: {now.strftime('%d/%m/%Y')}, Heure: {now.strftime('%H:%M:%S')}"
    
    def search_duckduckgo(self, query: str) -> str:
        """Recherche sur DuckDuckGo"""
        try:
            # URL de recherche DuckDuckGo
            search_url = "https://html.duckduckgo.com/html/"
            params = {
                'q': query,
                'kl': 'fr-fr'  # Langue française
            }
            
            response = self.session.get(search_url, params=params, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extraire les résultats
            results = []
            result_divs = soup.find_all('div', class_='result')[:3]  # Top 3 résultats
            
            for div in result_divs:
                title_elem = div.find('a', class_='result__a')
                snippet_elem = div.find('a', class_='result__snippet')
                
                if title_elem and snippet_elem:
                    title = title_elem.get_text(strip=True)
                    snippet = snippet_elem.get_text(strip=True)
                    results.append(f"• {title}: {snippet}")
            
            if results:
                return "\n".join(results)
            else:
                return "Aucun résultat trouvé sur DuckDuckGo"
                
        except Exception as e:
            logger.error(f"❌ Erreur recherche DuckDuckGo: {e}")
            return f"Erreur lors de la recherche: {str(e)}"
    
    def search_weather(self, location: str = "Paris") -> str:
        """Recherche météo simplifiée"""
        try:
            # Utiliser une API météo gratuite (OpenWeatherMap nécessite une clé)
            # Pour la démo, on simule avec une recherche web
            query = f"météo {location} aujourd'hui"
            return self.search_duckduckgo(query)
        except Exception as e:
            return f"Erreur recherche météo: {str(e)}"
    
    def search_news(self, topic: str = "actualités") -> str:
        """Recherche d'actualités"""
        try:
            query = f"{topic} dernières nouvelles"
            return self.search_duckduckgo(query)
        except Exception as e:
            return f"Erreur recherche actualités: {str(e)}"
    
    def search(self, query: str) -> Dict[str, Any]:
        """
        Effectue une recherche externe intelligente
        
        Args:
            query: La requête de recherche
            
        Returns:
            Dict avec la réponse et les métadonnées
        """
        try:
            logger.info(f"🔍 Recherche externe: {query}")
            
            # Analyser le type de question
            query_lower = query.lower()
            search_results = ""
            sources = []
            
            # Questions de date/heure
            if any(keyword in query_lower for keyword in ['heure', 'date', 'jour', 'mois', 'année', 'maintenant']):
                search_results = self.get_current_datetime()
                sources = ["Horloge système"]
            
            # Questions météo
            elif any(keyword in query_lower for keyword in ['météo', 'temps', 'température', 'pluie', 'soleil']):
                # Extraire la ville si mentionnée
                location = "Paris"  # Par défaut
                if "à " in query_lower:
                    location = query_lower.split("à ")[-1].strip()
                elif "de " in query_lower:
                    location = query_lower.split("de ")[-1].strip()
                
                search_results = self.search_weather(location)
                sources = ["DuckDuckGo", "Recherche météo"]
            
            # Questions d'actualités
            elif any(keyword in query_lower for keyword in ['actualité', 'news', 'nouvelles', 'dernières']):
                search_results = self.search_news()
                sources = ["DuckDuckGo", "Actualités"]
            
            # Recherche générale
            else:
                search_results = self.search_duckduckgo(query)
                sources = ["DuckDuckGo"]
            
            # Générer une réponse avec Gemini
            if self.llm_manager:
                prompt = f"""Tu es un assistant qui aide à interpréter les résultats de recherche web.

Question de l'utilisateur: {query}

Résultats de recherche:
{search_results}

Instructions:
- Réponds de manière naturelle et conversationnelle en français
- Utilise les informations trouvées pour donner une réponse précise
- Si les informations sont insuffisantes, dis-le clairement
- Sois concis mais informatif
- Ne mentionne pas que tu es un assistant IA

Réponse:"""
                
                response = self.llm_manager.generate(prompt)
            else:
                response = f"Voici les résultats pour '{query}':\n\n{search_results}"
            
            return {
                "success": True,
                "response": response,
                "sources": sources,
                "timestamp": datetime.now().isoformat(),
                "query": query,
                "raw_results": search_results[:500]  # Limiter la taille
            }
            
        except Exception as e:
            logger.error(f"❌ Erreur recherche: {e}")
            return {
                "success": False,
                "response": f"Désolé, je n'ai pas pu effectuer la recherche: {str(e)}",
                "sources": [],
                "timestamp": datetime.now().isoformat(),
                "query": query,
                "error": str(e)
            }

# Test
if __name__ == "__main__":
    agent = SimpleWebSearchAgent()
    
    test_queries = [
        "Quelle heure est-il ?",
        "Quelle est la météo à Paris ?",
        "Qui est le président actuel de la France ?",
        "C'est quoi NVIDIA ?"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n🔍 Test {i}: '{query}'")
        
        result = agent.search(query)
        
        print(f"✅ Succès: {result['success']}")
        print(f"📝 Réponse: {result['response'][:200]}...")
        print(f"📊 Sources: {', '.join(result['sources'])}")

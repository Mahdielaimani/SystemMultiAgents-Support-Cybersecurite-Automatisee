"""
Agent de support TeamSquare - VERSION OPTIMISÉE ET NATURELLE
Combine le meilleur des trois fichiers précédents
"""
import logging
import json
import time
import random
import os
import sys
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path
import re

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AgenticSupportAgentWithExternalRouting:
    """Agent de support TeamSquare optimisé avec recherche web intégrée"""
    
    def __init__(self):
        """Initialisation simplifiée"""
        logger.info("🔄 Initialisation de l'agent TeamSquare...")
        
        # Composants essentiels seulement
        self._init_llm_manager()
        self._init_embeddings()
        self._init_vectorstore()
        
        # Mémoire persistante
        self.memory_store = {}
        self.memory_file = "data/memory/agent_memory.json"
        self._load_memory()
        
        # Sessions avec recherche externe en attente
        self.pending_external_searches = {}
        
        # Statistiques
        self.stats = {
            "queries_processed": 0,
            "external_searches": 0,
            "greetings_handled": 0,
            "in_scope_queries": 0,
            "out_of_scope_queries": 0
        }
        
        # Connaissances de base TeamSquare (intégrées directement)
        self.teamsquare_info = {
            "company": {
                "name": "TeamSquare",
                "description": "TeamSquare est une plateforme innovante de collaboration d'équipe qui révolutionne la façon dont les équipes travaillent ensemble.",
                "mission": "Faciliter la collaboration et améliorer la productivité des équipes",
                "vision": "Devenir la référence mondiale en matière d'outils de collaboration d'équipe"
            },
            "features": {
                "collaboration": [
                    "Chat en temps réel",
                    "Partage de fichiers sécurisé",
                    "Espaces de travail collaboratifs",
                    "Tableaux de bord partagés"
                ],
                "project_management": [
                    "Gestion de projets agile",
                    "Suivi des tâches et deadlines",
                    "Planification d'équipe",
                    "Rapports de progression"
                ],
                "communication": [
                    "Visioconférences intégrées",
                    "Messagerie instantanée",
                    "Notifications intelligentes",
                    "Intégration email"
                ],
                "security": [
                    "Chiffrement end-to-end",
                    "Authentification à deux facteurs",
                    "Contrôle d'accès granulaire",
                    "Sauvegarde automatique"
                ]
            },
            "pricing": {
                "plans": [
                    {
                        "name": "Starter",
                        "price": "9€/mois par utilisateur",
                        "description": "Parfait pour les petites équipes",
                        "features": ["Jusqu'à 10 utilisateurs", "5GB de stockage", "Support email"]
                    },
                    {
                        "name": "Professional", 
                        "price": "19€/mois par utilisateur",
                        "description": "Idéal pour les équipes en croissance",
                        "features": ["Utilisateurs illimités", "100GB de stockage", "Support prioritaire", "Intégrations avancées"]
                    },
                    {
                        "name": "Enterprise",
                        "price": "Sur devis",
                        "description": "Pour les grandes organisations",
                        "features": ["Tout du plan Pro", "Stockage illimité", "Support dédié", "Sécurité renforcée"]
                    }
                ],
                "contact": "Contactez notre équipe commerciale pour obtenir un devis personnalisé"
            },
            "integrations": [
                "Slack", "Microsoft Teams", "Google Workspace", "Zoom", 
                "Trello", "Asana", "GitHub", "Salesforce"
            ],
            "support": {
                "channels": ["Email", "Chat en direct", "Base de connaissances", "Webinaires"],
                "hours": "Support disponible 24/7 pour les plans Professional et Enterprise"
            }
        }
        
        logger.info("✅ Agent TeamSquare optimisé initialisé")
    
    def _init_llm_manager(self):
        """Initialiser le LLM"""
        try:
            from utils.hybrid_llm_manager_gemini import HybridLLMManagerGemini
            self.llm_manager = HybridLLMManagerGemini()
            logger.info("✅ LLM initialisé")
        except Exception as e:
            logger.error(f"❌ Erreur LLM: {e}")
            self.llm_manager = None
    
    def _init_embeddings(self):
        """Initialiser les embeddings"""
        try:
            from sentence_transformers import SentenceTransformer
            self.embedding_model = SentenceTransformer('BAAI/bge-large-en-v1.5')
            logger.info("✅ Embeddings initialisés")
        except Exception as e:
            logger.error(f"❌ Erreur embeddings: {e}")
            self.embedding_model = None
    
    def _init_vectorstore(self):
        """Initialiser ChromaDB"""
        try:
            import chromadb
            self.chroma_client = chromadb.PersistentClient(path="data/vector_db")
            try:
                self.collection = self.chroma_client.get_collection("teamsquare_knowledge")
                logger.info("✅ ChromaDB connecté")
            except:
                self.collection = self.chroma_client.create_collection("teamsquare_knowledge")
                logger.info("✅ ChromaDB créé")
        except Exception as e:
            logger.error(f"❌ Erreur ChromaDB: {e}")
            self.collection = None
    
    def _load_memory(self):
        """Charge la mémoire depuis le fichier"""
        try:
            os.makedirs(os.path.dirname(self.memory_file), exist_ok=True)
            if os.path.exists(self.memory_file):
                with open(self.memory_file, 'r', encoding='utf-8') as f:
                    self.memory_store = json.load(f)
                logger.info(f"✅ Mémoire chargée: {len(self.memory_store)} sessions")
            else:
                self.memory_store = {}
                logger.info("✅ Nouvelle mémoire initialisée")
        except Exception as e:
            logger.error(f"❌ Erreur chargement mémoire: {e}")
            self.memory_store = {}
    
    def _save_memory(self):
        """Sauvegarde la mémoire dans le fichier"""
        try:
            with open(self.memory_file, 'w', encoding='utf-8') as f:
                json.dump(self.memory_store, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"❌ Erreur sauvegarde mémoire: {e}")
    
    def _get_or_create_session_memory(self, session_id: str) -> Dict:
        """Récupère ou crée la mémoire d'une session"""
        if session_id not in self.memory_store:
            self.memory_store[session_id] = {
                "created_at": time.time(),
                "last_active": time.time(),
                "greeted": False,
                "user_info": {},
                "messages": []
            }
        return self.memory_store[session_id]
    
    def _update_session_memory(self, session_id: str, query: str, response: str):
        """Met à jour la mémoire de session"""
        session = self._get_or_create_session_memory(session_id)
        session["last_active"] = time.time()
        session["messages"].append({
            "timestamp": time.time(),
            "query": query,
            "response": response
        })
        
        # Limiter à 20 messages par session
        if len(session["messages"]) > 20:
            session["messages"] = session["messages"][-20:]
        
        self._save_memory()
    
    def _get_conversation_context(self, session_id: str) -> str:
        """Récupère le contexte de conversation récent"""
        session = self._get_or_create_session_memory(session_id)
        
        # Récupérer les 3 derniers messages
        recent_messages = session["messages"][-3:] if session["messages"] else []
        
        if not recent_messages:
            return ""
        
        context_parts = ["Historique de conversation récent:"]
        for msg in recent_messages:
            context_parts.append(f"Utilisateur: {msg['query']}")
            context_parts.append(f"Assistant: {msg['response']}")
        
        return "\n".join(context_parts)
    
    def _is_greeting(self, query: str) -> bool:
        """Détecter les salutations"""
        greetings = ['bonjour', 'bonsoir', 'salut', 'hello', 'hi', 'hey', 'coucou', 'yo']
        query_lower = query.lower().strip()
        return any(g in query_lower for g in greetings) and len(query.split()) <= 3
    
    def _is_teamsquare_question(self, query: str) -> bool:
        """Détecter les questions TeamSquare"""
        keywords = [
            'teamsquare', 'prix', 'tarif', 'fonctionnalité', 'collaboration',
            'équipe', 'projet', 'entreprise', 'société', 'que fait', 'votre entreprise'
        ]
        query_lower = query.lower()
        return any(k in query_lower for k in keywords)
    
    def _should_search_externally(self, query: str) -> bool:
        """Déterminer si recherche externe nécessaire - VERSION AMÉLIORÉE"""
        query_lower = query.lower().strip()
        
        # Pas de recherche externe pour salutations
        if self._is_greeting(query):
            return False
        
        # Pas de recherche externe pour questions TeamSquare
        if self._is_teamsquare_question(query):
            return False
        
        # Pas de recherche externe pour les interactions sociales/conversationnelles
        social_patterns = [
            # Présentations personnelles
            r"je m['\']?appelle?\s+\w+",
            r"mon nom est\s+\w+",
            r"je suis\s+\w+",
            r"moi c['\']?est\s+\w+",
            
            # Phrases conversationnelles simples
            r"^(ça va|comment ça va|bien et toi|très bien|ça roule|nickel)$",
            r"^(merci|thanks|thx|ok|d['\']?accord|parfait|super|cool|génial)$",
            r"^(au revoir|bye|à bientôt|ciao|salut)$",
            
            # Questions de politesse
            r"^(comment allez-vous|comment tu vas|ça va bien)$",
            r"^(vous allez bien|tu vas bien)$",
            
            # Expressions courtes sans contenu informatif
            r"^(ah|oh|euh|hmm|hein|quoi|pardon)$",
            r"^(lol|mdr|haha|hihi)$",
            
            # Réponses courtes
            r"^(oui|non|peut-être|je sais pas|aucune idée)$"
        ]
        
        # Vérifier les patterns sociaux
        for pattern in social_patterns:
            if re.search(pattern, query_lower):
                return False
        
        # Pas de recherche pour les phrases très courtes (moins de 4 mots) sans mots-clés externes
        words = query_lower.split()
        if len(words) < 4:
            # Vérifier si ça contient des mots-clés externes spécifiques
            external_keywords = [
                'météo', 'weather', 'nvidia', 'google', 'microsoft', 'apple',
                'actualité', 'news', 'recette', 'cuisine', 'football', 'sport'
            ]
            if not any(keyword in query_lower for keyword in external_keywords):
                return False
        
        # Recherche externe pour les vraies questions externes
        external_indicators = [
            'météo', 'meteo', 'weather', 'temps qu\'il fait', 'température',
            'nvidia', 'invidia', 'google', 'microsoft', 'apple', 'amazon',
            'actualité', 'news', 'nouvelles', 'dernières',
            'recette', 'cuisine', 'cuisinier',
            'c\'est quoi', 'qu\'est-ce que', 'qui est', 'définition',
            'heure', 'date', 'maintenant', 'aujourd\'hui',
            'football', 'sport', 'match', 'résultat'
        ]
        
        # Vérifier si la question contient des indicateurs externes
        has_external_indicator = any(indicator in query_lower for indicator in external_indicators)
        
        if has_external_indicator:
            logger.info(f"🔍 Question externe détectée: {query}")
            return True
        
        # Pour les questions longues et complexes sans contexte TeamSquare
        if len(words) > 6 and not self._is_teamsquare_question(query):
            # Vérifier si c'est une vraie question (contient des mots interrogatifs)
            question_words = ['comment', 'pourquoi', 'quand', 'où', 'que', 'qui', 'quoi', 'quel']
            if any(word in query_lower for word in question_words):
                return True
        
        return False
    
    def _get_varied_greeting(self, session_id: str) -> str:
        """Générer une salutation variée"""
        session = self._get_or_create_session_memory(session_id)
        
        if not session.get("greeted", False):
            # Première salutation
            session["greeted"] = True
            greetings = [
                "Salut ! 😊 Moi c'est l'assistant TeamSquare. Comment ça va ?",
                "Hey ! Ravi de te rencontrer ! Je suis là pour t'aider avec TeamSquare.",
                "Hello ! 👋 Je suis ton assistant TeamSquare. Qu'est-ce que je peux faire pour toi ?",
                "Coucou ! 😊 Assistant TeamSquare ici ! Comment je peux t'aider aujourd'hui ?"
            ]
        else:
            # Salutations suivantes
            greetings = [
                "Re ! 😊 Ça va ? Une autre question ?",
                "Salut ! De retour ? Comment je peux t'aider cette fois ?",
                "Hello ! 👋 Encore moi ! Qu'est-ce que tu veux savoir ?",
                "Hey ! 😊 Quoi de neuf ?",
                "Re-coucou ! Une autre question pour moi ?"
            ]
        
        return random.choice(greetings)
    
    def _search_knowledge(self, query: str) -> List[str]:
        """Rechercher dans la base de connaissances"""
        results = []
        
        # Recherche dans ChromaDB si disponible
        if self.collection and self.embedding_model:
            try:
                query_embedding = self.embedding_model.encode([query]).tolist()[0]
                chroma_results = self.collection.query(
                    query_embeddings=[query_embedding],
                    n_results=3
                )
                if chroma_results['documents'] and chroma_results['documents'][0]:
                    results.extend(chroma_results['documents'][0])
            except Exception as e:
                logger.error(f"❌ Erreur recherche ChromaDB: {e}")
        
        return results
    
    def _generate_teamsquare_response(self, query: str, context: List[str], conversation_context: str) -> str:
        """Générer une réponse sur TeamSquare"""
        if not self.llm_manager:
            # Réponses de fallback
            if 'prix' in query.lower() or 'tarif' in query.lower():
                return """Ah les prix ! Alors on a 3 formules :

💰 **Starter** : 9€/mois par personne
   Parfait pour débuter !

💰 **Professional** : 19€/mois par personne  
   Le plus populaire, idéal pour grandir

💰 **Enterprise** : Sur devis
   Pour les grosses boîtes

Lequel t'intéresse le plus ?"""

            elif 'entreprise' in query.lower() or 'société' in query.lower():
                return """TeamSquare ? On aide les équipes à mieux bosser ensemble ! 🚀

En gros on fait :
• Chat et messages en temps réel
• Partage de fichiers sécurisé  
• Gestion de projets
• Visio intégrée

Le tout dans une seule app ! Tu veux en savoir plus ?"""

            else:
                return "Hey ! Je suis l'assistant TeamSquare ! Comment je peux t'aider avec notre plateforme ?"
        
        # Construire le contexte
        context_text = "\n".join(context) if context else ""
        
        # Informations TeamSquare
        company_info = self.teamsquare_info["company"]["description"]
        features = ", ".join([item for sublist in self.teamsquare_info["features"].values() for item in sublist[:2]])
        pricing = ", ".join([f"{plan['name']} ({plan['price']})" for plan in self.teamsquare_info["pricing"]["plans"]])
        
        prompt = f"""Tu es l'assistant TeamSquare. Réponds de manière naturelle et amicale.

INFORMATIONS TEAMSQUARE :
- {company_info}
- Fonctionnalités : {features}
- Plans : {pricing}

{conversation_context}

CONTEXTE DISPONIBLE :
{context_text}

QUESTION : {query}

INSTRUCTIONS :
- Réponds naturellement comme un humain
- Utilise les infos TeamSquare et le contexte conversationnel
- Sois concis et utile
- Pas de formatage excessif
- Ne répète JAMAIS exactement la même réponse que précédemment
- Varie ton style et ton vocabulaire

RÉPONSE :"""
        
        try:
            return self.llm_manager.generate(prompt)
        except Exception as e:
            logger.error(f"❌ Erreur génération: {e}")
            return "Désolé, petit problème technique ! Pouvez-vous reformuler votre question ?"
    
    def _offer_external_search(self, query: str) -> str:
        """Proposer une recherche externe"""
        offers = [
            f"Ah '{query}' ! Ça c'est pas mon domaine, moi je suis plutôt TeamSquare 😅 Mais je peux chercher ça pour toi ! Tu veux ?",
            f"Hmm '{query}'... Alors là tu me poses une colle ! 🤔 Je peux demander à Google si tu veux ? (oui/non)",
            f"Oh là '{query}' ! Ça sort de mes compétences TeamSquare ça ! Mais je peux faire une petite recherche ! Ça te dit ?",
            f"Euh... '{query}' ? 😅 C'est pas vraiment mon truc, mais je peux chercher sur le web ! Tu veux que je regarde ?"
        ]
        return random.choice(offers)
    
    def _search_duckduckgo(self, query: str) -> str:
        """Recherche sur DuckDuckGo"""
        try:
            # Créer une session pour les requêtes
            session = requests.Session()
            session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            })
            
            # URL de recherche DuckDuckGo
            search_url = "https://html.duckduckgo.com/html/"
            params = {
                'q': query,
                'kl': 'fr-fr'  # Langue française
            }
            
            response = session.get(search_url, params=params, timeout=10)
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
    
    def _get_current_datetime(self) -> str:
        """Obtient la date et l'heure actuelles"""
        now = datetime.now()
        return f"Date: {now.strftime('%d/%m/%Y')}, Heure: {now.strftime('%H:%M:%S')}"
    
    def _search_external(self, query: str) -> Dict[str, Any]:
        """Effectue une recherche externe"""
        try:
            logger.info(f"🔍 Recherche externe: {query}")
            
            # Analyser le type de question
            query_lower = query.lower()
            search_results = ""
            sources = []
            
            # Questions de date/heure
            if any(keyword in query_lower for keyword in ['heure', 'date', 'jour', 'mois', 'année', 'maintenant']):
                search_results = self._get_current_datetime()
                sources = ["Horloge système"]
            
            # Questions météo
            elif any(keyword in query_lower for keyword in ['météo', 'temps', 'température', 'pluie', 'soleil']):
                # Extraire la ville si mentionnée
                location = "Paris"  # Par défaut
                if "à " in query_lower:
                    location = query_lower.split("à ")[-1].strip()
                elif "de " in query_lower:
                    location = query_lower.split("de ")[-1].strip()
                
                search_results = self._search_duckduckgo(f"météo {location} aujourd'hui")
                sources = ["DuckDuckGo", "Recherche météo"]
            
            # Questions d'actualités
            elif any(keyword in query_lower for keyword in ['actualité', 'news', 'nouvelles', 'dernières']):
                search_results = self._search_duckduckgo("dernières actualités")
                sources = ["DuckDuckGo", "Actualités"]
            
            # Recherche générale
            else:
                search_results = self._search_duckduckgo(query)
                sources = ["DuckDuckGo"]
            
            # Générer une réponse avec le LLM
            if self.llm_manager:
                prompt = f"""Tu es un assistant qui aide à interpréter les résultats de recherche web.

Question de l'utilisateur: {query}

Résultats de recherche:
{search_results}

Instructions:
- Réponds de manière naturelle et conversationnelle en français
- Utilise les informations trouvées pour donner une réponse COURTE et PRÉCISE
- Maximum 2-3 phrases
- Sois direct et concis
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
                "query": query
            }
            
        except Exception as e:
            logger.error(f"❌ Erreur recherche externe: {e}")
            return {
                "success": False,
                "response": f"Désolé, je n'ai pas pu effectuer la recherche: {str(e)}",
                "sources": [],
                "timestamp": datetime.now().isoformat(),
                "query": query
            }
    
    def _is_affirmative(self, text: str) -> bool:
        """Détecte si une réponse est affirmative"""
        affirmative_words = [
            'oui', 'yes', 'ok', 'okay', 'd\'accord', 'daccord', 'bien sûr', 'bien sur',
            'ouais', 'yep', 'yup', 'pourquoi pas', 'vas-y', 'allez', 'go', 'si', 'affirmatif',
            'exactement', 'tout à fait', 'absolument', 'certainement', 'volontiers'
        ]
        
        # Vérifier les mots exacts
        text_lower = text.lower().strip()
        if any(word == text_lower for word in affirmative_words):
            return True
        
        # Vérifier les mots contenus
        if any(word in text_lower for word in affirmative_words):
            return True
            
        # Vérifier les emojis positifs
        positive_emojis = ['👍', '✅', '✔️', '👌', '👏', '🙌', '🤝', '😊', '🙂', '😀']
        if any(emoji in text for emoji in positive_emojis):
            return True
            
        return False
    
    def _is_negative(self, text: str) -> bool:
        """Détecte si une réponse est négative"""
        negative_words = [
            'non', 'no', 'nan', 'pas maintenant', 'non merci', 'nope', 'jamais',
            'négatif', 'pas du tout', 'pas vraiment', 'pas intéressé', 'laisse tomber',
            'ça va pas', 'non merci', 'plus tard', 'une autre fois'
        ]
        
        # Vérifier les mots exacts
        text_lower = text.lower().strip()
        if any(word == text_lower for word in negative_words):
            return True
        
        # Vérifier les mots contenus
        if any(word in text_lower for word in negative_words):
            return True
            
        # Vérifier les emojis négatifs - CORRECTION ICI
        negative_emojis = ['👎', '❌', '❎', '🙅', '🙅‍♂️', '🙅‍♀️', '😕', '😒', '😞', '😔']
        if any(emoji in text for emoji in negative_emojis):
            return True
            
        return False
    
    def _is_greeting_response(self, text: str) -> bool:
        """Détecte si c'est une réponse à une salutation"""
        greeting_responses = [
            'hi', 'hello', 'hey', 'bonjour', 'salut', 'coucou', 'yo',
            'ça va', 'comment ça va', 'bien et toi', 'bien', 'ça va bien'
        ]
        
        text_lower = text.lower().strip()
        return any(resp in text_lower for resp in greeting_responses)
    
    def _is_confusion(self, text: str) -> bool:
        """Détecte si l'utilisateur est confus"""
        confusion_indicators = [
            'quoi', 'hein', 'pardon', 'je comprends pas', 'comprends pas',
            'c\'est quoi', 'qu\'est-ce que', 'de quoi', 'comment ça',
            '?', 'wtf', 'huh', 'euh'
        ]
        
        text_lower = text.lower().strip()
        return any(indicator in text_lower for indicator in confusion_indicators)
    
    def _handle_external_search_response(self, query: str, session_id: str) -> str:
        """Gérer la réponse à la recherche externe - VERSION AMÉLIORÉE"""
        query_lower = query.lower().strip()
        
        if session_id not in self.pending_external_searches:
            return "Je n'ai pas de recherche en attente."
        
        original_query = self.pending_external_searches[session_id]
        
        # Détection intelligente de la réponse
        if self._is_affirmative(query):
            # L'utilisateur veut la recherche
            del self.pending_external_searches[session_id]
            self.stats["external_searches"] += 1
            
            # Effectuer la recherche externe
            search_result = self._search_external(original_query)
            
            if search_result.get("success"):
                responses = [
                    "🔍 " + search_result.get('response', 'Aucun résultat.') + "\n\nBon, maintenant si tu veux parler de TeamSquare... 😉",
                    "🔍 " + search_result.get('response', 'Aucun résultat.') + "\n\nSinon, tu veux découvrir TeamSquare ? On a des trucs sympas !",
                    "🔍 " + search_result.get('response', 'Aucun résultat.') + "\n\nAu fait, tu connais TeamSquare ? Notre plateforme de collaboration !",
                    "🔍 " + search_result.get('response', 'Aucun résultat.') + "\n\nDis-moi, ça t'intéresse de voir ce qu'on fait chez TeamSquare ?"
                ]
                response = random.choice(responses)
            else:
                response = "Désolé, la recherche a échoué. Mais hey, on peut parler de TeamSquare si tu veux ! 😊"
            
            # Mettre à jour la mémoire
            self._update_session_memory(session_id, query, response)
            return response
        
        elif self._is_negative(query):
            # L'utilisateur ne veut pas la recherche
            del self.pending_external_searches[session_id]
            response = "Pas de souci ! Une question sur TeamSquare ?"
            self._update_session_memory(session_id, query, response)
            return response
        
        elif self._is_greeting_response(query):
            # L'utilisateur répond à la salutation, on considère ça comme un oui
            del self.pending_external_searches[session_id]
            response = "Salut ! Je vais prendre ça pour un oui et chercher sur '" + original_query + "'. Un instant..."
            self._update_session_memory(session_id, query, response)
            
            # Effectuer la recherche externe
            search_result = self._search_external(original_query)
            
            if search_result.get("success"):
                return "🔍 " + search_result.get('response', 'Aucun résultat.') + "\n\nAutre chose que je peux faire pour toi ?"
            else:
                return "Désolé, la recherche a échoué. On peut parler de TeamSquare si tu veux ! 😊"
        
        elif self._is_confusion(query):
            # L'utilisateur est confus, on clarifie
            response = f"Je te demandais si tu voulais que je cherche des infos sur '{original_query}' ? C'est pas lié à TeamSquare, mais je peux quand même chercher si tu veux. Dis-moi juste oui ou non 😊"
            self._update_session_memory(session_id, query, response)
            return response
        
        else:
            # Si c'est une nouvelle question, on annule la recherche précédente et on traite comme nouvelle requête
            if len(query) > 10 or '?' in query:
                del self.pending_external_searches[session_id]
                return self.process_query(query, session_id)
            
            # Sinon on demande une clarification
            responses = [
                f"Pardon, je n'ai pas bien compris. Tu veux que je cherche des infos sur '{original_query}' ?",
                f"Hmm, pas sûr de comprendre. Un simple oui ou non pour savoir si je cherche '{original_query}' ?",
                f"Désolé, je suis un peu perdu. Tu veux que je fasse une recherche sur '{original_query}' ?",
                f"Je n'ai pas bien saisi. Tu préfères qu'on parle de TeamSquare ou que je cherche '{original_query}' ?"
            ]
            response = random.choice(responses)
            self._update_session_memory(session_id, query, response)
            return response
    
    def _handle_social_interaction(self, query: str, session_id: str) -> str:
        """Gérer les interactions sociales normales"""
        query_lower = query.lower().strip()
        
        # Présentations personnelles
        if re.search(r"je m['\']?appelle?\s+(\w+)", query_lower):
            name_match = re.search(r"je m['\']?appelle?\s+(\w+)", query_lower)
            if name_match:
                name = name_match.group(1).capitalize()
                session = self._get_or_create_session_memory(session_id)
                session["user_info"]["name"] = name
                
                responses = [
                    f"Salut {name} ! 😊 Ravi de faire ta connaissance ! Moi c'est l'assistant TeamSquare.",
                    f"Hello {name} ! 👋 Enchanté ! Je suis là pour t'aider avec TeamSquare.",
                    f"Coucou {name} ! 😊 Super de te rencontrer ! Comment je peux t'aider avec TeamSquare ?",
                    f"Hey {name} ! Sympa de se présenter ! Qu'est-ce que tu veux savoir sur TeamSquare ?"
                ]
                return random.choice(responses)
        
        # Autres interactions sociales
        if query_lower in ['ça va', 'comment ça va', 'bien et toi', 'très bien', 'ça roule']:
            responses = [
                "Ça va super bien merci ! 😊 Et toi ? Une question sur TeamSquare ?",
                "Nickel ! 👍 Comment je peux t'aider avec TeamSquare aujourd'hui ?",
                "Très bien merci ! 😊 Tu veux découvrir TeamSquare ?",
                "Ça roule ! Et toi ? Qu'est-ce que je peux faire pour toi ?"
            ]
            return random.choice(responses)
        
        if query_lower in ['merci', 'thanks', 'thx']:
            responses = [
                "De rien ! 😊 Autre chose ?",
                "Avec plaisir ! Une autre question ?",
                "Pas de souci ! Comment je peux encore t'aider ?",
                "Je t'en prie ! 😊 Quoi d'autre ?"
            ]
            return random.choice(responses)
        
        # Réponse générale pour les interactions sociales
        responses = [
            "😊 Comment je peux t'aider avec TeamSquare ?",
            "👋 Une question sur notre plateforme ?",
            "😊 Qu'est-ce que tu veux savoir sur TeamSquare ?",
            "Salut ! Comment je peux t'aider aujourd'hui ?"
        ]
        return random.choice(responses)
    
    def process_query(self, query: str, session_id: str = "default") -> str:
        """Traiter une requête - VERSION OPTIMISÉE"""
        try:
            logger.info(f"🔍 Requête: {query[:50]}...")
            
            self.stats["queries_processed"] += 1
            
            # Vérifier recherche externe en attente
            if session_id in self.pending_external_searches:
                return self._handle_external_search_response(query, session_id)
            
            # Gestion des salutations
            if self._is_greeting(query):
                self.stats["greetings_handled"] += 1
                response = self._get_varied_greeting(session_id)
                self._update_session_memory(session_id, query, response)
                return response
            
            # Gestion des interactions sociales (NOUVEAU)
            query_lower = query.lower().strip()
            social_patterns = [
                r"je m['\']?appelle?\s+\w+",
                r"mon nom est\s+\w+",
                r"je suis\s+\w+",
                r"^(ça va|comment ça va|bien et toi|très bien|ça roule|merci|thanks)$"
            ]
            
            if any(re.search(pattern, query_lower) for pattern in social_patterns):
                response = self._handle_social_interaction(query, session_id)
                self._update_session_memory(session_id, query, response)
                return response
            
            # Vérifier si recherche externe nécessaire
            if self._should_search_externally(query):
                self.stats["out_of_scope_queries"] += 1
                self.pending_external_searches[session_id] = query
                response = self._offer_external_search(query)
                self._update_session_memory(session_id, query, response)
                return response
            
            # Question TeamSquare - rechercher et répondre
            self.stats["in_scope_queries"] += 1
            context = self._search_knowledge(query)
            conversation_context = self._get_conversation_context(session_id)
            response = self._generate_teamsquare_response(query, context, conversation_context)
            
            # Mettre à jour la mémoire
            self._update_session_memory(session_id, query, response)
            
            return response
            
        except Exception as e:
            logger.error(f"❌ Erreur: {e}")
            return "Oups, petit problème ! Reformulez votre question ?"
    
    def get_stats(self) -> Dict[str, Any]:
        """Statistiques de l'agent"""
        return {
            "agent_type": "optimized_natural_agent",
            "version": "10.0.0",
            "stats": self.stats,
            "active_sessions": len(self.memory_store),
            "pending_searches": len(self.pending_external_searches),
            "components": {
                "llm": self.llm_manager is not None,
                "embeddings": self.embedding_model is not None,
                "vectorstore": self.collection is not None
            }
        }

# Test
if __name__ == "__main__":
    agent = AgenticSupportAgentWithExternalRouting()
    
    print("=== Test 1: Première salutation ===")
    print(agent.process_query("Bonjour", "test1"))
    
    print("\n=== Test 2: Deuxième salutation ===")
    print(agent.process_query("Salut", "test1"))
    
    print("\n=== Test 3: Question NVIDIA ===")
    print(agent.process_query("C'est quoi NVIDIA ?", "test2"))
    
    print("\n=== Test 4: Prix TeamSquare ===")
    print(agent.process_query("Quels sont vos prix ?", "test3"))

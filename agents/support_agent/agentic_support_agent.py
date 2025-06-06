"""
Agent Support Agentic avec RAG + Outils Externes
Combine recherche interne (ChromaDB) et externe (Web, APIs)
"""

import asyncio
import logging
import os
import sys
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import json

# Ajouter le répertoire racine au path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Imports pour RAG
try:
    from sentence_transformers import SentenceTransformer
    import chromadb
    from chromadb.config import Settings
    CHROMADB_AVAILABLE = True
except ImportError:
    print("⚠️  ChromaDB non disponible, utilisation du mode fallback")
    CHROMADB_AVAILABLE = False

# Imports pour outils externes
try:
    import requests
    from bs4 import BeautifulSoup
    WEB_TOOLS_AVAILABLE = True
except ImportError:
    print("⚠️  Outils web non disponibles")
    WEB_TOOLS_AVAILABLE = False

# Configuration
try:
    from config.settings import get_settings
    settings = get_settings()
except ImportError:
    # Configuration fallback
    class FallbackSettings:
        def __init__(self):
            self.OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
            self.HUGGINGFACE_TOKEN = os.getenv("HUGGINGFACE_TOKEN", "")
            self.DEFAULT_EMBEDDING_MODEL = "BAAI/bge-large-en-v1.5"
    
    settings = FallbackSettings()

@dataclass
class QueryResult:
    """Résultat d'une requête"""
    content: str
    source: str
    confidence: float
    metadata: Dict[str, Any] = None

class AgenticSupportAgent:
    """
    Agent Support Intelligent avec architecture Agentic RAG
    
    Fonctionnalités:
    - RAG interne (ChromaDB + BGE-Large-EN)
    - Recherche web externe
    - Routage intelligent des requêtes
    - Combinaison de sources multiples
    """
    
    def __init__(self):
        self.logger = self._setup_logger()
        
        # Initialisation des composants
        self.embedding_model = None
        self.chroma_client = None
        self.collection = None
        
        # Seuils de décision
        self.internal_confidence_threshold = 0.7
        self.external_search_threshold = 0.5
        
        self._initialize_components()
    
    def _setup_logger(self):
        """Configure le logger"""
        logger = logging.getLogger("AgenticSupportAgent")
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def _initialize_components(self):
        """Initialise les composants RAG et outils"""
        try:
            if CHROMADB_AVAILABLE:
                # Modèle d'embedding BGE-Large-EN
                self.logger.info("🔄 Chargement du modèle BGE-Large-EN...")
                try:
                    self.embedding_model = SentenceTransformer('BAAI/bge-large-en-v1.5')
                    self.logger.info("✅ Modèle BGE-Large-EN chargé")
                except Exception as e:
                    self.logger.warning(f"⚠️  Erreur chargement BGE: {e}, utilisation modèle alternatif")
                    try:
                        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
                        self.logger.info("✅ Modèle alternatif chargé")
                    except Exception as e2:
                        self.logger.error(f"❌ Impossible de charger un modèle d'embedding: {e2}")
                
                # Client ChromaDB
                self.logger.info("🔄 Connexion à ChromaDB...")
                try:
                    chroma_path = "./data/vector_db/chroma_db"
                    os.makedirs(chroma_path, exist_ok=True)
                    
                    self.chroma_client = chromadb.PersistentClient(
                        path=chroma_path,
                        settings=Settings(anonymized_telemetry=False)
                    )
                    
                    # Collection pour la base de connaissances
                    try:
                        self.collection = self.chroma_client.get_collection("knowledge_base")
                        self.logger.info("✅ Collection ChromaDB trouvée")
                    except:
                        self.logger.warning("⚠️  Collection ChromaDB non trouvée, création...")
                        self.collection = self.chroma_client.create_collection(
                            name="knowledge_base",
                            metadata={"description": "Base de connaissances NextGen-Agent"}
                        )
                        
                        # Ajouter quelques données de test
                        self._add_sample_data()
                        
                except Exception as e:
                    self.logger.error(f"❌ Erreur ChromaDB: {e}")
            else:
                self.logger.info("🔄 Mode fallback activé (sans ChromaDB)")
                
        except Exception as e:
            self.logger.error(f"❌ Erreur initialisation: {e}")
            self.logger.info("🔄 Mode fallback complet activé")
    
    def _add_sample_data(self):
        """Ajoute des données d'exemple à ChromaDB"""
        try:
            sample_docs = [
                {
                    "content": "TeamSquare propose trois plans tarifaires : Starter à 29€/mois, Professional à 79€/mois, et Enterprise à 199€/mois. Chaque plan inclut différentes fonctionnalités et limites d'utilisateurs.",
                    "metadata": {"source": "pricing", "category": "teamsquare"}
                },
                {
                    "content": "Pour installer l'API TeamSquare, vous devez d'abord créer un compte développeur, obtenir vos clés API, puis suivre la documentation d'intégration disponible sur notre portail développeur.",
                    "metadata": {"source": "documentation", "category": "api"}
                },
                {
                    "content": "TeamSquare offre des fonctionnalités de collaboration en temps réel, gestion de projets, chat intégré, partage de fichiers, et tableaux de bord analytiques pour optimiser la productivité des équipes.",
                    "metadata": {"source": "features", "category": "teamsquare"}
                },
                {
                    "content": "La sécurité TeamSquare inclut le chiffrement end-to-end, l'authentification à deux facteurs, la conformité GDPR, et des audits de sécurité réguliers pour protéger vos données.",
                    "metadata": {"source": "security", "category": "teamsquare"}
                }
            ]
            
            if self.embedding_model and self.collection:
                for i, doc in enumerate(sample_docs):
                    embedding = self.embedding_model.encode([doc["content"]]).tolist()
                    
                    self.collection.add(
                        embeddings=embedding,
                        documents=[doc["content"]],
                        metadatas=[doc["metadata"]],
                        ids=[f"sample_{i}"]
                    )
                
                self.logger.info(f"✅ {len(sample_docs)} documents d'exemple ajoutés")
                
        except Exception as e:
            self.logger.error(f"❌ Erreur ajout données d'exemple: {e}")
    
    async def process_query(self, query: str) -> str:
        """
        Traite une requête avec l'architecture Agentic RAG
        
        Flow:
        1. Analyse de la requête
        2. Recherche RAG interne
        3. Si insuffisant → Recherche externe
        4. Combinaison et génération de réponse
        """
        self.logger.info(f"🔍 Traitement requête: {query[:50]}...")
        
        try:
            # 1. Analyse de la requête
            query_analysis = await self._analyze_query(query)
            self.logger.info(f"📊 Analyse: {query_analysis}")
            
            # 2. Recherche RAG interne
            internal_results = await self._search_internal_knowledge(query)
            self.logger.info(f"📚 Résultats internes: {len(internal_results)}")
            
            # 3. Décision de recherche externe
            external_results = []
            if self._should_search_external(query_analysis, internal_results):
                self.logger.info("🌐 Recherche externe nécessaire")
                external_results = await self._search_external_sources(query)
            
            # 4. Combinaison et génération
            final_response = await self._generate_response(
                query, internal_results, external_results
            )
            
            self.logger.info(f"✅ Réponse générée ({len(final_response)} chars)")
            return final_response
            
        except Exception as e:
            self.logger.error(f"❌ Erreur traitement requête: {e}")
            return self._fallback_response(query)
    
    async def _analyze_query(self, query: str) -> Dict[str, Any]:
        """Analyse la requête pour déterminer le type et la stratégie"""
        
        # Mots-clés pour classification
        internal_keywords = [
            'teamsquare', 'prix', 'tarif', 'fonctionnalité', 'api',
            'documentation', 'guide', 'tutoriel', 'installation',
            'sécurité', 'collaboration', 'projet'
        ]
        
        external_keywords = [
            'actualité', 'nouvelle', 'récent', 'dernière', 'aujourd\'hui',
            'microsoft', 'google', 'openai', 'technologie', 'marché',
            'météo', 'temps', 'news'
        ]
        
        query_lower = query.lower()
        
        internal_score = sum(1 for kw in internal_keywords if kw in query_lower)
        external_score = sum(1 for kw in external_keywords if kw in query_lower)
        
        return {
            'type': 'internal' if internal_score > external_score else 'external',
            'internal_score': internal_score,
            'external_score': external_score,
            'requires_real_time': any(kw in query_lower for kw in ['actualité', 'récent', 'dernière', 'météo']),
            'complexity': len(query.split())
        }
    
    async def _search_internal_knowledge(self, query: str) -> List[QueryResult]:
        """Recherche dans la base de connaissances interne"""
        
        if not self.embedding_model or not self.collection:
            self.logger.warning("⚠️  RAG interne non disponible")
            return []
        
        try:
            # Génération de l'embedding
            query_embedding = self.embedding_model.encode([query]).tolist()
            
            # Recherche dans ChromaDB
            results = self.collection.query(
                query_embeddings=query_embedding,
                n_results=5,
                include=['documents', 'metadatas', 'distances']
            )
            
            # Conversion en QueryResult
            query_results = []
            if results['documents'] and results['documents'][0]:
                for i, (doc, metadata, distance) in enumerate(zip(
                    results['documents'][0],
                    results['metadatas'][0] or [{}] * len(results['documents'][0]),
                    results['distances'][0]
                )):
                    confidence = max(0, 1 - distance)  # Distance → Confidence
                    
                    query_results.append(QueryResult(
                        content=doc,
                        source="internal_kb",
                        confidence=confidence,
                        metadata=metadata
                    ))
            
            self.logger.info(f"📚 Trouvé {len(query_results)} résultats internes")
            return query_results
            
        except Exception as e:
            self.logger.error(f"❌ Erreur recherche interne: {e}")
            return []
    
    def _should_search_external(self, analysis: Dict, internal_results: List[QueryResult]) -> bool:
        """Détermine si une recherche externe est nécessaire"""
        
        # Si pas de résultats internes suffisants
        if not internal_results:
            return True
        
        # Si confiance interne faible
        max_confidence = max((r.confidence for r in internal_results), default=0)
        if max_confidence < self.internal_confidence_threshold:
            return True
        
        # Si requête nécessite des infos temps réel
        if analysis.get('requires_real_time', False):
            return True
        
        # Si type externe détecté
        if analysis.get('type') == 'external':
            return True
        
        return False
    
    async def _search_external_sources(self, query: str) -> List[QueryResult]:
        """Recherche dans les sources externes"""
        
        external_results = []
        
        try:
            # Recherche web simple
            web_results = await self._search_web(query)
            external_results.extend(web_results)
            
            self.logger.info(f"🌐 Trouvé {len(external_results)} résultats externes")
            
        except Exception as e:
            self.logger.error(f"❌ Erreur recherche externe: {e}")
        
        return external_results
    
    async def _search_web(self, query: str) -> List[QueryResult]:
        """Recherche web basique"""
        
        try:
            # Pour cette démo, on simule des résultats web
            # En production, utiliser une vraie API de recherche (Google, Bing, etc.)
            
            simulated_results = []
            
            # Simulation basée sur le type de requête
            if any(kw in query.lower() for kw in ['microsoft', 'actualité', 'nouvelle']):
                simulated_results.append(QueryResult(
                    content=f"Dernières actualités Microsoft : Microsoft continue d'investir massivement dans l'IA avec de nouveaux partenariats et innovations. "
                           f"L'entreprise a récemment annoncé des améliorations significatives à ses services cloud et IA.",
                    source="web_search",
                    confidence=0.8,
                    metadata={"url": "https://news.microsoft.com", "title": "Microsoft News"}
                ))
            
            elif any(kw in query.lower() for kw in ['météo', 'temps']):
                simulated_results.append(QueryResult(
                    content=f"Météo actuelle : Conditions météorologiques variables selon votre localisation. "
                           f"Pour des informations précises, consultez un service météo local.",
                    source="web_search",
                    confidence=0.6,
                    metadata={"url": "https://weather.com", "title": "Weather Info"}
                ))
            
            else:
                simulated_results.append(QueryResult(
                    content=f"Informations web pour '{query}' : Cette recherche nécessiterait une connexion "
                           f"à une API de recherche web réelle pour obtenir des résultats actualisés.",
                    source="web_search",
                    confidence=0.5,
                    metadata={"url": "https://example.com", "title": "Résultat simulé"}
                ))
            
            return simulated_results
            
        except Exception as e:
            self.logger.error(f"❌ Erreur recherche web: {e}")
            return []
    
    async def _generate_response(self, query: str, internal_results: List[QueryResult], 
                                external_results: List[QueryResult]) -> str:
        """Génère la réponse finale en combinant toutes les sources"""
        
        # Combinaison des résultats
        all_results = internal_results + external_results
        
        if not all_results:
            return self._fallback_response(query)
        
        # Tri par confiance
        all_results.sort(key=lambda x: x.confidence, reverse=True)
        
        # Construction de la réponse
        response_parts = []
        
        # Meilleur résultat comme base
        best_result = all_results[0]
        response_parts.append(f"**Réponse principale:**\n{best_result.content}")
        
        # Sources additionnelles si pertinentes
        additional_sources = [r for r in all_results[1:3] if r.confidence > 0.5]
        if additional_sources:
            response_parts.append("\n**Informations complémentaires:**")
            for result in additional_sources:
                response_parts.append(f"- {result.content[:200]}...")
        
        # Sources utilisées
        sources = list(set(r.source for r in all_results[:3]))
        response_parts.append(f"\n**Sources:** {', '.join(sources)}")
        
        # Confiance globale
        avg_confidence = sum(r.confidence for r in all_results[:3]) / min(3, len(all_results))
        response_parts.append(f"**Confiance:** {avg_confidence:.1%}")
        
        return "\n".join(response_parts)
    
    def _fallback_response(self, query: str) -> str:
        """Réponse de fallback quand aucune source n'est disponible"""
        return (
            f"Je comprends votre question sur '{query}', mais je n'ai pas "
            f"suffisamment d'informations dans ma base de connaissances actuelle "
            f"pour vous donner une réponse précise.\n\n"
            f"**Suggestions:**\n"
            f"- Reformulez votre question avec plus de détails\n"
            f"- Consultez la documentation officielle\n"
            f"- Contactez le support technique pour une assistance personnalisée\n\n"
            f"**Sources:** fallback_response"
        )

# Test rapide
async def test_agent():
    """Test rapide de l'agent"""
    print("🧪 TEST RAPIDE AGENT AGENTIC")
    print("-" * 40)
    
    agent = AgenticSupportAgent()
    
    test_queries = [
        "Quels sont les prix de TeamSquare ?",
        "Comment installer l'API ?",
        "Quelles sont les dernières nouvelles de Microsoft ?"
    ]
    
    for query in test_queries:
        print(f"\n🔍 Test: {query}")
        response = await agent.process_query(query)
        print(f"📝 Réponse: {response[:150]}...")

if __name__ == "__main__":
    asyncio.run(test_agent())

"""
Gestionnaire de prompts LangChain optimisé pour des réponses naturelles
"""
import logging
from typing import Dict, List, Optional, Any
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.messages import SystemMessage, HumanMessage

logger = logging.getLogger(__name__)

class LangChainPromptManager:
    """Gestionnaire de prompts LangChain pour l'agent de support"""
    
    def __init__(self):
        self._setup_prompts()
    
    def _setup_prompts(self):
        """Configure les templates de prompts"""
        
        # Prompt principal simple et naturel
        self.main_template = PromptTemplate(
            input_variables=["query", "context", "memory"],
            template="""Tu es un assistant TeamSquare sympathique et naturel.

{memory}

Contexte disponible:
{context}

Question: {query}

Instructions:
- Réponds de manière naturelle et conversationnelle
- Sois bref et direct
- Utilise le contexte si pertinent
- Si tu ne sais pas, dis-le simplement
- Pas de niveau de confiance ou de métadonnées

Réponse:"""
        )
        
        # Prompt pour les salutations
        self.greeting_template = PromptTemplate(
            input_variables=["query", "memory"],
            template="""Tu es un assistant TeamSquare sympathique.

{memory}

Question: {query}

Réponds simplement et naturellement à cette salutation. Sois bref et amical.

Réponse:"""
        )
        
        # Prompt pour les prix
        self.pricing_template = PromptTemplate(
            input_variables=["query", "context", "memory"],
            template="""Tu es un assistant TeamSquare.

{memory}

Informations sur les prix:
{context}

Question: {query}

Donne les informations de prix de manière claire et directe.

Réponse:"""
        )
        
        # Prompt pour les fonctionnalités
        self.features_template = PromptTemplate(
            input_variables=["query", "context", "memory"],
            template="""Tu es un assistant TeamSquare.

{memory}

Informations sur les fonctionnalités:
{context}

Question: {query}

Explique les fonctionnalités de manière simple et claire.

Réponse:"""
        )
    
    def detect_prompt_type(self, query: str) -> str:
        """Détecte le type de prompt nécessaire"""
        query_lower = query.lower()
        
        # Salutations
        if any(word in query_lower for word in ['bonjour', 'salut', 'hello', 'hi', 'bonsoir']):
            return "greeting"
        
        # Prix
        if any(word in query_lower for word in ['prix', 'tarif', 'coût', 'coute', 'price', 'cost']):
            return "pricing"
        
        # Fonctionnalités
        if any(word in query_lower for word in ['fonctionnalité', 'feature', 'fonction', 'capacité']):
            return "features"
        
        return "main"
    
    def get_prompt_with_context(self, query: str, context_docs: List[str], 
                              memory_context: str, prompt_type: str = None) -> str:
        """Génère un prompt avec contexte"""
        
        if prompt_type is None:
            prompt_type = self.detect_prompt_type(query)
        
        # Formater le contexte
        context_text = "\n".join(context_docs[:3]) if context_docs else "Aucun contexte spécifique disponible."
        
        # Formater la mémoire
        memory_text = memory_context if memory_context.strip() else "Nouvelle conversation."
        
        # Sélectionner le template approprié
        if prompt_type == "greeting":
            template = self.greeting_template
            return template.format(
                query=query,
                memory=memory_text
            )
        elif prompt_type == "pricing":
            template = self.pricing_template
            return template.format(
                query=query,
                context=context_text,
                memory=memory_text
            )
        elif prompt_type == "features":
            template = self.features_template
            return template.format(
                query=query,
                context=context_text,
                memory=memory_text
            )
        else:
            template = self.main_template
            return template.format(
                query=query,
                context=context_text,
                memory=memory_text
            )
    
    def format_memory_for_langchain(self, recent_messages: List[Dict[str, Any]]) -> str:
        """Formate les messages récents pour LangChain"""
        if not recent_messages:
            return ""
        
        formatted_messages = []
        for msg in recent_messages[-3:]:  # Derniers 3 messages seulement
            query = msg.get('query', '')
            response = msg.get('response', '')
            if query and response:
                formatted_messages.append(f"Utilisateur: {query}")
                formatted_messages.append(f"Assistant: {response}")
        
        if formatted_messages:
            return "Historique récent:\n" + "\n".join(formatted_messages) + "\n"
        
        return ""

def main():
    """Test du gestionnaire de prompts"""
    print("🧪 TEST GESTIONNAIRE DE PROMPTS LANGCHAIN")
    print("-" * 50)
    
    manager = LangChainPromptManager()
    
    test_cases = [
        {
            "query": "Bonjour !",
            "context": [],
            "memory": "",
            "expected_type": "greeting"
        },
        {
            "query": "Quels sont les prix de TeamSquare ?",
            "context": ["TeamSquare propose trois plans : Starter (29€), Professional (79€), Enterprise (199€)"],
            "memory": "",
            "expected_type": "pricing"
        },
        {
            "query": "Quelles sont les fonctionnalités ?",
            "context": ["TeamSquare inclut chat, gestion de projets, partage de fichiers"],
            "memory": "",
            "expected_type": "features"
        }
    ]
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n🔍 Test {i}: {test['query']}")
        
        detected_type = manager.detect_prompt_type(test['query'])
        print(f"   Type détecté: {detected_type} (attendu: {test['expected_type']})")
        
        prompt = manager.get_prompt_with_context(
            query=test['query'],
            context_docs=test['context'],
            memory_context=test['memory'],
            prompt_type=detected_type
        )
        
        print(f"   Prompt généré: {prompt[:200]}...")

if __name__ == "__main__":
    main()

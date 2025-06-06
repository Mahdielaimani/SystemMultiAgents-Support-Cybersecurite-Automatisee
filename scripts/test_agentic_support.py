#!/usr/bin/env python3
"""
Test complet de l'agent support agentic
"""

import asyncio
import sys
import os

# Ajouter le répertoire parent au path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.support_agent.agentic_support_agent import AgenticSupportAgent

async def test_complete_agent():
    """Test complet de l'agent support agentic"""
    
    print("🚀 TEST AGENT SUPPORT AGENTIC")
    print("=" * 50)
    
    # Initialisation
    agent = AgenticSupportAgent()
    
    # Tests variés
    test_cases = [
        {
            "query": "Quels sont les prix de TeamSquare ?",
            "expected_source": "internal",
            "description": "Test RAG interne - Pricing"
        },
        {
            "query": "Comment installer l'API TeamSquare ?",
            "expected_source": "internal", 
            "description": "Test RAG interne - Documentation"
        },
        {
            "query": "Quelles sont les dernières nouvelles de Microsoft ?",
            "expected_source": "external",
            "description": "Test recherche externe - Actualités"
        },
        {
            "query": "Quelle est la météo aujourd'hui ?",
            "expected_source": "external",
            "description": "Test recherche externe - Info temps réel"
        },
        {
            "query": "Comment configurer la sécurité ?",
            "expected_source": "mixed",
            "description": "Test mixte - Sécurité"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📝 TEST {i}: {test_case['description']}")
        print(f"❓ Question: {test_case['query']}")
        
        try:
            response = await agent.process_query(test_case['query'])
            
            print(f"✅ Réponse ({len(response)} chars):")
            print(f"   {response[:200]}...")
            
            if len(response) > 200:
                print("   [Réponse tronquée]")
                
        except Exception as e:
            print(f"❌ Erreur: {e}")
    
    print(f"\n🎯 TESTS TERMINÉS")
    print("=" * 50)

if __name__ == "__main__":
    asyncio.run(test_complete_agent())

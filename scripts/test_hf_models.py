"""
Script de test pour vos modèles Hugging Face
"""

import sys
import os
import json
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Ajout du chemin parent pour l'import
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importer la version réelle (pas mock) de vos modèles
from agents.cybersecurity_agent.huggingface_models import HuggingFaceSecurityModels

# Essayer d'importer l'agent amélioré si disponible
try:
    from agents.cybersecurity_agent.enhanced_agent import EnhancedCybersecurityAgent
    agent_available = True
except ImportError as e:
    print(f"Erreur import agent amélioré: {e}")
    agent_available = False


def test_elmahdi_models():
    """Teste tous vos modèles avec des exemples réels"""
    
    print("🧪 TEST DE VOS MODÈLES HUGGING FACE")
    print("-" * 50)

    # Initialiser les modèles (avec votre token si nécessaire)
    try:
        models = HuggingFaceSecurityModels()
        print("✅ Modèles initialisés avec succès\n")
    except Exception as e:
        print(f"❌ Erreur lors de l'initialisation des modèles: {e}")
        return

    # Test 1 : Classificateur de vulnérabilités
    print("\n1️⃣ TEST VULNERABILITY CLASSIFIER")
    print("-" * 30)
    test_cases_vuln = [
        "<script>alert('XSS attack')</script>",
        "SELECT * FROM users WHERE id = 1 OR 1=1",
        "This is a normal comment about security",
        "<?php system($_GET['cmd']); ?>",
        "../../../etc/passwd"
    ]

    for test_case in test_cases_vuln:
        try:
            result = models.classify_vulnerability(test_case)
            print(f"   Input: {test_case[:30]}...")
            print(f"   Result: {result.get('vulnerability_type', 'error')} (conf: {result.get('confidence', 0):.2f})")
        except Exception as e:
            print(f"   ❌ Erreur pour '{test_case[:30]}...': {e}")

    # Test 2 : Analyseur de trafic réseau
    print("\n2️⃣ TEST NETWORK ANALYZER (CIC-IDS)")
    print("-" * 30)
    test_cases_network = [
        "Multiple failed authentication attempts from 192.168.1.100",
        "High volume of SYN packets detected - possible DDoS",
        "Normal HTTP traffic to web server",
        "Port scanning activity detected on ports 22, 80, 443",
        "Malicious payload detected in network traffic"
    ]

    for test_case in test_cases_network:
        try:
            result = models.analyze_network_traffic(test_case)
            print(f"   Input: {test_case[:30]}...")
            print(f"   Result: {result.get('traffic_type', 'error')} (conf: {result.get('confidence', 0):.2f})")
        except Exception as e:
            print(f"   ❌ Erreur pour '{test_case[:30]}...': {e}")

    # Test 3 : Classificateur d'intention
    print("\n3️⃣ TEST INTENT CLASSIFIER")
    print("-" * 30)
    test_cases_intent = [
        "I want to hack this website and steal data",
        "Can you help me with a security audit?",
        "How do I perform a penetration test?",
        "I need to bypass this security system",
        "Please help me secure my application"
    ]

    for test_case in test_cases_intent:
        try:
            result = models.classify_intent(test_case)
            print(f"   Input: {test_case[:30]}...")
            print(f"   Result: {result.get('intent', 'error')} (conf: {result.get('confidence', 0):.2f})")
        except Exception as e:
            print(f"   ❌ Erreur pour '{test_case[:30]}...': {e}")

    # Test global
    print("\n🔄 TEST GLOBAL DE TOUS LES MODÈLES")
    print("-" * 30)
    try:
        global_test = models.test_all_models()
        print(f"   Statut: {global_test['overall_status']}")
        print(f"   Modèles testés: {global_test['models_tested']}")
        for key, value in global_test.items():
            if key not in ['overall_status', 'models_tested', 'timestamp']:
                print(f"   {key}: {value}")
    except Exception as e:
        print(f"   ❌ Erreur lors du test global: {e}")

    # Informations sur les modèles
    print("\n📊 INFORMATIONS SUR VOS MODÈLES")
    print("-" * 30)
    try:
        model_info = models.get_model_info()
        print(json.dumps(model_info, indent=2))
    except Exception as e:
        print(f"   ❌ Erreur lors de la récupération des infos: {e}")

    # Test de l'agent amélioré si disponible
    if agent_available:
        print("\n🤖 TEST DE L'AGENT AMÉLIORÉ")
        print("-" * 30)
        try:
            agent = EnhancedCybersecurityAgent()
            test_query = "Analyze this code for vulnerabilities: SELECT * FROM users WHERE id = $_GET['id']"
            response = agent.process_query(test_query)
            print(f"   Query: {test_query}")
            print(f"   Response: {response[:200]}...")
        except Exception as e:
            print(f"   ❌ Erreur avec l'agent: {e}")


def test_individual_model(model_name):
    """Teste un modèle spécifique"""
    from transformers import pipeline
    
    print(f"\n🔬 Test individuel du modèle: {model_name}")
    print("-" * 50)
    
    try:
        # Créer un pipeline
        classifier = pipeline("text-classification", model=model_name)
        
        # Tester avec un exemple
        test_text = "This is a test for security classification"
        result = classifier(test_text)
        
        print(f"✅ Modèle chargé avec succès!")
        print(f"   Test: {test_text}")
        print(f"   Résultat: {result}")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")


if __name__ == "__main__":
    # Test principal
    test_elmahdi_models()
    
    # Tests individuels optionnels
    print("\n" + "="*60)
    print("TESTS INDIVIDUELS DES MODÈLES")
    print("="*60)
    
    models_to_test = [
        "elmahdielaimani/vulnerability-classifier",
        "elmahdielaimani/network-analyzer-cicids",
        "elmahdielaimani/intent-classifier-security"
    ]
    
    for model in models_to_test:
        test_individual_model(model)
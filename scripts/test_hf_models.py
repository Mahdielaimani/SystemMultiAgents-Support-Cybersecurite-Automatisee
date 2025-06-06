"""
Script de test pour vos modèles Hugging Face
"""

import sys
import os
import json

# Ajout du chemin parent pour l'import
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.cybersecurity_agent.huggingface_models import HuggingFaceSecurityModels


def test_elmahdi_models():
    """Teste tous vos modèles avec des exemples réels"""
    
    print("🧪 TEST DE VOS MODÈLES HUGGING FACE")
    print("-" * 50)

    # Initialiser les modèles (avec votre token si nécessaire)
    models = HuggingFaceSecurityModels()

    # Test 1 : Classificateur de vulnérabilités
    print("\n1️⃣ TEST VULNERABILITY CLASSIFIER")
    test_cases_vuln = [
        "<script>alert('XSS attack')</script>",
        "SELECT * FROM users WHERE id = 1 OR 1=1",
        "This is a normal comment about security",
        "<?php system($_GET['cmd']); ?>",
        "../../../etc/passwd"
    ]

    for test_case in test_cases_vuln:
        result = models.classify_vulnerability(test_case)
        print(f"   Input: {test_case[:30]}...")
        print(f"   Result: {result.get('vulnerability_type', 'error')} (conf: {result.get('confidence', 0):.2f})")

    # Test 2 : Analyseur de trafic réseau
    print("\n2️⃣ TEST NETWORK ANALYZER (CIC-IDS)")
    test_cases_network = [
        "Multiple failed authentication attempts from 192.168.1.100",
        "High volume of SYN packets detected - possible DDoS",
        "Normal HTTP traffic to web server",
        "Port scanning activity detected on ports 22, 80, 443",
        "Malicious payload detected in network traffic"
    ]

    for test_case in test_cases_network:
        result = models.analyze_network_traffic(test_case)
        print(f"   Input: {test_case[:30]}...")
        print(f"   Result: {result.get('traffic_type', 'error')} (conf: {result.get('confidence', 0):.2f})")

    # Test 3 : Classificateur d'intention
    print("\n3️⃣ TEST INTENT CLASSIFIER")
    test_cases_intent = [
        "I want to hack this website and steal data",
        "Can you help me with a security audit?",
        "How do I perform a penetration test?",
        "I need to bypass this security system",
        "Please help me secure my application"
    ]

    for test_case in test_cases_intent:
        result = models.classify_intent(test_case)
        print(f"   Input: {test_case[:30]}...")
        print(f"   Result: {result.get('intent', 'error')} (conf: {result.get('confidence', 0):.2f})")

    # Test global
    print("\n🔄 TEST GLOBAL DE TOUS LES MODÈLES")
    global_test = models.test_all_models()
    print(f"   Statut: {global_test['overall_status']}")
    print(f"   Modèles testés: {global_test['models_tested']}")

    # Informations sur les modèles
    print("\n📊 INFORMATIONS SUR VOS MODÈLES")
    model_info = models.get_model_info()
    print(json.dumps(model_info, indent=2))


if __name__ == "__main__":
    test_elmahdi_models()

"""
Test des modèles personnalisés
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.cybersecurity_agent.custom_model_loaders import HuggingFaceSecurityModelsCustom

def test_custom_models():
    print("🧪 TEST DES MODÈLES PERSONNALISÉS")
    print("-" * 50)
    
    # Initialiser
    models = HuggingFaceSecurityModelsCustom()
    
    # Tests
    test_cases = [
        "<script>alert('XSS')</script>",
        "SELECT * FROM users WHERE id=1",
        "Multiple failed login attempts detected",
        "I want to hack this system"
    ]
    
    for text in test_cases:
        print(f"\n📝 Test: {text}")
        
        # Vulnérabilité
        vuln = models.classify_vulnerability(text)
        print(f"   Vulnerability: {vuln}")
        
        # Réseau
        net = models.analyze_network_traffic(text)
        print(f"   Network: {net}")
        
        # Intention
        intent = models.classify_intent(text)
        print(f"   Intent: {intent}")
    
    # Info
    print("\n📊 INFORMATIONS")
    print(models.get_model_info())

if __name__ == "__main__":
    test_custom_models()

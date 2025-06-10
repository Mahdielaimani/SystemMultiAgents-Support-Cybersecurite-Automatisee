# scripts/verify_agent_communication.py
"""
Script pour vérifier la communication entre les agents Support et Sécurité
"""
import requests
import json
import time
from datetime import datetime

def test_security_analysis():
    """Teste l'analyse de sécurité"""
    print("🔍 Test de l'analyse de sécurité...")
    
    # Message suspect à analyser
    suspicious_message = "J'ai besoin d'exploiter une vulnérabilité SQL injection"
    
    try:
        response = requests.post(
            "http://localhost:8000/api/cybersecurity/analyze",
            json={
                "text": suspicious_message,
                "models": ["vulnerability_classifier", "intent_classifier"]
            },
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Analyse réussie:")
            print(f"   Vulnérabilité: {result.get('vulnerability_classifier', {}).get('vulnerability_type', 'N/A')}")
            print(f"   Intention: {result.get('intent_classifier', {}).get('intent', 'N/A')}")
            print(f"   Niveau menace: {result.get('overall_threat_level', 'N/A')}")
            return result
        else:
            print(f"❌ Erreur analyse: HTTP {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return None

def test_support_chat():
    """Teste le chat de support"""
    print("\n💬 Test du chat de support...")
    
    # Message suspect
    suspicious_query = "Comment puis-je faire une injection SQL sur TeamSquare ?"
    
    try:
        response = requests.post(
            "http://localhost:8000/api/agentic/chat",
            json={
                "query": suspicious_query,
                "session_id": "security_test"
            },
            timeout=15
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Chat réussi:")
            print(f"   Réponse: {result.get('content', 'N/A')[:100]}...")
            print(f"   Métadonnées: {result.get('metadata', {})}")
            return result
        else:
            print(f"❌ Erreur chat: HTTP {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return None

def test_inter_agent_communication():
    """Teste la communication inter-agents"""
    print("\n🤝 Test de communication inter-agents...")
    
    try:
        # Simuler une communication du support vers la sécurité
        response = requests.post(
            "http://localhost:8000/api/inter-agent/communicate",
            json={
                "from_agent": "support",
                "to_agent": "security", 
                "message": {
                    "action": "verify_message",
                    "text": "SELECT * FROM users WHERE id = 1 OR 1=1",
                    "session_id": "test_communication"
                }
            },
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Communication inter-agents réussie:")
            print(f"   Statut: {result.get('status', 'N/A')}")
            print(f"   Analyse: {result.get('analysis', {})}")
            return result
        else:
            print(f"❌ Erreur communication: HTTP {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return None

def check_alerts():
    """Vérifie les alertes de sécurité"""
    print("\n🚨 Vérification des alertes...")
    
    try:
        response = requests.get(
            "http://localhost:8000/api/cybersecurity/alerts",
            timeout=5
        )
        
        if response.status_code == 200:
            result = response.json()
            alerts = result.get('alerts', [])
            print(f"✅ {len(alerts)} alertes trouvées:")
            
            for alert in alerts[:3]:  # Afficher les 3 dernières
                print(f"   🔹 {alert.get('severity', 'N/A').upper()}: {alert.get('message', 'N/A')}")
                print(f"     Session: {alert.get('user_session', 'N/A')} | {alert.get('timestamp', 'N/A')}")
            
            return alerts
        else:
            print(f"❌ Erreur alertes: HTTP {response.status_code}")
            return []
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return []

def verify_agent_integration():
    """Vérifie l'intégration complète des agents"""
    print(f"""
╔══════════════════════════════════════════════════════════════════════════╗
║                    VÉRIFICATION AGENTS INTÉGRÉS                          ║
║                                                                          ║
║  Test de communication entre Agent Support et Agent Sécurité            ║
║                                                                          ║
╚══════════════════════════════════════════════════════════════════════════╝

Démarré le: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
""")
    
    # 1. Tester l'analyse de sécurité
    security_result = test_security_analysis()
    
    # 2. Tester le chat de support  
    chat_result = test_support_chat()
    
    # 3. Tester la communication inter-agents
    comm_result = test_inter_agent_communication()
    
    # 4. Vérifier les alertes
    alerts = check_alerts()
    
    # 5. Résumé
    print(f"\n{'='*70}")
    print("📊 RÉSUMÉ DE LA VÉRIFICATION")
    print(f"{'='*70}")
    
    services_status = {
        "Analyse Sécurité": "✅ OK" if security_result else "❌ KO",
        "Chat Support": "✅ OK" if chat_result else "❌ KO", 
        "Communication Inter-Agents": "✅ OK" if comm_result else "❌ KO",
        "Alertes Sécurité": f"✅ {len(alerts)} alertes" if alerts else "❌ Aucune alerte"
    }
    
    for service, status in services_status.items():
        print(f"  {service}: {status}")
    
    # Vérification de l'intégration
    integration_working = all([security_result, chat_result, comm_result])
    
    print(f"\n🔗 INTÉGRATION AGENTS:")
    if integration_working:
        print("✅ LES AGENTS SONT CONNECTÉS ET COMMUNICENT !")
        print("   • L'agent Support peut analyser les menaces")
        print("   • L'agent Sécurité détecte les vulnérabilités")
        print("   • La communication inter-agents fonctionne")
        print("   • Les alertes sont générées automatiquement")
    else:
        print("❌ Problème d'intégration détecté")
        print("   Vérifiez que tous les services sont démarrés")
    
    print(f"\n📱 INTERFACES DISPONIBLES:")
    print(f"   • Chat Support: http://localhost:3000")
    print(f"   • Admin Sécurité: http://localhost:3000/admin-security")
    print(f"   • API Docs: http://localhost:8000/docs")
    
    return integration_working

if __name__ == "__main__":
    verify_agent_integration()
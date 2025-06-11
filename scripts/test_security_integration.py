#!/usr/bin/env python3
"""
Script de test pour vérifier que l'intégration de sécurité fonctionne correctement
"""
import asyncio
import sys
import os
from pathlib import Path

# Ajouter le répertoire racine au path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import des modules corrigés
from api.shared_state import system_state, security_alerts, add_security_alert
from api.cybersecurity_routes import analyze_security, SecurityAnalysisRequest
from api.agentic_routes import analyze_message_security, check_and_block_if_needed

async def test_security_analysis():
    """Test de l'analyse de sécurité"""
    print("🧪 TEST 1: Analyse de sécurité")
    print("-" * 50)
    
    test_cases = [
        ("Message normal", "Bonjour, comment allez-vous ?"),
        ("SQL Injection", "SELECT * FROM users WHERE id = 1 OR 1=1"),
        ("XSS Attack", "<script>alert('XSS')</script>"),
        ("Malicious Intent", "Comment puis-je hacker votre système ?")
    ]
    
    for name, message in test_cases:
        print(f"\n📝 Test: {name}")
        print(f"   Message: {message}")
        
        # Créer une requête d'analyse
        request = SecurityAnalysisRequest(
            text=message,
            models=["vulnerability_classifier", "intent_classifier"],
            session_id="test_session"
        )
        
        # Analyser
        result = await analyze_security(request)
        
        print(f"   ✅ Analyse complétée:")
        print(f"      - Niveau de menace: {result.overall_threat_level}")
        print(f"      - Vulnérabilité: {result.vulnerability_classifier}")
        print(f"      - Intention: {result.intent_classifier}")
        print(f"      - Alertes avant: {len(security_alerts)}")
        
        # Vérifier si des alertes ont été créées
        await asyncio.sleep(0.1)  # Petit délai pour les alertes asynchrones
        print(f"      - Alertes après: {len(security_alerts)}")

async def test_blocking_mechanism():
    """Test du mécanisme de blocage"""
    print("\n\n🧪 TEST 2: Mécanisme de blocage")
    print("-" * 50)
    
    # Réinitialiser l'état
    system_state["blocked"] = False
    system_state["threat_level"] = "safe"
    
    print(f"État initial - Bloqué: {system_state['blocked']}, Niveau: {system_state['threat_level']}")
    
    # Test avec un message très malveillant
    malicious_message = "'; DROP TABLE users; -- SELECT * FROM admin"
    
    # Analyser la sécurité
    analysis = await analyze_message_security(malicious_message, "attacker_001")
    print(f"\n📊 Analyse du message malveillant:")
    print(f"   - Niveau de menace: {analysis.get('overall_threat_level')}")
    
    # Vérifier si blocage nécessaire
    should_block = await check_and_block_if_needed(analysis, "attacker_001")
    print(f"\n🚫 Doit bloquer ? {should_block}")
    print(f"État après - Bloqué: {system_state['blocked']}, Niveau: {system_state['threat_level']}")
    
    if should_block:
        print(f"   ✅ Système correctement bloqué!")
        print(f"   - Raison: {system_state['block_reason']}")
    else:
        print(f"   ❌ Le système aurait dû être bloqué!")

async def test_alert_generation():
    """Test de la génération d'alertes"""
    print("\n\n🧪 TEST 3: Génération d'alertes")
    print("-" * 50)
    
    initial_alerts = len(security_alerts)
    print(f"Alertes initiales: {initial_alerts}")
    
    # Ajouter quelques alertes
    add_security_alert(
        alert_type="vulnerability",
        severity="high",
        message="SQL Injection détectée",
        session_id="test_001"
    )
    
    add_security_alert(
        alert_type="intent",
        severity="critical",
        message="Intention malveillante confirmée",
        session_id="test_002"
    )
    
    final_alerts = len(security_alerts)
    print(f"Alertes finales: {final_alerts}")
    print(f"Nouvelles alertes créées: {final_alerts - initial_alerts}")
    
    # Afficher les dernières alertes
    print("\n📋 Dernières alertes:")
    for alert in security_alerts[:3]:
        print(f"   - [{alert['severity'].upper()}] {alert['message']} ({alert['timestamp']})")

async def test_full_integration():
    """Test d'intégration complète"""
    print("\n\n🧪 TEST 4: Intégration complète")
    print("-" * 50)
    
    # Simuler une conversation avec attaque
    messages = [
        ("user_normal", "Bonjour, quels sont vos prix ?"),
        ("attacker_001", "'; DROP TABLE users; --"),
        ("user_normal", "Comment fonctionne votre plateforme ?"),
        ("attacker_002", "<script>alert('XSS')</script>")
    ]
    
    for session_id, message in messages:
        print(f"\n👤 Session: {session_id}")
        print(f"💬 Message: {message}")
        
        # Analyser et vérifier
        analysis = await analyze_message_security(message, session_id)
        blocked = await check_and_block_if_needed(analysis, session_id)
        
        print(f"🔍 Résultat:")
        print(f"   - Menace: {analysis.get('overall_threat_level')}")
        print(f"   - Bloqué: {'✅ OUI' if blocked else '❌ NON'}")
        print(f"   - État système: {'🚫 BLOQUÉ' if system_state['blocked'] else '✅ ACTIF'}")

async def main():
    """Fonction principale"""
    print("""
╔══════════════════════════════════════════════════════════════════════════╗
║                TEST D'INTÉGRATION SÉCURITÉ CORRIGÉE                      ║
╚══════════════════════════════════════════════════════════════════════════╝
""")
    
    try:
        # Exécuter les tests
        await test_security_analysis()
        await test_blocking_mechanism()
        await test_alert_generation()
        await test_full_integration()
        
        # Résumé final
        print("\n\n📊 RÉSUMÉ FINAL")
        print("=" * 70)
        print(f"✅ Tests complétés avec succès!")
        print(f"📈 Statistiques:")
        print(f"   - Total d'alertes générées: {len(security_alerts)}")
        print(f"   - État du système: {'🚫 BLOQUÉ' if system_state['blocked'] else '✅ ACTIF'}")
        print(f"   - Niveau de menace: {system_state['threat_level']}")
        print(f"   - Menaces détectées: {system_state.get('total_threats_detected', 0)}")
        
    except Exception as e:
        print(f"\n❌ Erreur durant les tests: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
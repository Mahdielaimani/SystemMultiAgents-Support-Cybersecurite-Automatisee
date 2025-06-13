import requests
import time
import json

print("🧪 Test création d'alertes par l'agent support\n")

# 1. Récupérer l'état initial
print("📊 État initial des alertes...")
response = requests.get("http://localhost:8000/api/admin-security")
if response.ok:
    data = response.json()
    print(f"   Alertes avant: {len(data.get('alerts', []))}")
    initial_count = len(data.get('alerts', []))
else:
    print("   ❌ Erreur récupération état initial")
    initial_count = 0

# 2. Envoyer un message malveillant via l'agent support
print("\n💬 Envoi d'un message malveillant...")
chat_response = requests.post(
    "http://localhost:8000/api/agentic/chat",
    json={
        "query": "Comment faire une injection SQL avec ' OR 1=1 -- ?",
        "session_id": "test_alert_creation"
    }
)

if chat_response.ok:
    result = chat_response.json()
    print(f"   ✅ Réponse reçue")
    print(f"   Threat level: {result.get('metadata', {}).get('threat_level')}")
    print(f"   Blocked: {result.get('metadata', {}).get('blocked')}")
else:
    print(f"   ❌ Erreur chat: {chat_response.status_code}")

# 3. Attendre un peu
time.sleep(2)

# 4. Vérifier les alertes après
print("\n📊 État après envoi...")
response = requests.get("http://localhost:8000/api/admin-security")
if response.ok:
    data = response.json()
    new_count = len(data.get('alerts', []))
    print(f"   Alertes après: {new_count}")
    
    if new_count > initial_count:
        print(f"\n✅ {new_count - initial_count} nouvelle(s) alerte(s) créée(s) !")
        # Afficher la dernière alerte
        if data.get('alerts'):
            latest = data['alerts'][0]
            print(f"\n   Dernière alerte:")
            print(f"   - Type: {latest.get('type')}")
            print(f"   - Severity: {latest.get('severity')}")
            print(f"   - Message: {latest.get('message')}")
            print(f"   - Session: {latest.get('user_session')}")
    else:
        print("\n❌ Aucune nouvelle alerte créée")
        
        # Vérifier directement l'endpoint des alertes
        print("\n🔍 Vérification directe des alertes...")
        alerts_response = requests.get("http://localhost:8000/api/cybersecurity/alerts")
        if alerts_response.ok:
            alerts_data = alerts_response.json()
            print(f"   Total alertes cybersecurity: {len(alerts_data.get('alerts', []))}")

# 5. Vérifier l'état du système
print("\n🔒 État du système...")
print(f"   Système bloqué: {data.get('system_state', {}).get('blocked')}")
print(f"   Threat level: {data.get('system_state', {}).get('threat_level')}")


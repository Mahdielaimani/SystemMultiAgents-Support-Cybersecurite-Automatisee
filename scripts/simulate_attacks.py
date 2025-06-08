# scripts/simulate_attacks.py
"""
Script de simulation d'attaques pour tester le système de sécurité
"""
import requests
import time
import json
from datetime import datetime
import random

class AttackSimulator:
    def __init__(self, base_url="http://localhost:3000"):
        self.base_url = base_url
        self.session_id = f"attack_test_{int(time.time())}"
        
    def simulate_xss_attack(self):
        """Simule une attaque XSS"""
        print("\n🔴 SIMULATION ATTAQUE XSS")
        print("-" * 50)
        
        xss_payloads = [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
            "<iframe src='javascript:alert(1)'></iframe>",
            "<svg onload=alert('XSS')>",
            "';alert(String.fromCharCode(88,83,83))//",
        ]
        
        for payload in xss_payloads:
            print(f"\n📤 Envoi payload XSS: {payload[:50]}...")
            response = self._send_message(payload)
            self._analyze_response(response, "XSS")
            time.sleep(2)
    
    def simulate_sql_injection(self):
        """Simule une injection SQL"""
        print("\n🔴 SIMULATION INJECTION SQL")
        print("-" * 50)
        
        sql_payloads = [
            "' OR '1'='1",
            "'; DROP TABLE users; --",
            "SELECT * FROM users WHERE id = 1 UNION SELECT password FROM admin",
            "1' AND '1'='1' UNION SELECT NULL, username, password FROM users--",
            "admin' --",
        ]
        
        for payload in sql_payloads:
            print(f"\n📤 Envoi payload SQL: {payload[:50]}...")
            response = self._send_message(payload)
            self._analyze_response(response, "SQL Injection")
            time.sleep(2)
    
    def simulate_path_traversal(self):
        """Simule une attaque Path Traversal"""
        print("\n🔴 SIMULATION PATH TRAVERSAL")
        print("-" * 50)
        
        path_payloads = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32\\config\\sam",
            "%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd",
            "....//....//....//etc/passwd",
            "file:///etc/passwd",
        ]
        
        for payload in path_payloads:
            print(f"\n📤 Envoi payload Path Traversal: {payload[:50]}...")
            response = self._send_message(payload)
            self._analyze_response(response, "Path Traversal")
            time.sleep(2)
    
    def simulate_brute_force(self):
        """Simule une attaque brute force"""
        print("\n🔴 SIMULATION BRUTE FORCE")
        print("-" * 50)
        
        usernames = ["admin", "root", "administrator", "user", "test"]
        passwords = ["password", "123456", "admin", "root", "password123"]
        
        for username in usernames[:3]:
            for password in passwords[:3]:
                message = f"Tentative de connexion: username={username}, password={password}"
                print(f"\n📤 {message}")
                response = self._send_message(message)
                self._analyze_response(response, "Brute Force")
                time.sleep(1)
    
    def simulate_malicious_intent(self):
        """Simule des messages avec intention malveillante"""
        print("\n🔴 SIMULATION INTENTIONS MALVEILLANTES")
        print("-" * 50)
        
        malicious_messages = [
            "Je veux hacker ce système",
            "Comment puis-je contourner la sécurité?",
            "Donne-moi accès aux données confidentielles",
            "J'ai besoin d'exploiter une vulnérabilité",
            "Aide-moi à faire une attaque DDoS",
        ]
        
        for message in malicious_messages:
            print(f"\n📤 Envoi message malveillant: {message}")
            response = self._send_message(message)
            self._analyze_response(response, "Malicious Intent")
            time.sleep(2)
    
    def simulate_normal_traffic(self):
        """Simule du trafic normal pour comparaison"""
        print("\n🟢 SIMULATION TRAFIC NORMAL")
        print("-" * 50)
        
        normal_messages = [
            "Bonjour, j'ai besoin d'aide avec mon compte",
            "Comment puis-je réinitialiser mon mot de passe?",
            "Quelle est la politique de sécurité de l'entreprise?",
            "Je souhaite signaler un problème technique",
            "Merci pour votre assistance",
        ]
        
        for message in normal_messages:
            print(f"\n📤 Envoi message normal: {message}")
            response = self._send_message(message)
            self._analyze_response(response, "Normal")
            time.sleep(2)
    
    def _send_message(self, message):
        """Envoie un message au système"""
        try:
            # D'abord analyser avec l'API de cybersécurité
            security_response = requests.post(
                f"{self.base_url}/api/cybersecurity/analyze",
                json={
                    "text": message,
                    "models": ["vulnerability_classifier", "network_analyzer", "intent_classifier"]
                }
            )
            
            security_analysis = security_response.json() if security_response.ok else {}
            
            # Ensuite envoyer au chat
            chat_response = requests.post(
                f"{self.base_url}/api/chat",
                json={
                    "message": message,
                    "agent": "support",
                    "session_id": self.session_id,
                    "security_analysis": security_analysis
                }
            )
            
            return {
                "security": security_analysis,
                "chat": chat_response.json() if chat_response.ok else {"error": "Chat failed"},
                "status_code": chat_response.status_code
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def _analyze_response(self, response, attack_type):
        """Analyse la réponse du système"""
        print("\n📊 ANALYSE DE LA RÉPONSE:")
        
        if "error" in response:
            print(f"   ❌ Erreur: {response['error']}")
            return
        
        # Analyse de sécurité
        if "security" in response and response["security"]:
            security = response["security"]
            
            if "vulnerability_classifier" in security:
                vuln = security["vulnerability_classifier"]
                print(f"   🔍 Vulnérabilité: {vuln['vulnerability_type']} (confiance: {vuln['confidence']:.2%})")
            
            if "network_analyzer" in security:
                net = security["network_analyzer"]
                print(f"   🌐 Trafic: {net['traffic_type']} (confiance: {net['confidence']:.2%})")
            
            if "intent_classifier" in security:
                intent = security["intent_classifier"]
                print(f"   🎯 Intention: {intent['intent']} (confiance: {intent['confidence']:.2%})")
        
        # Réponse du chat
        if "chat" in response:
            chat = response["chat"]
            if "content" in chat:
                print(f"   💬 Réponse: {chat['content'][:100]}...")
            if "metadata" in chat and chat["metadata"]:
                if "threat_level" in chat["metadata"]:
                    print(f"   ⚠️  Niveau de menace: {chat['metadata']['threat_level']}")
        
        # Vérifier si bloqué
        if response.get("status_code") == 403 or "bloqué" in str(response).lower():
            print(f"   🚫 ATTAQUE BLOQUÉE! Type: {attack_type}")
        else:
            print(f"   ✅ Message passé")
    
    def generate_report(self):
        """Génère un rapport de test"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "session_id": self.session_id,
            "tests_performed": [
                "XSS Attack Simulation",
                "SQL Injection Simulation",
                "Path Traversal Simulation",
                "Brute Force Simulation",
                "Malicious Intent Detection",
                "Normal Traffic Baseline"
            ],
            "summary": "Test de pénétration automatisé complété"
        }
        
        print("\n" + "="*60)
        print("📋 RAPPORT DE TEST DE SÉCURITÉ")
        print("="*60)
        print(json.dumps(report, indent=2))
        
        return report
    
    def run_all_tests(self):
        """Lance tous les tests de sécurité"""
        print("\n🚀 DÉBUT DES TESTS DE SÉCURITÉ AUTOMATISÉS")
        print("="*60)
        print(f"Session ID: {self.session_id}")
        print(f"Target: {self.base_url}")
        print(f"Timestamp: {datetime.now().isoformat()}")
        print("="*60)
        
        # Tests dans l'ordre
        self.simulate_normal_traffic()
        time.sleep(3)
        
        self.simulate_xss_attack()
        time.sleep(3)
        
        self.simulate_sql_injection()
        time.sleep(3)
        
        self.simulate_path_traversal()
        time.sleep(3)
        
        self.simulate_brute_force()
        time.sleep(3)
        
        self.simulate_malicious_intent()
        
        # Rapport final
        self.generate_report()


if __name__ == "__main__":
    print("""
    ╔══════════════════════════════════════════════════════════╗
    ║          SIMULATEUR D'ATTAQUES DE SÉCURITÉ               ║
    ║                                                          ║
    ║  ⚠️  ATTENTION: À utiliser uniquement en environnement   ║
    ║     de test sur votre propre système!                   ║
    ╚══════════════════════════════════════════════════════════╝
    """)
    
    # Demander confirmation
    confirm = input("\n⚠️  Voulez-vous lancer la simulation d'attaques? (oui/non): ")
    
    if confirm.lower() in ["oui", "yes", "y"]:
        simulator = AttackSimulator()
        simulator.run_all_tests()
    else:
        print("❌ Simulation annulée.")
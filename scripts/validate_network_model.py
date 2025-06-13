# scripts/validate_network_model.py
"""
Script de validation pratique pour le modèle d'analyse réseau CICIDS2017
Usage: python scripts/validate_network_model.py [--full] [--interface eth0]
"""
import os
import sys
import argparse
import time
import json
from pathlib import Path
from datetime import datetime

# Ajouter le répertoire racine au path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def check_dependencies():
    """Vérifie que toutes les dépendances sont installées"""
    print("🔍 Vérification des dépendances...")
    
    required_packages = {
        'numpy': 'numpy',
        'pandas': 'pandas', 
        'sklearn': 'scikit-learn',
        'torch': 'torch',
        'xgboost': 'xgboost'
    }
    
    optional_packages = {
        'pyshark': 'pyshark',
        'scapy': 'scapy'
    }
    
    missing_required = []
    missing_optional = []
    
    for package, pip_name in required_packages.items():
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            missing_required.append(pip_name)
            print(f"❌ {package} - REQUIS")
    
    for package, pip_name in optional_packages.items():
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            missing_optional.append(pip_name)
            print(f"⚠️ {package} - optionnel")
    
    if missing_required:
        print(f"\n❌ Packages requis manquants: {', '.join(missing_required)}")
        print(f"Installer avec: pip install {' '.join(missing_required)}")
        return False
    
    if missing_optional:
        print(f"\n⚠️ Packages optionnels manquants: {', '.join(missing_optional)}")
        print(f"Pour la capture réseau: pip install {' '.join(missing_optional)}")
        print("Mode fallback sera utilisé sans ces packages")
    
    return True

def test_model_loading():
    """Test le chargement du modèle"""
    print("\n📊 Test de chargement du modèle...")
    
    try:
        from agents.cybersecurity_agent.custom_model_loaders import NetworkAnalyzerXGBoost
        
        print("🔄 Chargement du modèle XGBoost...")
        model = NetworkAnalyzerXGBoost()
        
        # Test de prédiction basique
        test_inputs = [
            "normal web traffic",
            "ddos flood attack", 
            "port scan reconnaissance"
        ]
        
        print("🧪 Test des prédictions...")
        for test_input in test_inputs:
            result = model.predict([test_input])
            print(f"   Input: '{test_input}' → {result[0] if result else 'Erreur'}")
        
        print("✅ Modèle chargé et fonctionnel!")
        return True
        
    except Exception as e:
        print(f"❌ Erreur chargement modèle: {e}")
        return False

def test_traffic_collection(interface="any", duration=10):
    """Test la collecte de trafic"""
    print(f"\n📡 Test de collecte de trafic (interface: {interface}, durée: {duration}s)...")
    
    try:
        from agents.cybersecurity_agent.traffic_collector import RealTimeTrafficCollector
        
        collector = RealTimeTrafficCollector(interface=interface)
        print(f"🔍 Méthode de capture: {collector.capture_method}")
        
        print(f"📈 Démarrage capture ({duration}s)...")
        print("💡 Générez du trafic réseau maintenant (navigation web, ping, etc.)")
        
        features_df = collector.start_capture(duration=duration, max_packets=100)
        
        if not features_df.empty:
            print(f"✅ {len(features_df)} flows capturés")
            print(f"📋 Features extraites: {len(features_df.columns)} colonnes")
            
            # Afficher quelques features
            if len(features_df) > 0:
                first_flow = features_df.iloc[0]
                print("🔍 Exemple de features extraites:")
                print(f"   Flow Duration: {first_flow.get('Flow Duration', 0):.2f}")
                print(f"   Total Fwd Packets: {first_flow.get('Total Fwd Packets', 0)}")
                print(f"   Total Backward Packets: {first_flow.get('Total Backward Packets', 0)}")
            
            return True
        else:
            print("⚠️ Aucun trafic capturé")
            return False
            
    except Exception as e:
        print(f"❌ Erreur collecte trafic: {e}")
        return False

def test_end_to_end_analysis(interface="any"):
    """Test complet d'analyse end-to-end"""
    print(f"\n🎯 Test d'analyse complète...")
    
    try:
        from agents.cybersecurity_agent.traffic_collector import RealTimeTrafficCollector
        from agents.cybersecurity_agent.custom_model_loaders import NetworkAnalyzerXGBoost
        
        # Charger le modèle
        model = NetworkAnalyzerXGBoost()
        collector = RealTimeTrafficCollector(interface=interface)
        
        print("📡 Capture de trafic pour analyse (15s)...")
        features_df = collector.start_capture(duration=15, max_packets=50)
        
        if features_df.empty:
            print("⚠️ Aucun trafic à analyser")
            return False
        
        print(f"🧠 Analyse de {len(features_df)} flows avec le modèle...")
        
        results = []
        for index, row in features_df.iterrows():
            # Convertir les features en description textuelle (simplifié)
            features_text = f"flow with {row.get('Total Fwd Packets', 0)} forward packets and {row.get('Total Backward Packets', 0)} backward packets"
            
            try:
                prediction = model.predict([features_text])
                if prediction:
                    results.append(prediction[0])
                else:
                    results.append({'label': 'ERROR', 'score': 0})
            except Exception as e:
                print(f"   ⚠️ Erreur analyse flow {index}: {e}")
                results.append({'label': 'ERROR', 'score': 0})
        
        # Statistiques des résultats
        labels = [r.get('label', 'UNKNOWN') for r in results]
        label_counts = {}
        for label in labels:
            label_counts[label] = label_counts.get(label, 0) + 1
        
        print("📊 Résultats d'analyse:")
        for label, count in label_counts.items():
            percentage = (count / len(results)) * 100
            print(f"   {label}: {count} flows ({percentage:.1f}%)")
        
        # Vérifier si des attaques ont été détectées
        attack_labels = [l for l in labels if l not in ['NORMAL', 'ERROR', 'UNKNOWN']]
        if attack_labels:
            print(f"🚨 Attaques potentielles détectées: {set(attack_labels)}")
        else:
            print("✅ Aucune attaque détectée - trafic semble normal")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur analyse end-to-end: {e}")
        return False

def run_full_validation():
    """Lance la validation complète avec le système intégré"""
    print("\n🚀 VALIDATION COMPLÈTE DU MODÈLE")
    print("="*50)
    
    try:
        from agents.cybersecurity_agent.traffic_collector import NetworkModelValidator
        
        validator = NetworkModelValidator()
        
        print("⏳ Exécution de la suite de validation complète...")
        print("📝 Cela peut prendre quelques minutes...")
        
        results = validator.run_validation_suite()
        
        # Générer et afficher le rapport
        report = validator.generate_validation_report(results)
        print("\n" + report)
        
        # Sauvegarder le rapport
        report_file = f"data/validation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        os.makedirs(os.path.dirname(report_file), exist_ok=True)
        
        with open(report_file, 'w') as f:
            f.write(report)
        
        print(f"\n💾 Rapport sauvegardé: {report_file}")
        
        return results['overall_success']
        
    except Exception as e:
        print(f"❌ Erreur validation complète: {e}")
        return False

def simulate_attacks():
    """Simule des attaques pour tester la détection"""
    print("\n🎭 Simulation d'attaques pour test...")
    
    attack_simulations = [
        {
            'name': 'Port Scan',
            'command': 'nmap -sS -F 127.0.0.1',
            'description': 'Scan de ports TCP sur localhost'
        },
        {
            'name': 'SYN Flood (léger)',
            'command': 'hping3 -S -p 80 -c 50 -i u100 127.0.0.1',
            'description': 'Attaque SYN flood légère'
        },
        {
            'name': 'Ping Flood (léger)',
            'command': 'ping -f -c 100 127.0.0.1',
            'description': 'Flood de pings'
        }
    ]
    
    print("📋 Attaques disponibles pour simulation:")
    for i, attack in enumerate(attack_simulations, 1):
        print(f"   {i}. {attack['name']}: {attack['description']}")
        print(f"      Commande: {attack['command']}")
    
    print("\n⚠️ ATTENTION: Ces simulations sont à des fins de test uniquement!")
    print("💡 Lancez ces commandes manuellement dans un autre terminal pendant la capture")
    print("🔧 Assurez-vous d'avoir les outils installés (nmap, hping3)")
    
    choice = input("\nVoulez-vous des instructions détaillées? (y/N): ")
    
    if choice.lower() == 'y':
        print("\n📖 INSTRUCTIONS DÉTAILLÉES:")
        print("1. Ouvrez un nouveau terminal")
        print("2. Pendant que le script capture le trafic, lancez une des commandes ci-dessus")
        print("3. Exemple complet:")
        print("   Terminal 1: python scripts/validate_network_model.py --test-traffic")
        print("   Terminal 2: nmap -sS -F 127.0.0.1")
        print("4. Observez les résultats de détection")

def check_network_interfaces():
    """Affiche les interfaces réseau disponibles"""
    print("\n🌐 Interfaces réseau disponibles:")
    
    try:
        import psutil
        
        interfaces = psutil.net_if_addrs()
        for interface, addresses in interfaces.items():
            status = "UP" if interface in psutil.net_if_stats() and psutil.net_if_stats()[interface].isup else "DOWN"
            print(f"   📡 {interface}: {status}")
            
            for addr in addresses:
                if addr.family == 2:  # IPv4
                    print(f"      IPv4: {addr.address}")
    
    except ImportError:
        print("⚠️ psutil non disponible - utiliser 'ip addr' ou 'ifconfig'")
        
        # Fallback avec commandes système
        try:
            import subprocess
            result = subprocess.run(['ip', 'addr'], capture_output=True, text=True)
            if result.returncode == 0:
                lines = result.stdout.split('\n')
                for line in lines:
                    if ': ' in line and 'inet ' not in line:
                        parts = line.split(': ')
                        if len(parts) > 1:
                            interface = parts[1].split('@')[0]
                            print(f"   📡 {interface}")
        except:
            print("⚠️ Utilisez 'ip addr' ou 'ifconfig' pour voir les interfaces")

def create_requirements_file():
    """Crée un fichier requirements.txt pour les dépendances"""
    requirements = [
        "numpy>=1.21.0",
        "pandas>=1.3.0", 
        "scikit-learn>=1.0.0",
        "torch>=1.9.0",
        "xgboost>=1.5.0",
        "transformers>=4.15.0",
        "huggingface-hub>=0.11.0",
        "# Optional - pour capture réseau",
        "pyshark>=0.4.5",
        "scapy>=2.4.5",
        "psutil>=5.8.0"
    ]
    
    req_file = "requirements_network_validation.txt"
    
    with open(req_file, 'w') as f:
        f.write('\n'.join(requirements))
    
    print(f"📝 Fichier créé: {req_file}")
    print(f"🔧 Installation: pip install -r {req_file}")

def main():
    parser = argparse.ArgumentParser(description="Validation du modèle d'analyse réseau CICIDS2017")
    
    parser.add_argument('--full', action='store_true', 
                       help='Lance la validation complète')
    parser.add_argument('--interface', default='any',
                       help='Interface réseau à utiliser (défaut: any)')
    parser.add_argument('--duration', type=int, default=15,
                       help='Durée de capture en secondes (défaut: 15)')
    parser.add_argument('--check-deps', action='store_true',
                       help='Vérifie seulement les dépendances')
    parser.add_argument('--test-model', action='store_true',
                       help='Test seulement le chargement du modèle')
    parser.add_argument('--test-traffic', action='store_true',
                       help='Test seulement la capture de trafic')
    parser.add_argument('--simulate-attacks', action='store_true',
                       help='Affiche les instructions pour simuler des attaques')
    parser.add_argument('--interfaces', action='store_true',
                       help='Affiche les interfaces réseau disponibles')
    parser.add_argument('--create-requirements', action='store_true',
                       help='Crée un fichier requirements.txt')
    
    args = parser.parse_args()
    
    print("🚀 VALIDATION MODÈLE RÉSEAU CICIDS2017")
    print("="*50)
    print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🖥️ Interface: {args.interface}")
    print("")
    
    success = True
    
    # Actions spécifiques
    if args.create_requirements:
        create_requirements_file()
        return
    
    if args.interfaces:
        check_network_interfaces()
        return
    
    if args.simulate_attacks:
        simulate_attacks()
        return
    
    # Vérification des dépendances (toujours)
    if not check_dependencies():
        print("\n❌ Impossible de continuer sans les dépendances requises")
        print("💡 Utilisez --create-requirements pour générer le fichier d'installation")
        return 1
    
    # Tests spécifiques
    if args.check_deps:
        print("\n✅ Toutes les dépendances sont installées!")
        return 0
    
    if args.test_model:
        success = test_model_loading()
    
    elif args.test_traffic:
        success = test_traffic_collection(args.interface, args.duration)
    
    elif args.full:
        success = run_full_validation()
    
    else:
        # Test rapide par défaut
        print("🔬 VALIDATION RAPIDE")
        print("-" * 30)
        
        # 1. Test modèle
        if not test_model_loading():
            success = False
        
        # 2. Test capture
        if success and not test_traffic_collection(args.interface, args.duration):
            success = False
        
        # 3. Test end-to-end
        if success and not test_end_to_end_analysis(args.interface):
            success = False
        
        print("\n" + "="*50)
        if success:
            print("✅ VALIDATION RAPIDE RÉUSSIE!")
            print("💡 Pour une validation complète: --full")
            print("🎭 Pour tester avec des attaques: --simulate-attacks")
        else:
            print("❌ VALIDATION ÉCHOUÉE!")
            print("🔧 Vérifiez les erreurs ci-dessus")
    
    print("\n📖 Autres options utiles:")
    print("   --interfaces     : Voir les interfaces réseau")
    print("   --test-model     : Tester seulement le modèle")
    print("   --test-traffic   : Tester seulement la capture")
    print("   --simulate-attacks : Instructions simulation d'attaques")
    print("   --create-requirements : Créer requirements.txt")
    
    return 0 if success else 1

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⏹️ Arrêt demandé par l'utilisateur")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erreur inattendue: {e}")
        print("🐛 Veuillez reporter ce bug avec les détails ci-dessus")
        sys.exit(1)
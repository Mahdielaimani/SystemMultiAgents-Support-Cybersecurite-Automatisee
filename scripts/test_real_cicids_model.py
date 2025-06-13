# scripts/test_real_cicids_model.py
"""
Script pour tester le VRAI modèle CICIDS2017 depuis HuggingFace
"""
import sys
import numpy as np
import pandas as pd
from pathlib import Path

# Ajouter le répertoire racine au path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_model_download():
    """Test le téléchargement et chargement du vrai modèle"""
    print("🔄 TEST TÉLÉCHARGEMENT VRAI MODÈLE")
    print("="*40)
    
    try:
        from agents.cybersecurity_agent.real_cicids_model import RealNetworkAnalyzerCICIDS
        
        # Charger le modèle
        model = RealNetworkAnalyzerCICIDS()
        
        # Vérifier le chargement
        info = model.get_model_info()
        
        print(f"📊 Repo ID: {info['repo_id']}")
        print(f"✅ Modèle chargé: {info['is_loaded']}")
        print(f"🔧 Type: {info['model_type']}")
        print(f"📈 Features: {info['features_count']}")
        print(f"🏷️ Classes: {info['classes']}")
        print(f"⚖️ Scaler disponible: {info['has_scaler']}")
        print(f"🎯 Feature selector: {info['has_feature_selector']}")
        
        return model, info['is_loaded']
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return None, False

def test_real_predictions(model):
    """Test des prédictions avec le vrai modèle"""
    print("\n🧪 TEST PRÉDICTIONS VRAI MODÈLE")
    print("="*40)
    
    if not model.is_loaded:
        print("❌ Modèle non chargé - impossible de tester")
        return False
    
    try:
        # Créer des données de test réalistes
        feature_names = model.feature_names
        
        # Scénario 1: Trafic normal
        print("📊 Test 1: Trafic Normal")
        normal_data = {}
        for name in feature_names:
            if 'Duration' in name:
                normal_data[name] = [1500000]  # 1.5 secondes en microsecondes
            elif 'Packets' in name:
                normal_data[name] = [10]  # Peu de paquets
            elif 'Length' in name or 'Bytes' in name:
                normal_data[name] = [500]  # Taille normale
            elif 'Flag' in name:
                normal_data[name] = [2]  # Quelques flags
            else:
                normal_data[name] = [np.random.uniform(0, 100)]
        
        normal_df = pd.DataFrame(normal_data)
        normal_result = model.predict_from_features(normal_df)
        print(f"   Prédiction: {normal_result[0]['label']} (confiance: {normal_result[0]['confidence']:.2f})")
        
        # Scénario 2: Trafic suspect (beaucoup de paquets)
        print("\n📊 Test 2: Trafic Suspect (Volume élevé)")
        suspect_data = {}
        for name in feature_names:
            if 'Duration' in name:
                suspect_data[name] = [100000]  # Très court
            elif 'Fwd Packets' in name or 'Total Fwd' in name:
                suspect_data[name] = [1000]  # Beaucoup de paquets
            elif 'Backward' in name:
                suspect_data[name] = [0]  # Pas de réponse
            elif 'SYN Flag' in name:
                suspect_data[name] = [500]  # Beaucoup de SYN
            elif 'Length' in name:
                suspect_data[name] = [40]  # Petits paquets
            else:
                suspect_data[name] = [np.random.uniform(0, 50)]
        
        suspect_df = pd.DataFrame(suspect_data)
        suspect_result = model.predict_from_features(suspect_df)
        print(f"   Prédiction: {suspect_result[0]['label']} (confiance: {suspect_result[0]['confidence']:.2f})")
        
        # Scénario 3: Multiple flows
        print("\n📊 Test 3: Analyse Multiple Flows")
        multi_data = {}
        n_flows = 5
        
        for name in feature_names:
            multi_data[name] = [np.random.uniform(0, 1000) for _ in range(n_flows)]
        
        multi_df = pd.DataFrame(multi_data)
        multi_results = model.predict_from_features(multi_df)
        
        for i, result in enumerate(multi_results):
            print(f"   Flow {i+1}: {result['label']} (confiance: {result['confidence']:.2f})")
        
        # Statistiques
        labels = [r['label'] for r in multi_results]
        unique_labels = set(labels)
        print(f"\n📈 Résumé: {len(unique_labels)} types détectés: {unique_labels}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur test prédictions: {e}")
        return False

def compare_with_simulation():
    """Compare le vrai modèle avec la simulation"""
    print("\n🔄 COMPARAISON VRAI MODÈLE vs SIMULATION")
    print("="*50)
    
    try:
        # Charger le vrai modèle
        from agents.cybersecurity_agent.real_cicids_model import RealNetworkAnalyzerCICIDS
        real_model = RealNetworkAnalyzerCICIDS()
        
        # Charger l'ancien modèle (simulation)
        from agents.cybersecurity_agent.custom_model_loaders import NetworkAnalyzerXGBoost
        sim_model = NetworkAnalyzerXGBoost()
        
        # Tests avec descriptions textuelles
        test_descriptions = [
            "normal web browsing traffic",
            "ddos attack high volume",
            "port scan reconnaissance",
            "brute force login attempts",
            "botnet malicious activity"
        ]
        
        print("📊 Comparaison des prédictions:")
        print(f"{'Description':<30} {'Simulation':<15} {'Vrai Modèle':<15}")
        print("-" * 65)
        
        for desc in test_descriptions:
            # Prédiction simulation
            sim_result = sim_model.predict([desc])
            sim_label = sim_result[0]['label'] if sim_result else "ERROR"
            
            # Pour le vrai modèle, on doit utiliser des features
            if real_model.is_loaded:
                # Créer des features factices basées sur la description
                features = create_features_from_description(desc, real_model.feature_names)
                real_result = real_model.predict_from_features(features)
                real_label = real_result[0]['label'] if real_result else "ERROR"
            else:
                real_label = "NOT_LOADED"
            
            print(f"{desc:<30} {sim_label:<15} {real_label:<15}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur comparaison: {e}")
        return False

def create_features_from_description(description: str, feature_names: list) -> pd.DataFrame:
    """Crée des features réalistes basées sur une description"""
    desc_lower = description.lower()
    features = {}
    
    for name in feature_names:
        if "ddos" in desc_lower or "flood" in desc_lower:
            # Patterns DDoS
            if 'Fwd Packets' in name:
                features[name] = [2000]  # Beaucoup de paquets
            elif 'Duration' in name:
                features[name] = [50000]  # Court
            elif 'SYN Flag' in name:
                features[name] = [1000]  # Beaucoup de SYN
            else:
                features[name] = [np.random.uniform(100, 2000)]
                
        elif "port scan" in desc_lower or "reconnaissance" in desc_lower:
            # Patterns Port Scan
            if 'Fwd Packets' in name:
                features[name] = [100]  # Paquets moyens
            elif 'Duration' in name:
                features[name] = [5000000]  # Long scan
            elif 'Length' in name:
                features[name] = [40]  # Petits paquets
            else:
                features[name] = [np.random.uniform(1, 200)]
                
        elif "brute force" in desc_lower:
            # Patterns Brute Force
            if 'Fwd Packets' in name:
                features[name] = [50]  # Tentatives répétées
            elif 'Duration' in name:
                features[name] = [30000000]  # Longue durée
            else:
                features[name] = [np.random.uniform(10, 500)]
                
        else:
            # Trafic normal
            if 'Fwd Packets' in name:
                features[name] = [10]  # Peu de paquets
            elif 'Duration' in name:
                features[name] = [1000000]  # Durée normale
            elif 'Length' in name:
                features[name] = [500]  # Taille normale
            else:
                features[name] = [np.random.uniform(0, 100)]
    
    return pd.DataFrame(features)

def main():
    print("🚀 TEST COMPLET DU VRAI MODÈLE CICIDS2017")
    print("="*50)
    
    # Test 1: Téléchargement et chargement
    model, is_loaded = test_model_download()
    
    if not model:
        print("❌ Impossible de charger le modèle")
        return
    
    # Test 2: Prédictions si modèle chargé
    if is_loaded:
        success = test_real_predictions(model)
        if success:
            print("✅ Tests de prédictions réussis")
        else:
            print("❌ Problème avec les prédictions")
    else:
        print("⚠️ Modèle non chargé - vérifiez votre repo HuggingFace")
    
    # Test 3: Comparaison
    compare_with_simulation()
    
    # Conclusion
    print(f"\n{'='*50}")
    if is_loaded:
        print("🎉 VRAI MODÈLE CICIDS2017 FONCTIONNEL!")
        print("💡 Votre modèle HuggingFace est correctement chargé et utilisable")
        print("🔧 Remplacez l'ancien code par le nouveau pour utiliser le vrai modèle")
    else:
        print("⚠️ VRAI MODÈLE NON CHARGÉ")
        print("🔍 Vérifiez:")
        print("   - Connexion internet")
        print("   - Repo HuggingFace accessible")
        print("   - Fichiers .pkl présents dans le repo")
        print("   - Format des fichiers compatible")

if __name__ == "__main__":
    main()
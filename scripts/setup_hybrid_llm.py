#!/usr/bin/env python3
"""
Configuration LLM hybride : OpenAI -> Mistral 7B en cas de dépassement
"""

import os
import sys
import subprocess
import json
import requests
import time
from pathlib import Path

def print_header(title):
    print(f"\n🚀 {title}")
    print("=" * 60)

def print_success(message):
    print(f"✅ {message}")

def print_error(message):
    print(f"❌ {message}")

def print_info(message):
    print(f"🔧 {message}")

def install_ollama_if_needed():
    """Installe Ollama si nécessaire"""
    print_header("VÉRIFICATION OLLAMA")
    
    try:
        result = subprocess.run(['ollama', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print_success(f"Ollama déjà installé: {result.stdout.strip()}")
            return True
    except FileNotFoundError:
        pass
    
    print_info("Installation d'Ollama...")
    try:
        install_cmd = "curl -fsSL https://ollama.ai/install.sh | sh"
        result = subprocess.run(install_cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            print_success("Ollama installé avec succès")
            return True
        else:
            print_error(f"Erreur installation: {result.stderr}")
            return False
    except Exception as e:
        print_error(f"Erreur: {e}")
        return False

def setup_mistral_7b():
    """Configure Mistral 7B comme fallback"""
    print_header("CONFIGURATION MISTRAL 7B")
    
    # Démarrer Ollama
    try:
        subprocess.Popen(['ollama', 'serve'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(3)
        print_info("Service Ollama démarré")
    except:
        pass
    
    # Télécharger Mistral 7B
    print_info("Téléchargement de Mistral 7B... (peut prendre du temps)")
    try:
        result = subprocess.run(['ollama', 'pull', 'mistral:7b'], capture_output=True, text=True)
        if result.returncode == 0:
            print_success("Mistral 7B téléchargé")
            return True
        else:
            print_error(f"Erreur téléchargement: {result.stderr}")
            # Essayer la version instruct plus petite
            print_info("Essai avec mistral:7b-instruct...")
            result = subprocess.run(['ollama', 'pull', 'mistral:7b-instruct'], capture_output=True, text=True)
            if result.returncode == 0:
                print_success("Mistral 7B Instruct téléchargé")
                return True
            return False
    except Exception as e:
        print_error(f"Erreur: {e}")
        return False

def create_hybrid_llm_manager():
    """Crée le gestionnaire LLM hybride"""
    print_header("CRÉATION GESTIONNAIRE HYBRIDE")
    
    hybrid_manager_code = '''
import os
import json
import time
import requests
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

class HybridLLMManager:
    """Gestionnaire LLM hybride : OpenAI -> Mistral 7B"""
    
    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.ollama_url = "http://localhost:11434"
        self.mistral_model = "mistral:7b-instruct"
        
        # Configuration des limites
        self.token_limit_per_hour = 10000  # Limite tokens/heure
        self.token_limit_per_day = 50000   # Limite tokens/jour
        
        # Tracking des tokens
        self.token_usage_file = "config/token_usage.json"
        self.load_token_usage()
        
        # État du système
        self.openai_available = self._check_openai()
        self.mistral_available = self._check_mistral()
        self.current_provider = "openai" if self.openai_available else "mistral"
        
        print(f"🤖 LLM Manager initialisé - Provider: {self.current_provider}")
    
    def _check_openai(self) -> bool:
        """Vérifie la disponibilité d'OpenAI"""
        if not self.openai_api_key:
            return False
        
        try:
            from langchain_openai import ChatOpenAI
            llm = ChatOpenAI(
                model="gpt-3.5-turbo",
                openai_api_key=self.openai_api_key,
                max_tokens=10  # Test minimal
            )
            # Test simple
            response = llm.invoke([{"role": "user", "content": "test"}])
            return True
        except Exception as e:
            error_str = str(e).lower()
            if "quota" in error_str or "429" in error_str:
                print("⚠️ Quota OpenAI dépassé")
                return False
            elif "401" in error_str or "invalid" in error_str:
                print("⚠️ Clé OpenAI invalide")
                return False
            return False
    
    def _check_mistral(self) -> bool:
        """Vérifie la disponibilité de Mistral"""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get("models", [])
                for model in models:
                    if "mistral" in model.get("name", "").lower():
                        return True
            return False
        except:
            return False
    
    def load_token_usage(self):
        """Charge l'utilisation des tokens"""
        try:
            if os.path.exists(self.token_usage_file):
                with open(self.token_usage_file, 'r') as f:
                    self.token_usage = json.load(f)
            else:
                self.token_usage = {
                    "daily": {"date": "", "tokens": 0},
                    "hourly": {"hour": "", "tokens": 0}
                }
        except:
            self.token_usage = {
                "daily": {"date": "", "tokens": 0},
                "hourly": {"hour": "", "tokens": 0}
            }
    
    def save_token_usage(self):
        """Sauvegarde l'utilisation des tokens"""
        try:
            os.makedirs(os.path.dirname(self.token_usage_file), exist_ok=True)
            with open(self.token_usage_file, 'w') as f:
                json.dump(self.token_usage, f, indent=2)
        except:
            pass
    
    def update_token_usage(self, tokens: int):
        """Met à jour le compteur de tokens"""
        now = datetime.now()
        today = now.strftime("%Y-%m-%d")
        current_hour = now.strftime("%Y-%m-%d-%H")
        
        # Reset daily counter if new day
        if self.token_usage["daily"]["date"] != today:
            self.token_usage["daily"] = {"date": today, "tokens": 0}
        
        # Reset hourly counter if new hour
        if self.token_usage["hourly"]["hour"] != current_hour:
            self.token_usage["hourly"] = {"hour": current_hour, "tokens": 0}
        
        # Add tokens
        self.token_usage["daily"]["tokens"] += tokens
        self.token_usage["hourly"]["tokens"] += tokens
        
        self.save_token_usage()
    
    def should_use_openai(self) -> bool:
        """Détermine si on peut utiliser OpenAI"""
        if not self.openai_available:
            return False
        
        # Vérifier les limites de tokens
        if self.token_usage["hourly"]["tokens"] >= self.token_limit_per_hour:
            print("⚠️ Limite horaire atteinte, basculement vers Mistral")
            return False
        
        if self.token_usage["daily"]["tokens"] >= self.token_limit_per_day:
            print("⚠️ Limite quotidienne atteinte, basculement vers Mistral")
            return False
        
        return True
    
    def generate_with_openai(self, prompt: str, system_prompt: str = None) -> str:
        """Génère avec OpenAI"""
        try:
            from langchain_openai import ChatOpenAI
            from langchain.schema import HumanMessage, SystemMessage
            
            llm = ChatOpenAI(
                model="gpt-3.5-turbo",
                temperature=0.1,
                openai_api_key=self.openai_api_key
            )
            
            messages = []
            if system_prompt:
                messages.append(SystemMessage(content=system_prompt))
            messages.append(HumanMessage(content=prompt))
            
            response = llm.invoke(messages)
            
            # Estimer les tokens utilisés (approximation)
            estimated_tokens = len(prompt.split()) + len(response.content.split())
            self.update_token_usage(estimated_tokens)
            
            return response.content
            
        except Exception as e:
            error_str = str(e).lower()
            if "quota" in error_str or "429" in error_str:
                print("🔄 Quota OpenAI dépassé, basculement vers Mistral")
                self.openai_available = False
                return self.generate_with_mistral(prompt, system_prompt)
            else:
                raise e
    
    def generate_with_mistral(self, prompt: str, system_prompt: str = None) -> str:
        """Génère avec Mistral 7B"""
        try:
            full_prompt = prompt
            if system_prompt:
                full_prompt = f"<s>[INST] {system_prompt}\\n\\n{prompt} [/INST]"
            
            payload = {
                "model": self.mistral_model,
                "prompt": full_prompt,
                "stream": False,
                "options": {
                    "temperature": 0.1,
                    "top_p": 0.9
                }
            }
            
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json=payload,
                timeout=120
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("response", "Erreur de génération")
            else:
                return f"Erreur Mistral: {response.status_code}"
                
        except Exception as e:
            return f"Erreur Mistral: {str(e)}"
    
    def generate(self, prompt: str, system_prompt: str = None) -> str:
        """Génère une réponse avec le meilleur provider disponible"""
        # Essayer OpenAI en premier si disponible
        if self.should_use_openai():
            try:
                return self.generate_with_openai(prompt, system_prompt)
            except Exception as e:
                print(f"⚠️ Erreur OpenAI: {e}")
                print("🔄 Basculement vers Mistral")
        
        # Fallback vers Mistral
        if self.mistral_available:
            return self.generate_with_mistral(prompt, system_prompt)
        else:
            return "❌ Aucun LLM disponible. Vérifiez votre configuration."
    
    def get_status(self) -> Dict[str, Any]:
        """Retourne le statut du système"""
        return {
            "openai_available": self.openai_available,
            "mistral_available": self.mistral_available,
            "current_provider": self.current_provider,
            "token_usage": self.token_usage,
            "limits": {
                "hourly": self.token_limit_per_hour,
                "daily": self.token_limit_per_day
            }
        }

# Instance globale
hybrid_llm = HybridLLMManager()
'''
    
    # Créer le fichier
    manager_file = "utils/hybrid_llm_manager.py"
    os.makedirs("utils", exist_ok=True)
    
    with open(manager_file, 'w', encoding='utf-8') as f:
        f.write(hybrid_manager_code)
    
    print_success(f"Gestionnaire hybride créé: {manager_file}")
    return True

def main():
    """Fonction principale"""
    print_header("CONFIGURATION LLM HYBRIDE : OPENAI -> MISTRAL 7B")
    
    steps = [
        ("Installation Ollama", install_ollama_if_needed),
        ("Configuration Mistral 7B", setup_mistral_7b),
        ("Gestionnaire hybride", create_hybrid_llm_manager)
    ]
    
    success_count = 0
    
    for step_name, step_func in steps:
        print_info(f"Étape: {step_name}")
        try:
            if step_func():
                success_count += 1
            else:
                print_error(f"Échec: {step_name}")
        except Exception as e:
            print_error(f"Erreur {step_name}: {e}")
    
    print_header("RÉSUMÉ CONFIGURATION HYBRIDE")
    print(f"✅ Étapes réussies: {success_count}/{len(steps)}")
    
    if success_count >= 2:
        print_success("🎉 SYSTÈME HYBRIDE CONFIGURÉ!")
        print_info("Fonctionnalités:")
        print_info("- 🔄 Basculement automatique OpenAI -> Mistral")
        print_info("- 📊 Monitoring des tokens en temps réel")
        print_info("- ⚡ Optimisation des coûts")
        print_info("- 🛡️ Fallback robuste")
        print("")
        print_info("Commandes utiles:")
        print_info("- Monitoring: python scripts/monitor_tokens.py")
        print_info("- Test: python agents/support_agent/agentic_support_agent_hybrid.py")
        print_info("- Redémarrer API: python api/server.py")
    else:
        print_error("⚠️ Configuration incomplète")
    
    return success_count >= 2

if __name__ == "__main__":
    main()

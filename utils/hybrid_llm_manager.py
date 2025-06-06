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
        
        # Configuration des limites (ajustables)
        self.token_limit_per_hour = 8000   # Limite tokens/heure (conservateur)
        self.token_limit_per_day = 40000   # Limite tokens/jour (conservateur)
        
        # Tracking des tokens
        self.token_usage_file = "config/token_usage.json"
        self.load_token_usage()
        
        # État du système - OpenAI disponible si clé présente
        self.openai_available = bool(self.openai_api_key)
        self.mistral_available = self._check_mistral()
        self.current_provider = "openai" if self.openai_available else "mistral"
        
        print(f"🤖 LLM Manager initialisé")
        print(f"   🔑 OpenAI: {'✅ Disponible' if self.openai_available else '❌ Pas de clé'}")
        print(f"   🦙 Mistral: {'✅ Disponible' if self.mistral_available else '❌ Non installé'}")
        print(f"   🎯 Provider actuel: {self.current_provider}")
    
    def _check_mistral(self) -> bool:
        """Vérifie la disponibilité de Mistral (sans test coûteux)"""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=3)
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
        
        # Log usage
        print(f"📊 Tokens utilisés: +{tokens} (Total jour: {self.token_usage['daily']['tokens']}, Heure: {self.token_usage['hourly']['tokens']})")
    
    def should_use_openai(self) -> bool:
        """Détermine si on peut utiliser OpenAI"""
        if not self.openai_available:
            return False
        
        # Vérifier les limites de tokens
        if self.token_usage["hourly"]["tokens"] >= self.token_limit_per_hour:
            print(f"⚠️ Limite horaire atteinte ({self.token_usage['hourly']['tokens']}/{self.token_limit_per_hour})")
            return False
        
        if self.token_usage["daily"]["tokens"] >= self.token_limit_per_day:
            print(f"⚠️ Limite quotidienne atteinte ({self.token_usage['daily']['tokens']}/{self.token_limit_per_day})")
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
                max_tokens=500,  # Limite pour contrôler les coûts
                openai_api_key=self.openai_api_key
            )
            
            messages = []
            if system_prompt:
                messages.append(SystemMessage(content=system_prompt))
            messages.append(HumanMessage(content=prompt))
            
            print("🔄 Génération avec OpenAI...")
            response = llm.invoke(messages)
            
            # Estimer les tokens utilisés (approximation)
            estimated_tokens = len(prompt.split()) + len(response.content.split()) + (len(system_prompt.split()) if system_prompt else 0)
            self.update_token_usage(estimated_tokens)
            
            print(f"✅ Réponse OpenAI générée ({len(response.content)} chars)")
            return response.content
            
        except Exception as e:
            error_str = str(e).lower()
            print(f"❌ Erreur OpenAI: {e}")
            
            # Vérifier si c'est vraiment un problème de quota
            if any(keyword in error_str for keyword in ["quota", "429", "rate limit", "insufficient"]):
                print("🔄 Quota OpenAI épuisé, basculement vers Mistral")
                self.openai_available = False  # Désactiver temporairement
                return self.generate_with_mistral(prompt, system_prompt)
            elif any(keyword in error_str for keyword in ["401", "invalid", "unauthorized"]):
                print("🔄 Clé OpenAI invalide, basculement vers Mistral")
                self.openai_available = False
                return self.generate_with_mistral(prompt, system_prompt)
            else:
                # Autre erreur, essayer Mistral
                print("🔄 Erreur OpenAI, tentative avec Mistral")
                return self.generate_with_mistral(prompt, system_prompt)
    
    def generate_with_mistral(self, prompt: str, system_prompt: str = None) -> str:
        """Génère avec Mistral 7B"""
        try:
            # Format Mistral avec instructions
            if system_prompt:
                full_prompt = f"<s>[INST] {system_prompt}\n\nQuestion: {prompt} [/INST]"
            else:
                full_prompt = f"<s>[INST] {prompt} [/INST]"
            
            payload = {
                "model": self.mistral_model,
                "prompt": full_prompt,
                "stream": False,
                "options": {
                    "temperature": 0.1,
                    "top_p": 0.9,
                    "max_tokens": 500
                }
            }
            
            print("🦙 Génération avec Mistral 7B...")
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result.get("response", "Erreur de génération")
                print(f"✅ Réponse Mistral générée ({len(content)} chars)")
                return content
            else:
                return f"Erreur Mistral HTTP {response.status_code}"
                
        except Exception as e:
            print(f"❌ Erreur Mistral: {e}")
            return f"Désolé, j'ai rencontré un problème technique. Erreur: {str(e)}"
    
    def generate(self, prompt: str, system_prompt: str = None) -> str:
        """Génère une réponse avec le meilleur provider disponible"""
        
        # Essayer OpenAI en premier si disponible et dans les limites
        if self.should_use_openai():
            try:
                self.current_provider = "openai"
                return self.generate_with_openai(prompt, system_prompt)
            except Exception as e:
                print(f"⚠️ Échec OpenAI: {e}")
        
        # Fallback vers Mistral
        if self.mistral_available:
            self.current_provider = "mistral"
            return self.generate_with_mistral(prompt, system_prompt)
        else:
            return "❌ Aucun LLM disponible. Vérifiez votre configuration OpenAI ou installez Mistral avec Ollama."
    
    def reset_openai_availability(self):
        """Réactive OpenAI (utile après une pause)"""
        if self.openai_api_key:
            self.openai_available = True
            print("🔄 OpenAI réactivé")
    
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
            },
            "usage_percentage": {
                "hourly": round((self.token_usage["hourly"]["tokens"] / self.token_limit_per_hour) * 100, 1),
                "daily": round((self.token_usage["daily"]["tokens"] / self.token_limit_per_day) * 100, 1)
            }
        }

# Instance globale
hybrid_llm = HybridLLMManager()

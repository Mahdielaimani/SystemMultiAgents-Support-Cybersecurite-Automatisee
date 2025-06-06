import os
import json
import time
import requests
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

class HybridLLMManagerGemini:
    """Gestionnaire LLM hybride : Google Gemini -> Mistral 7B"""
    
    def __init__(self):
        self.google_api_key = os.getenv("GOOGLE_API_KEY")
        self.gemini_model = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
        self.ollama_url = "http://localhost:11434"
        self.mistral_model = "mistral:7b-instruct"
        
        # Configuration des limites (Gemini a des quotas généreux)
        self.token_limit_per_hour = 15000   # Limite tokens/heure
        self.token_limit_per_day = 100000   # Limite tokens/jour
        
        # Tracking des tokens
        self.token_usage_file = "config/token_usage_gemini.json"
        self.load_token_usage()
        
        # État du système - Gemini disponible si clé présente
        self.gemini_available = bool(self.google_api_key)
        self.mistral_available = self._check_mistral()
        self.current_provider = "gemini" if self.gemini_available else "mistral"
        
        print(f"🤖 LLM Manager Gemini initialisé")
        print(f"   🔑 Gemini: {'✅ Disponible' if self.gemini_available else '❌ Pas de clé'}")
        print(f"   🦙 Mistral: {'✅ Disponible' if self.mistral_available else '❌ Non installé'}")
        print(f"   🎯 Provider actuel: {self.current_provider}")
    
    def _check_mistral(self) -> bool:
        """Vérifie la disponibilité de Mistral"""
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
    
    def should_use_gemini(self) -> bool:
        """Détermine si on peut utiliser Gemini"""
        if not self.gemini_available:
            return False
        
        # Vérifier les limites de tokens
        if self.token_usage["hourly"]["tokens"] >= self.token_limit_per_hour:
            print(f"⚠️ Limite horaire atteinte ({self.token_usage['hourly']['tokens']}/{self.token_limit_per_hour})")
            return False
        
        if self.token_usage["daily"]["tokens"] >= self.token_limit_per_day:
            print(f"⚠️ Limite quotidienne atteinte ({self.token_usage['daily']['tokens']}/{self.token_limit_per_day})")
            return False
        
        return True
    
    def generate_with_gemini(self, prompt: str, system_prompt: str = None) -> str:
        """Génère avec Google Gemini"""
        try:
            import google.generativeai as genai
            
            # Configuration Gemini
            genai.configure(api_key=self.google_api_key)
            model = genai.GenerativeModel(self.gemini_model)
            
            # Construire le prompt complet
            if system_prompt:
                full_prompt = f"{system_prompt}\n\nQuestion: {prompt}"
            else:
                full_prompt = prompt
            
            print("🔄 Génération avec Google Gemini...")
            
            # Configuration de génération
            generation_config = genai.types.GenerationConfig(
                temperature=0.1,
                max_output_tokens=500,
                top_p=0.9,
            )
            
            response = model.generate_content(
                full_prompt,
                generation_config=generation_config
            )
            
            if response.text:
                # Estimer les tokens utilisés
                estimated_tokens = len(prompt.split()) + len(response.text.split()) + (len(system_prompt.split()) if system_prompt else 0)
                self.update_token_usage(estimated_tokens)
                
                print(f"✅ Réponse Gemini générée ({len(response.text)} chars)")
                return response.text
            else:
                return "Erreur: Réponse vide de Gemini"
            
        except Exception as e:
            error_str = str(e).lower()
            print(f"❌ Erreur Gemini: {e}")
            
            # Vérifier si c'est un problème de quota
            if any(keyword in error_str for keyword in ["quota", "429", "rate limit", "resource_exhausted"]):
                print("🔄 Quota Gemini épuisé, basculement vers Mistral")
                self.gemini_available = False
                return self.generate_with_mistral(prompt, system_prompt)
            elif any(keyword in error_str for keyword in ["401", "invalid", "unauthorized", "api_key"]):
                print("🔄 Clé Gemini invalide, basculement vers Mistral")
                self.gemini_available = False
                return self.generate_with_mistral(prompt, system_prompt)
            else:
                print("🔄 Erreur Gemini, tentative avec Mistral")
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
        
        # Essayer Gemini en premier si disponible et dans les limites
        if self.should_use_gemini():
            try:
                self.current_provider = "gemini"
                return self.generate_with_gemini(prompt, system_prompt)
            except Exception as e:
                print(f"⚠️ Échec Gemini: {e}")
        
        # Fallback vers Mistral
        if self.mistral_available:
            self.current_provider = "mistral"
            return self.generate_with_mistral(prompt, system_prompt)
        else:
            return "❌ Aucun LLM disponible. Vérifiez votre configuration Gemini ou installez Mistral avec Ollama."
    
    def reset_gemini_availability(self):
        """Réactive Gemini (utile après une pause)"""
        if self.google_api_key:
            self.gemini_available = True
            print("🔄 Gemini réactivé")
    
    def get_status(self) -> Dict[str, Any]:
        """Retourne le statut du système"""
        return {
            "gemini_available": self.gemini_available,
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
hybrid_llm_gemini = HybridLLMManagerGemini()

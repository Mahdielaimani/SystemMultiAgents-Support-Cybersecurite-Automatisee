# utils/hybrid_llm_manager_gemini.py
import os
import json
import time
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

class HybridLLMManagerGemini:
    """Gestionnaire LLM hybride : Google Gemini -> Groq/Llama 3"""
    
    def __init__(self):
        self.google_api_key = os.getenv("GOOGLE_API_KEY")
        self.gemini_model = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
        
        # Configuration Groq
        self.groq_api_key = os.getenv("GROQ_API_KEY", "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")
        self.groq_model = os.getenv("GROQ_MODEL", "llama3-8b-8192")
        
        # Configuration des limites (Gemini a des quotas généreux)
        self.token_limit_per_hour = 15000   # Limite tokens/heure
        self.token_limit_per_day = 100000   # Limite tokens/jour
        
        # Tracking des tokens
        self.token_usage_file = "config/token_usage_gemini.json"
        self.load_token_usage()
        
        # État du système
        self.gemini_available = bool(self.google_api_key)
        self.groq_available = self._check_groq()
        self.current_provider = "gemini" if self.gemini_available else "groq"
        
        print(f"🤖 LLM Manager Gemini initialisé")
        print(f"   🔑 Gemini: {'✅ Disponible' if self.gemini_available else '❌ Pas de clé'}")
        print(f"   🦙 Groq/Llama 3: {'✅ Disponible' if self.groq_available else '❌ Non disponible'}")
        print(f"   🎯 Provider actuel: {self.current_provider}")
    
    def _check_groq(self) -> bool:
        """Vérifie la disponibilité de Groq"""
        try:
            from groq import Groq
            # Tester la connexion
            client = Groq(api_key=self.groq_api_key)
            return True
        except Exception as e:
            print(f"⚠️ Groq non disponible: {e}")
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
                temperature=0.7,
                max_output_tokens=1024,
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
                print("🔄 Quota Gemini épuisé, basculement vers Groq/Llama 3")
                self.gemini_available = False
                return self.generate_with_groq(prompt, system_prompt)
            elif any(keyword in error_str for keyword in ["401", "invalid", "unauthorized", "api_key"]):
                print("🔄 Clé Gemini invalide, basculement vers Groq/Llama 3")
                self.gemini_available = False
                return self.generate_with_groq(prompt, system_prompt)
            else:
                print("🔄 Erreur Gemini, tentative avec Groq/Llama 3")
                return self.generate_with_groq(prompt, system_prompt)
    
    def generate_with_groq(self, prompt: str, system_prompt: str = None) -> str:
        """Génère avec Groq/Llama 3"""
        try:
            from groq import Groq
            
            # Initialiser le client Groq
            client = Groq(api_key=self.groq_api_key)
            
            # Construire les messages
            messages = []
            
            if system_prompt:
                messages.append({
                    "role": "system",
                    "content": system_prompt
                })
            
            messages.append({
                "role": "user",
                "content": prompt
            })
            
            print("🦙 Génération avec Groq/Llama 3...")
            
            # Appel à l'API Groq
            completion = client.chat.completions.create(
                model=self.groq_model,
                messages=messages,
                temperature=0.7,
                max_tokens=1024,
                top_p=0.9,
                stream=False
            )
            
            response_text = completion.choices[0].message.content
            print(f"✅ Réponse Groq/Llama 3 générée ({len(response_text)} chars)")
            return response_text
                
        except Exception as e:
            print(f"❌ Erreur Groq: {e}")
            
            # Vérifier le type d'erreur
            error_str = str(e).lower()
            if "rate limit" in error_str:
                return "Limite de taux Groq atteinte. Veuillez réessayer dans quelques instants."
            elif "api key" in error_str or "unauthorized" in error_str:
                return "Erreur d'authentification Groq. Vérifiez votre clé API."
            else:
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
        
        # Fallback vers Groq/Llama 3
        if self.groq_available:
            self.current_provider = "groq"
            return self.generate_with_groq(prompt, system_prompt)
        else:
            return "❌ Aucun LLM disponible. Vérifiez votre configuration Gemini ou votre clé API Groq."
    
    def reset_gemini_availability(self):
        """Réactive Gemini (utile après une pause)"""
        if self.google_api_key:
            self.gemini_available = True
            print("🔄 Gemini réactivé")
    
    def get_status(self) -> Dict[str, Any]:
        """Retourne le statut du système"""
        return {
            "gemini_available": self.gemini_available,
            "groq_available": self.groq_available,
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
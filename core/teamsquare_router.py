"""
Routeur d'intentions spécifique à TeamSquare.
"""
import logging
from typing import Dict, Any, List, Optional, Tuple
import re
import os

from transformers import pipeline
from config.settings import RouterConfig
from config.teamsquare_config import TEAMSQUARE_KEYWORDS

logger = logging.getLogger(__name__)

class TeamSquareRouter:
    """
    Routeur qui analyse les requêtes utilisateur pour déterminer l'intention
    et les diriger vers l'agent approprié, spécifiquement adapté à TeamSquare.
    """
    
    def __init__(self, config: RouterConfig):
        """
        Initialise le routeur d'intentions.
        
        Args:
            config: Configuration du routeur
        """
        self.config = config
        self.intent_classifier = None
        self.url_pattern = re.compile(
            r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+(?:/[-\w%!$&\'()*+,;=:@/~]+)*(?:\?[-\w%!$&\'()*+,;=:@/~]*)?'
        )
        
        # Mots-clés spécifiques à TeamSquare
        self.teamsquare_keywords = TEAMSQUARE_KEYWORDS
        
        # Mots-clés de sécurité
        self.security_keywords = [
            "vulnerability", "security", "hack", "exploit", "attack", "breach", 
            "malware", "virus", "phishing", "threat", "risk", "patch", "CVE",
            "vulnérabilité", "sécurité", "piratage", "attaque", "menace", "risque",
            "scan", "pentest", "penetration test", "security scan", "vulnerability scan",
            "security assessment", "security audit", "test de pénétration", "audit de sécurité"
        ]
        
        # Charger le modèle de classification si configuré
        if self.config.use_model and self.config.model_path:
            self._load_model()
    
    def _load_model(self):
        """Charge le modèle de classification d'intentions."""
        try:
            if os.path.exists(self.config.model_path):
                self.intent_classifier = pipeline(
                    "text-classification", 
                    model=self.config.model_path,
                    device=self.config.device
                )
                logger.info(f"Intent classifier loaded from {self.config.model_path}")
            else:
                logger.warning(f"Model path {self.config.model_path} does not exist. Using rule-based classification.")
        except Exception as e:
            logger.error(f"Error loading intent classifier: {str(e)}")
            logger.info("Falling back to rule-based classification")
    
    def route(self, query: str) -> Tuple[str, float]:
        """
        Détermine l'agent approprié pour traiter la requête.
        
        Args:
            query: Texte de la requête utilisateur
            
        Returns:
            Tuple contenant le nom de l'agent et le score de confiance
        """
        # Vérifier d'abord les règles explicites
        agent, confidence = self._rule_based_routing(query)
        if agent:
            return agent, confidence
        
        # Utiliser le modèle de classification si disponible
        if self.intent_classifier:
            try:
                result = self.intent_classifier(query)
                predicted_label = result[0]['label']
                confidence = result[0]['score']
                
                logger.debug(f"Model classified intent: {predicted_label} with confidence {confidence}")
                
                # N'utiliser la prédiction que si la confiance est suffisante
                if confidence >= self.config.confidence_threshold:
                    # Mapper l'intention à l'agent approprié
                    if predicted_label in ["cybersecurity", "security_question", "pentest_request"]:
                        return "security", confidence
                    elif predicted_label in ["customer_support", "technical_issue"]:
                        return "support", confidence
                    elif predicted_label in ["teamsquare_services", "service_inquiry"]:
                        return "support", confidence
                    elif predicted_label in ["teamsquare_products", "product_inquiry"]:
                        return "support", confidence
                    elif predicted_label in ["contact_info", "company_info"]:
                        return "support", confidence
                    else:
                        return "support", confidence
            except Exception as e:
                logger.error(f"Error in model-based intent classification: {str(e)}")
        
        # Par défaut, diriger vers l'agent de support
        return "support", 0.7
    
    def _rule_based_routing(self, query: str) -> Tuple[Optional[str], float]:
        """
        Routage basé sur des règles spécifiques à TeamSquare.
        
        Args:
            query: Texte de la requête utilisateur
            
        Returns:
            Tuple contenant le nom de l'agent (ou None) et le score de confiance
        """
        query_lower = query.lower()
        
        # Vérifier les questions de sécurité
        if any(keyword in query_lower for keyword in self.security_keywords):
            return "security", 0.9
        
        # Vérifier les URLs (potentiellement pour pentest)
        if self.url_pattern.search(query) and any(keyword in query_lower for keyword in self.security_keywords):
            return "security", 0.95
        
        # Vérifier les mots-clés spécifiques à TeamSquare
        for category, keywords in self.teamsquare_keywords.items():
            if any(keyword in query_lower for keyword in keywords):
                # Mapper la catégorie à l'agent approprié
                if category in ["transformation", "project_management", "organization"]:
                    return "support", 0.85
                elif category in ["digital"] and "sécurité" in query_lower:
                    return "security", 0.85
        
        # Aucune règle explicite ne correspond
        return None, 0.0
    
    def analyze_intent(self, query: str) -> Dict[str, Any]:
        """
        Analyse détaillée de l'intention de la requête.
        
        Args:
            query: Texte de la requête utilisateur
            
        Returns:
            Dictionnaire contenant l'analyse de l'intention
        """
        query_lower = query.lower()
        
        # Initialiser le résultat
        result = {
            "agent": "support",  # Agent par défaut
            "confidence": 0.0,
            "detected_keywords": [],
            "teamsquare_categories": [],
            "is_security_related": False,
            "urls": [],
            "entities": []
        }
        
        # Détecter les mots-clés de sécurité
        security_keywords_found = []
        for keyword in self.security_keywords:
            if keyword in query_lower:
                security_keywords_found.append(keyword)
                result["is_security_related"] = True
        
        if security_keywords_found:
            result["detected_keywords"].extend(security_keywords_found)
        
        # Détecter les mots-clés spécifiques à TeamSquare
        for category, keywords in self.teamsquare_keywords.items():
            category_keywords = []
            for keyword in keywords:
                if keyword in query_lower:
                    category_keywords.append(keyword)
            
            if category_keywords:
                result["teamsquare_categories"].append(category)
                result["detected_keywords"].extend(category_keywords)
        
        # Extraire les URLs
        urls = self.url_pattern.findall(query)
        if urls:
            result["urls"] = urls
        
        # Déterminer l'agent et la confiance
        agent, confidence = self.route(query)
        result["agent"] = agent
        result["confidence"] = confidence
        
        return result

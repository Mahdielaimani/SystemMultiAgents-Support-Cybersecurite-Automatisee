"""
Classificateur de sensibilité des questions.
"""
import re
import logging
from typing import Dict, Any, List
from enum import Enum

logger = logging.getLogger(__name__)

class SensitivityLevel(Enum):
    """Niveaux de sensibilité."""
    SAFE = "safe"           # Question sûre, peut chercher sur le web
    SENSITIVE = "sensitive"  # Question sensible, ne pas chercher
    UNKNOWN = "unknown"     # Incertain, traiter avec prudence

class SensitivityClassifier:
    """Classificateur pour déterminer la sensibilité des questions."""
    
    def __init__(self):
        # Mots-clés sensibles (données personnelles, sécurité, etc.)
        self.sensitive_keywords = {
            # Données personnelles
            "password", "mot de passe", "mdp", "login", "identifiant",
            "email", "adresse", "téléphone", "numéro", "carte bancaire",
            "compte", "solde", "transaction", "paiement", "facture",
            
            # Sécurité
            "hack", "pirate", "vulnérabilité", "faille", "exploit",
            "attaque", "malware", "virus", "trojan", "backdoor",
            
            # Informations confidentielles
            "confidentiel", "secret", "privé", "interne", "classifié",
            "salaire", "budget", "contrat", "accord", "négociation",
            
            # Données médicales
            "maladie", "diagnostic", "traitement", "médicament", "santé",
            "médical", "hôpital", "docteur", "patient",
            
            # Données légales
            "procès", "tribunal", "avocat", "juridique", "plainte",
            "délit", "crime", "police", "justice"
        }
        
        # Patterns sensibles
        self.sensitive_patterns = [
            r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b',  # Numéro de carte
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # Email
            r'\b\d{2}[-\s]?\d{2}[-\s]?\d{2}[-\s]?\d{2}[-\s]?\d{2}\b',  # Téléphone FR
            r'\b(?:mot de passe|password)[\s:=]+\S+\b',  # Mot de passe
        ]
        
        # Questions sûres communes
        self.safe_patterns = [
            r'\bcomment\s+(?:faire|utiliser|installer|configurer)\b',
            r'\bqu[\'e]?est[-\s]ce que\b',
            r'\bpourquoi\b',
            r'\bdéfinition\s+de\b',
            r'\bexemple\s+de\b',
            r'\btutoriel\b',
            r'\bguide\b',
            r'\bdocumentation\b'
        ]
    
    def classify_sensitivity(self, question: str) -> Dict[str, Any]:
        """
        Classifie la sensibilité d'une question.
        
        Args:
            question: Question à analyser
            
        Returns:
            Résultat de classification avec niveau et raison
        """
        try:
            question_lower = question.lower()
            
            # Vérifier les patterns sensibles
            for pattern in self.sensitive_patterns:
                if re.search(pattern, question, re.IGNORECASE):
                    return {
                        "level": SensitivityLevel.SENSITIVE,
                        "confidence": 0.95,
                        "reason": "Pattern sensible détecté",
                        "can_search_web": False
                    }
            
            # Vérifier les mots-clés sensibles
            sensitive_count = 0
            found_keywords = []
            
            for keyword in self.sensitive_keywords:
                if keyword in question_lower:
                    sensitive_count += 1
                    found_keywords.append(keyword)
            
            # Si plusieurs mots-clés sensibles
            if sensitive_count >= 2:
                return {
                    "level": SensitivityLevel.SENSITIVE,
                    "confidence": 0.9,
                    "reason": f"Mots-clés sensibles: {', '.join(found_keywords)}",
                    "can_search_web": False
                }
            
            # Si un seul mot-clé sensible
            elif sensitive_count == 1:
                return {
                    "level": SensitivityLevel.SENSITIVE,
                    "confidence": 0.7,
                    "reason": f"Mot-clé sensible: {found_keywords[0]}",
                    "can_search_web": False
                }
            
            # Vérifier les patterns sûrs
            for pattern in self.safe_patterns:
                if re.search(pattern, question_lower):
                    return {
                        "level": SensitivityLevel.SAFE,
                        "confidence": 0.8,
                        "reason": "Question de type informatif/éducatif",
                        "can_search_web": True
                    }
            
            # Par défaut, considérer comme sûr si pas de signaux sensibles
            return {
                "level": SensitivityLevel.SAFE,
                "confidence": 0.6,
                "reason": "Aucun indicateur de sensibilité détecté",
                "can_search_web": True
            }
        
        except Exception as e:
            logger.error(f"Erreur lors de la classification: {e}")
            return {
                "level": SensitivityLevel.UNKNOWN,
                "confidence": 0.0,
                "reason": f"Erreur de classification: {str(e)}",
                "can_search_web": False
            }
    
    def is_safe_for_web_search(self, question: str) -> bool:
        """
        Détermine si une question peut être recherchée sur le web.
        
        Args:
            question: Question à analyser
            
        Returns:
            True si sûr pour recherche web, False sinon
        """
        result = self.classify_sensitivity(question)
        return result.get("can_search_web", False)

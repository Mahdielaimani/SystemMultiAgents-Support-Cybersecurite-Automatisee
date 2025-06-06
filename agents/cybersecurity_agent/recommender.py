"""
Générateur de recommandations de sécurité pour l'agent de cybersécurité.
"""
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

class SecurityRecommender:
    """
    Générateur de recommandations de sécurité basées sur les vulnérabilités détectées.
    """
    
    def __init__(self):
        """Initialise le générateur de recommandations."""
        # Charger les recommandations prédéfinies
        self.recommendations = self._load_recommendations()
    
    def _load_recommendations(self) -> Dict[str, Dict[str, Any]]:
        """
        Charge les recommandations prédéfinies.
        
        Returns:
            Dictionnaire des recommandations par type de vulnérabilité
        """
        return {
            "sql_injection": {
                "title": "Prévention des injections SQL",
                "recommendations": [
                    "Utilisez des requêtes paramétrées ou des ORM",
                    "Validez toutes les entrées utilisateur",
                    "Appliquez le principe du moindre privilège pour les comptes de base de données",
                    "Utilisez des WAF pour une protection supplémentaire"
                ],
                "resources": [
                    "https://owasp.org/www-community/attacks/SQL_Injection",
                    "https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html"
                ]
            },
            "xss": {
                "title": "Prévention des attaques XSS",
                "recommendations": [
                    "Échappez toutes les sorties HTML",
                    "Utilisez des en-têtes Content-Security-Policy",
                    "Validez et assainissez toutes les entrées utilisateur",
                    "Utilisez des frameworks modernes qui échappent automatiquement le contenu"
                ],
                "resources": [
                    "https://owasp.org/www-community/attacks/xss/",
                    "https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html"
                ]
            },
            "csrf": {
                "title": "Prévention des attaques CSRF",
                "recommendations": [
                    "Utilisez des jetons anti-CSRF",
                    "Vérifiez l'en-tête Referer",
                    "Utilisez l'en-tête SameSite pour les cookies",
                    "Implémentez des vérifications d'origine"
                ],
                "resources": [
                    "https://owasp.org/www-community/attacks/csrf",
                    "https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html"
                ]
            },
            "authentication_bypass": {
                "title": "Prévention des contournements d'authentification",
                "recommendations": [
                    "Implémentez une authentification multi-facteurs",
                    "Utilisez des mécanismes d'authentification éprouvés",
                    "Évitez les identifiants prédictibles",
                    "Mettez en place des limites de tentatives de connexion"
                ],
                "resources": [
                    "https://owasp.org/www-project-top-ten/2017/A2_2017-Broken_Authentication",
                    "https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html"
                ]
            },
            "information_disclosure": {
                "title": "Prévention des fuites d'informations",
                "recommendations": [
                    "Minimisez les informations exposées dans les en-têtes HTTP",
                    "Désactivez les messages d'erreur détaillés en production",
                    "Utilisez des en-têtes de sécurité appropriés",
                    "Mettez en place une politique de gestion des informations sensibles"
                ],
                "resources": [
                    "https://owasp.org/www-project-top-ten/2017/A3_2017-Sensitive_Data_Exposure",
                    "https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html"
                ]
            },
            "insecure_configuration": {
                "title": "Correction des configurations non sécurisées",
                "recommendations": [
                    "Suivez le principe du moindre privilège",
                    "Désactivez les fonctionnalités et services non nécessaires",
                    "Mettez à jour régulièrement les composants",
                    "Utilisez des outils d'analyse de configuration"
                ],
                "resources": [
                    "https://owasp.org/www-project-top-ten/2017/A6_2017-Security_Misconfiguration",
                    "https://cheatsheetseries.owasp.org/cheatsheets/Configuration_Management_Cheat_Sheet.html"
                ]
            }
        }
    
    def get_recommendations(self, vulnerability_type: str) -> Dict[str, Any]:
        """
        Récupère les recommandations pour un type de vulnérabilité.
        
        Args:
            vulnerability_type: Type de vulnérabilité
            
        Returns:
            Recommandations pour ce type de vulnérabilité
        """
        # Récupérer les recommandations spécifiques ou des recommandations génériques
        return self.recommendations.get(vulnerability_type, {
            "title": "Recommandations générales de sécurité",
            "recommendations": [
                "Maintenez tous les logiciels à jour",
                "Utilisez des mots de passe forts et uniques",
                "Mettez en place une authentification multi-facteurs",
                "Effectuez des audits de sécurité réguliers",
                "Suivez le principe du moindre privilège"
            ],
            "resources": [
                "https://owasp.org/www-project-top-ten/",
                "https://cheatsheetseries.owasp.org/"
            ]
        })
    
    def format_recommendations(self, vulnerability_type: str) -> str:
        """
        Formate les recommandations pour un type de vulnérabilité.
        
        Args:
            vulnerability_type: Type de vulnérabilité
            
        Returns:
            Texte formaté des recommandations
        """
        recs = self.get_recommendations(vulnerability_type)
        
        formatted_text = f"## {recs['title']}\n\n"
        formatted_text += "### Recommandations:\n"
        
        for i, rec in enumerate(recs['recommendations'], 1):
            formatted_text += f"{i}. {rec}\n"
        
        formatted_text += "\n### Ressources:\n"
        for res in recs['resources']:
            formatted_text += f"- {res}\n"
        
        return formatted_text

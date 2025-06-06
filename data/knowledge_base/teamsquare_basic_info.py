"""
Connaissances de base sur TeamSquare pour l'assistant
"""

TEAMSQUARE_BASIC_INFO = {
    "company": {
        "name": "TeamSquare",
        "description": "TeamSquare est une plateforme innovante de collaboration d'équipe qui révolutionne la façon dont les équipes travaillent ensemble.",
        "mission": "Faciliter la collaboration et améliorer la productivité des équipes",
        "vision": "Devenir la référence mondiale en matière d'outils de collaboration d'équipe"
    },
    
    "features": {
        "collaboration": [
            "Chat en temps réel",
            "Partage de fichiers sécurisé",
            "Espaces de travail collaboratifs",
            "Tableaux de bord partagés"
        ],
        "project_management": [
            "Gestion de projets agile",
            "Suivi des tâches et deadlines",
            "Planification d'équipe",
            "Rapports de progression"
        ],
        "communication": [
            "Visioconférences intégrées",
            "Messagerie instantanée",
            "Notifications intelligentes",
            "Intégration email"
        ],
        "security": [
            "Chiffrement end-to-end",
            "Authentification à deux facteurs",
            "Contrôle d'accès granulaire",
            "Sauvegarde automatique"
        ]
    },
    
    "pricing": {
        "plans": [
            {
                "name": "Starter",
                "price": "9€/mois par utilisateur",
                "description": "Parfait pour les petites équipes",
                "features": ["Jusqu'à 10 utilisateurs", "5GB de stockage", "Support email"]
            },
            {
                "name": "Professional", 
                "price": "19€/mois par utilisateur",
                "description": "Idéal pour les équipes en croissance",
                "features": ["Utilisateurs illimités", "100GB de stockage", "Support prioritaire", "Intégrations avancées"]
            },
            {
                "name": "Enterprise",
                "price": "Sur devis",
                "description": "Pour les grandes organisations",
                "features": ["Tout du plan Pro", "Stockage illimité", "Support dédié", "Sécurité renforcée"]
            }
        ],
        "contact": "Contactez notre équipe commerciale pour obtenir un devis personnalisé"
    },
    
    "integrations": [
        "Slack", "Microsoft Teams", "Google Workspace", "Zoom", 
        "Trello", "Asana", "GitHub", "Salesforce"
    ],
    
    "support": {
        "channels": ["Email", "Chat en direct", "Base de connaissances", "Webinaires"],
        "hours": "Support disponible 24/7 pour les plans Professional et Enterprise"
    }
}

def get_teamsquare_info(category: str = None) -> str:
    """Récupère les informations sur TeamSquare"""
    if not category:
        return f"""TeamSquare est {TEAMSQUARE_BASIC_INFO['company']['description']}

🎯 **Notre mission :** {TEAMSQUARE_BASIC_INFO['company']['mission']}

✨ **Principales fonctionnalités :**
- Collaboration en temps réel
- Gestion de projets agile  
- Communication intégrée
- Sécurité de niveau entreprise

💰 **Plans disponibles :** Starter (9€/mois), Professional (19€/mois), Enterprise (sur devis)
📞 **Support :** {TEAMSQUARE_BASIC_INFO['support']['hours']}"""
    
    return TEAMSQUARE_BASIC_INFO.get(category, "Information non disponible")

def get_pricing_info() -> str:
    """Récupère les informations de tarification"""
    plans = TEAMSQUARE_BASIC_INFO['pricing']['plans']
    pricing_text = "💰 **Nos tarifs TeamSquare :**\n\n"
    
    for plan in plans:
        pricing_text += f"**{plan['name']}** - {plan['price']}\n"
        pricing_text += f"{plan['description']}\n"
        pricing_text += "• " + "\n• ".join(plan['features']) + "\n\n"
    
    pricing_text += f"📞 {TEAMSQUARE_BASIC_INFO['pricing']['contact']}"
    return pricing_text

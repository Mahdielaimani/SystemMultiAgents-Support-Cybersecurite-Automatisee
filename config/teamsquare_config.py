"""
Configuration spécifique à TeamSquare pour le système multi-agents.
"""
from typing import Dict, Any, List

# Informations sur l'entreprise
COMPANY_INFO = {
    "name": "TeamSquare",
    "slogan": "Unleash your projects potential",
    "description": "Cabinet de conseil spécialisé en management de projet, du changement et de la transformation.",
    "satisfaction_score": "98/100",
    "founded": "2015",  # À confirmer
    "website": "https://www.teamsquare.fr",
    "locations": [
        {
            "city": "Lyon",
            "address": "129 Rue Servient, Tour Part-Dieu",
            "postal_code": "69003",
            "phone": "+33 4 72 35 13 25"
        },
        {
            "city": "Paris",
            "address": "63 Rue de Rivoli",
            "postal_code": "75001",
            "phone": "+33 1 45 07 87 61"
        },
        {
            "city": "Genève",
            "address": "24 Rue du Cendrier",
            "postal_code": "1201",
            "country": "Suisse",
            "phone": "+33 4 72 35 13 25"  # Même numéro que Lyon
        }
    ],
    "social_media": {
        "linkedin": "https://www.linkedin.com/company/teamsquare/",
        "youtube": "https://www.youtube.com/channel/UCxxxxxxxx",  # À compléter
        "instagram": "https://www.instagram.com/teamsquare/"
    },
    "certifications": ["Microsoft Gold Partner", "Qualiopi", "EcoVadis"]
}

# Services offerts par TeamSquare
SERVICES = [
    {
        "name": "Management de la Transformation",
        "description": "Accompagnement des organisations dans leurs projets de transformation digitale et organisationnelle.",
        "sub_services": [
            "Transformer la transformation",
            "Accompagnement au changement",
            "Gestion de projet",
            "Coaching d'équipe"
        ]
    },
    {
        "name": "Conseil en Organisation",
        "description": "Optimisation des processus et structures organisationnelles.",
        "sub_services": [
            "Audit organisationnel",
            "Optimisation des processus",
            "Réorganisation d'entreprise"
        ]
    },
    {
        "name": "Solutions Digitales",
        "description": "Développement et implémentation de solutions numériques sur mesure.",
        "sub_services": [
            "Développement d'applications",
            "Intégration de systèmes",
            "Solutions cloud"
        ]
    },
    {
        "name": "Formation",
        "description": "Programmes de formation adaptés aux besoins des entreprises.",
        "sub_services": [
            "Gestion de projet",
            "Agilité",
            "Leadership",
            "Transformation digitale"
        ]
    }
]

# Valeurs et vision de TeamSquare
VISION = {
    "mission": "Accompagner les organisations dans leurs projets de transformation pour libérer leur potentiel.",
    "values": [
        "Excellence",
        "Innovation",
        "Collaboration",
        "Engagement",
        "Adaptabilité"
    ],
    "approach": "Approche sur mesure et collaborative, centrée sur les besoins spécifiques de chaque client."
}

# Partenaires stratégiques
PARTNERS = [
    {
        "name": "Microsoft",
        "type": "Gold Partner",
        "description": "Partenariat stratégique pour les solutions Microsoft."
    },
    {
        "name": "Qualiopi",
        "type": "Certification",
        "description": "Certification qualité pour les actions de formation."
    },
    {
        "name": "EcoVadis",
        "type": "Certification",
        "description": "Évaluation de la performance RSE."
    }
]

# Secteurs d'activité des clients
CLIENT_SECTORS = [
    "Banque & Assurance",
    "Industrie",
    "Services",
    "Santé",
    "Secteur Public",
    "Énergie",
    "Transport & Logistique",
    "Retail"
]

# Exemples de cas d'usage pour l'agent
CASE_STUDIES = [
    {
        "title": "Transformation digitale d'une banque",
        "sector": "Banque & Assurance",
        "challenge": "Modernisation des processus et outils digitaux",
        "solution": "Accompagnement au changement et implémentation de nouvelles solutions",
        "results": "Amélioration de l'efficacité opérationnelle de 30%"
    },
    {
        "title": "Réorganisation d'un service client",
        "sector": "Services",
        "challenge": "Optimisation de la structure organisationnelle",
        "solution": "Audit et refonte des processus",
        "results": "Augmentation de la satisfaction client de 25%"
    },
    {
        "title": "Déploiement d'une solution cloud",
        "sector": "Industrie",
        "challenge": "Migration vers le cloud",
        "solution": "Implémentation d'une architecture cloud sécurisée",
        "results": "Réduction des coûts IT de 40%"
    }
]

# Mots-clés spécifiques à TeamSquare pour la détection d'intentions
TEAMSQUARE_KEYWORDS = {
    "transformation": ["transformation", "changement", "transition", "évolution", "mutation"],
    "project_management": ["gestion de projet", "chef de projet", "PMO", "portfolio", "programme"],
    "digital": ["digital", "numérique", "technologie", "IT", "système d'information"],
    "organization": ["organisation", "processus", "structure", "gouvernance", "méthode"],
    "training": ["formation", "apprentissage", "compétence", "montée en compétence", "certification"],
    "consulting": ["conseil", "consultant", "expertise", "accompagnement", "audit"]
}

def get_company_info() -> Dict[str, Any]:
    """Retourne les informations sur l'entreprise."""
    return COMPANY_INFO

def get_services() -> List[Dict[str, Any]]:
    """Retourne la liste des services offerts."""
    return SERVICES

def get_vision() -> Dict[str, Any]:
    """Retourne la vision et les valeurs de l'entreprise."""
    return VISION

def get_partners() -> List[Dict[str, Any]]:
    """Retourne la liste des partenaires."""
    return PARTNERS

def get_case_studies() -> List[Dict[str, Any]]:
    """Retourne les études de cas."""
    return CASE_STUDIES

def get_keywords() -> Dict[str, List[str]]:
    """Retourne les mots-clés spécifiques à TeamSquare."""
    return TEAMSQUARE_KEYWORDS

"""
Détecteur de scope business pour l'agent de support - VERSION FINALE CORRIGÉE
"""
import logging
from typing import Dict, Tuple, List, Any
import re

logger = logging.getLogger(__name__)

class BusinessScopeDetector:
    """Détecteur de scope business pour déterminer si une question concerne TeamSquare"""
    
    def __init__(self):
        self._setup_keywords()
    
    def _setup_keywords(self):
        """Configure les mots-clés pour la détection de scope"""
        
        # Mots-clés business (TeamSquare) - VERSION AMÉLIORÉE
        self.business_keywords = {
            'platform': ['teamsquare', 'team square', 'plateforme', 'platform'],
            'pricing': ['prix', 'tarif', 'coût', 'coute', 'price', 'cost', 'plan', 'abonnement', 'subscription'],
            'features': ['fonctionnalité', 'feature', 'fonction', 'capacité', 'outil', 'tool'],
            'support': ['support', 'aide', 'help', 'assistance', 'contact'],
            'api': ['api', 'intégration', 'integration', 'webhook', 'endpoint'],
            'security': ['sécurité', 'security', 'données', 'data', 'protection'],
            'collaboration': ['collaboration', 'équipe', 'team', 'projet', 'project', 'partage', 'share'],
            'company': ['entreprise', 'company', 'société', 'business', 'votre', 'your', 'notre', 'our', 'vous', 'we', 'nous'],
            'about': ['qui êtes-vous', 'who are you', 'présentation', 'about', 'à propos', 'description', 'activité', 'activity', 'fait quoi', 'what do you do', 'que faites-vous']
        }
        
        # Mots-clés externes (hors business)
        self.external_keywords = {
            'weather': ['météo', 'weather', 'temps', 'température', 'pluie', 'soleil', 'climat'],
            'news': ['actualité', 'news', 'nouvelles', 'information', 'journal', 'média'],
            'time': ['heure', 'time', 'date', 'aujourd\'hui', 'today', 'maintenant', 'now', 'mois', 'jour', 'année', 'semaine', 'month', 'day', 'year', 'week'],
            'cooking': ['recette', 'cuisine', 'cooking', 'plat', 'dish', 'nourriture', 'food'],
            'travel': ['voyage', 'travel', 'destination', 'vacances', 'holiday', 'hôtel', 'vol', 'flight'],
            'sports': ['sport', 'football', 'tennis', 'match', 'équipe sportive', 'basketball', 'jeux'],
            'entertainment': ['film', 'movie', 'série', 'musique', 'music', 'jeu', 'game', 'concert', 'spectacle'],
            'health': ['santé', 'health', 'médecin', 'doctor', 'maladie', 'symptôme', 'hôpital', 'médicament'],
            'education': ['école', 'school', 'université', 'cours', 'étude', 'study', 'formation'],
            'general': ['comment', 'pourquoi', 'why', 'how', 'qu\'est-ce que', 'what is']
        }
        
        # Phrases qui indiquent clairement une recherche externe
        self.external_phrases = [
            'recherche externe',
            'agent externe',
            'recherche web',
            'chercher sur internet',
            'google',
            'wikipedia'
        ]
        
        # Patterns de questions externes
        self.external_patterns = [
            r'quelle (est|sont) la .*(date|heure|météo|température)',
            r'quel (est|sont) le .*(jour|mois|temps)',
            r'on est (en|dans|à) quel.*(jour|mois|année|heure)',
            r'quelle (heure|date) est-il',
            r'quel temps fait-il',
            r'comment faire (une|un|des)',
            r'qu\'est-ce que .*(pas teamsquare)',
            r'qui (est|sont|a) .*(pas teamsquare)',
            # NOUVEAUX PATTERNS AJOUTÉS
            r'c\'est quoi (?!.*teamsquare)',
            r'qu\'est-ce que (?!.*teamsquare)',
            r'qui est (?!.*teamsquare)',
            r'que fait (?!.*teamsquare)',
            r'comment fonctionne (?!.*teamsquare)',
            r'définition de (?!.*teamsquare)'
        ]
    
    def analyze_query(self, query: str) -> Dict[str, any]:
        """
        Analyse une requête pour déterminer son scope
        
        Args:
            query: La requête à analyser
            
        Returns:
            Dict contenant le scope et la confiance
        """
        query_lower = query.lower().strip()
        
        # Vérifier les patterns externes explicites
        for pattern in self.external_patterns:
            if re.search(pattern, query_lower):
                return {
                    'scope': 'external',
                    'confidence': 0.8,
                    'business_score': 0.1,
                    'external_score': 0.8,
                    'query': query,
                    'matched_pattern': pattern
                }
        
        # Calculer les scores
        business_score = self._calculate_business_score(query_lower)
        external_score = self._calculate_external_score(query_lower)
        
        # Déterminer le scope
        if business_score > external_score and business_score > 0.3:
            scope = 'business'
            confidence = business_score
        elif external_score > business_score and external_score > 0.3:  # Seuil abaissé à 0.3
            scope = 'external'
            confidence = external_score
        else:
            # Vérifier les questions de date/heure/météo spécifiquement
            if self._is_time_date_question(query_lower):
                scope = 'external'
                confidence = 0.7
                external_score = 0.7
            else:
                scope = 'unknown'
                confidence = max(business_score, external_score, 0.3)
        
        return {
            'scope': scope,
            'confidence': confidence,
            'business_score': business_score,
            'external_score': external_score,
            'query': query
        }
    
    def _is_time_date_question(self, query: str) -> bool:
        """Détecte spécifiquement les questions de date/heure - VERSION CORRIGÉE"""
        # Patterns spécifiques pour éviter les faux positifs
        time_date_patterns = [
            r'\bquelle heure\b',
            r'\bquel jour\b',
            r'\bquelle date\b', 
            r'\bquel mois\b',
            r'\bquelle année\b',
            r'\bon est quel jour\b',
            r'\bon est en quelle année\b',
            r'\bon est quel mois\b',
            r'\bon est dans quel mois\b',
            r'\baujourd\'hui\b',
            r'\bmaintenant\b',
            r'\bdate actuelle\b',
            r'\bheure actuelle\b',
            r'\bcombien de temps\b',
            r'\bquand est-ce\b'
        ]
        
        # Utiliser des regex avec des limites de mots pour éviter les faux positifs
        for pattern in time_date_patterns:
            if re.search(pattern, query, re.IGNORECASE):
                return True
        
        return False
    
    def _calculate_business_score(self, query: str) -> float:
        """Calcule le score business de la requête - VERSION AMÉLIORÉE"""
        score = 0.0
        
        for category, keywords in self.business_keywords.items():
            for keyword in keywords:
                if keyword in query:
                    # Bonus élevé pour les questions sur l'entreprise
                    if category in ['company', 'about']:
                        score += 0.4
                    # Bonus pour les mots-clés importants
                    elif category in ['platform', 'pricing']:
                        score += 0.3
                    elif category in ['features', 'api']:
                        score += 0.2
                    else:
                        score += 0.1

        # Bonus spécial pour les questions directes sur l'entreprise
        company_patterns = [
            r'votre entreprise',
            r'your company',
            r'que fait.*(votre|vous)',
            r'what do you do',
            r'qui êtes-vous',
            r'who are you',
            r'à propos de vous',
            r'about you'
        ]
        
        for pattern in company_patterns:
            if re.search(pattern, query, re.IGNORECASE):
                score += 0.6  # Score très élevé
        
        return min(score, 1.0)
    
    def _calculate_external_score(self, query: str) -> float:
        """Calcule le score externe de la requête - VERSION CORRIGÉE"""
        score = 0.0
        
        # Vérifier les phrases explicites
        for phrase in self.external_phrases:
            if phrase in query:
                return 0.9
        
        # Vérifier les mots-clés externes avec des limites de mots
        for category, keywords in self.external_keywords.items():
            for keyword in keywords:
                # Utiliser des regex pour éviter les faux positifs
                pattern = r'\b' + re.escape(keyword) + r'\b'
                if re.search(pattern, query, re.IGNORECASE):
                    # Score élevé pour les catégories clairement externes
                    if category in ['weather', 'news', 'time']:
                        score += 0.4
                    elif category in ['cooking', 'travel', 'sports']:
                        score += 0.3
                    else:
                        score += 0.2
        
        # Bonus pour les questions générales sans contexte business
        if any(word in query for word in ['comment', 'pourquoi', 'qu\'est-ce']):
            if not any(biz_word in query for category in self.business_keywords.values() for biz_word in category):
                score += 0.2
        
        # Bonus pour les questions de définition/explication d'entités externes
        definition_patterns = [
            r'c\'est quoi',
            r'qu\'est-ce que',
            r'qui est',
            r'que fait',
            r'définition de',
            r'expliquer'
        ]

        for pattern in definition_patterns:
            if re.search(pattern, query, re.IGNORECASE):
                # Vérifier que ce n'est pas lié à TeamSquare
                if not any(biz_word in query for category in self.business_keywords.values() for biz_word in category):
                    score += 0.5  # Score élevé pour les questions de définition externes
        
        # Bonus pour les questions de date/heure (utilise la fonction corrigée)
        if self._is_time_date_question(query):
            score += 0.4
        
        return min(score, 1.0)
    
    def should_offer_external_search(self, query: str) -> Tuple[bool, str]:
        """
        Détermine si on doit proposer une recherche externe
        
        Args:
            query: La requête à analyser
            
        Returns:
            Tuple (should_offer, reason)
        """
        analysis = self.analyze_query(query)
        query_lower = query.lower().strip()
        
        # Cas explicites de recherche externe
        if analysis['scope'] == 'external' and analysis['confidence'] > 0.3:  # Seuil abaissé à 0.3
            # Détection spécifique pour différentes catégories
            if self._is_time_date_question(query_lower):
                return True, "Cette question porte sur la date ou l'heure, qui n'est pas liée à TeamSquare."
            elif any(keyword in query_lower for keyword in ['météo', 'weather', 'temps', 'température']):
                return True, "Cette question semble porter sur la météo qui n'est pas liée à TeamSquare."
            elif any(keyword in query_lower for keyword in ['actualité', 'news', 'nouvelles']):
                return True, "Cette question porte sur les actualités qui ne sont pas liées à TeamSquare."
            elif any(keyword in query_lower for keyword in ['recette', 'cuisine', 'cooking']):
                return True, "Cette question porte sur la cuisine qui n'est pas liée à TeamSquare."
            elif any(keyword in query_lower for keyword in ['voyage', 'travel', 'destination']):
                return True, "Cette question porte sur les voyages qui ne sont pas liés à TeamSquare."
            else:
                return True, "Cette question ne semble pas être liée à TeamSquare."
        
        # Cas spéciaux : questions de définition sur des entités non-TeamSquare
        definition_keywords = ['c\'est quoi', 'qu\'est-ce que', 'qui est', 'que fait', 'définition de']
        if any(keyword in query_lower for keyword in definition_keywords):
            # Vérifier que ce n'est pas lié à TeamSquare
            if not any(biz_word in query_lower for category in self.business_keywords.values() for biz_word in category):
                return True, "Cette question porte sur une entité qui n'est pas liée à TeamSquare."
        
        # Cas spéciaux : demandes explicites de recherche externe
        if any(phrase in query_lower for phrase in self.external_phrases):
            return True, "Vous avez demandé une recherche externe."
        
        # Questions très générales sans contexte business
        if (analysis['scope'] == 'unknown' and 
            analysis['business_score'] < 0.2 and 
            len(query.strip()) > 10):
            
            # Vérifier si c'est une vraie question générale
            if any(word in query_lower for word in ['comment', 'pourquoi', 'qu\'est-ce', 'how', 'why', 'what']):
                return True, "Cette question semble être générale et ne pas concerner TeamSquare."
        
        return False, ""
    
    def get_scope_explanation(self, analysis: Dict[str, Any]) -> str:
        """Génère une explication du scope détecté"""
        scope = analysis['scope']
        confidence = analysis['confidence']
        
        if scope == 'business':
            return f"Question business TeamSquare (confiance: {confidence:.2f})"
        elif scope == 'external':
            return f"Question externe hors TeamSquare (confiance: {confidence:.2f})"
        else:
            return f"Scope incertain (confiance: {confidence:.2f})"

def main():
    """Test du détecteur de scope"""
    print("🧪 TEST DÉTECTEUR DE SCOPE BUSINESS - VERSION FINALE CORRIGÉE")
    print("-" * 50)
    
    detector = BusinessScopeDetector()
    
    test_queries = [
        # Questions business
        "Quels sont les prix de TeamSquare ?",
        "Comment fonctionne l'API TeamSquare ?",
        "TeamSquare a-t-il des fonctionnalités de sécurité ?",
        
        # Questions externes claires
        "Quelle est la météo aujourd'hui ?",
        "Quelles sont les dernières actualités ?",
        "Quelle est la date d'aujourd'hui ?",
        "On est dans quel mois ?",
        "Quel jour sommes-nous ?",
        "Comment faire une pasta carbonara ?",
        
        # Questions ambiguës (ne doivent PAS déclencher de recherche externe)
        "Bonjour !",
        "Comment ça va ?",
        "Tu peux m'aider ?",
        
        # Demandes explicites de recherche externe
        "Tu peux appeler l'agent qui fait la recherche externe ?",
        "Recherche externe pour la météo"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n🔍 Test {i}: '{query}'")
        
        analysis = detector.analyze_query(query)
        should_offer, reason = detector.should_offer_external_search(query)
        
        print(f"   Scope: {analysis['scope']} (confiance: {analysis['confidence']:.2f})")
        print(f"   Business: {analysis['business_score']:.2f}, External: {analysis['external_score']:.2f}")
        print(f"   Recherche externe: {'OUI' if should_offer else 'NON'}")
        if reason:
            print(f"   Raison: {reason}")

if __name__ == "__main__":
    main()

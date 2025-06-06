"""
Module pour la collecte et le traitement du feedback utilisateur.

Ce module permet de collecter, stocker et analyser le feedback des utilisateurs
pour améliorer les performances du système.
"""
import logging
from typing import Dict, List, Any, Optional, Union
import os
import json
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)

class FeedbackManager:
    """Gestionnaire de feedback utilisateur."""
    
    def __init__(self, 
                 storage_path: str = "data/feedback",
                 analysis_frequency: str = "daily",
                 notification_enabled: bool = True):
        """
        Initialise le gestionnaire de feedback.
        
        Args:
            storage_path: Chemin pour stocker les données de feedback
            analysis_frequency: Fréquence d'analyse du feedback ('daily', 'weekly', 'monthly')
            notification_enabled: Activer les notifications d'analyse
        """
        self.storage_path = storage_path
        self.analysis_frequency = analysis_frequency
        self.notification_enabled = notification_enabled
        
        # Créer le dossier de stockage s'il n'existe pas
        os.makedirs(storage_path, exist_ok=True)
        
        # Créer les sous-dossiers par catégorie
        for category in ["general", "security", "support", "pentest"]:
            os.makedirs(os.path.join(storage_path, category), exist_ok=True)
    
    def collect_feedback(self, 
                        feedback_type: str,
                        content: Dict[str, Any],
                        category: str = "general",
                        user_id: Optional[str] = None,
                        session_id: Optional[str] = None) -> str:
        """
        Collecte le feedback d'un utilisateur.
        
        Args:
            feedback_type: Type de feedback ('rating', 'comment', 'correction', 'report')
            content: Contenu du feedback
            category: Catégorie du feedback ('general', 'security', 'support', 'pentest')
            user_id: Identifiant de l'utilisateur
            session_id: Identifiant de la session
            
        Returns:
            str: Identifiant du feedback
        """
        # Générer un identifiant unique pour le feedback
        feedback_id = str(uuid.uuid4())
        
        # Préparer les données de feedback
        feedback_data = {
            "id": feedback_id,
            "timestamp": datetime.now().isoformat(),
            "type": feedback_type,
            "category": category,
            "content": content,
            "user_id": user_id,
            "session_id": session_id,
            "status": "new",
            "processed": False
        }
        
        # Déterminer le chemin de stockage
        category_path = os.path.join(self.storage_path, category)
        filepath = os.path.join(category_path, f"{feedback_id}.json")
        
        # Sauvegarder le feedback
        with open(filepath, 'w') as f:
            json.dump(feedback_data, f, indent=2)
        
        logger.info(f"Feedback collecté: {feedback_id} (type: {feedback_type}, catégorie: {category})")
        
        # Déclencher une analyse si nécessaire
        self._check_for_analysis_trigger(feedback_type, category)
        
        return feedback_id
    
    def get_feedback(self, feedback_id: str) -> Optional[Dict[str, Any]]:
        """
        Récupère un feedback spécifique.
        
        Args:
            feedback_id: Identifiant du feedback
            
        Returns:
            Dict: Données du feedback ou None si non trouvé
        """
        # Rechercher le feedback dans toutes les catégories
        for category in ["general", "security", "support", "pentest"]:
            category_path = os.path.join(self.storage_path, category)
            filepath = os.path.join(category_path, f"{feedback_id}.json")
            
            if os.path.exists(filepath):
                with open(filepath, 'r') as f:
                    return json.load(f)
        
        logger.warning(f"Feedback non trouvé: {feedback_id}")
        return None
    
    def update_feedback_status(self, 
                              feedback_id: str, 
                              status: str,
                              notes: Optional[str] = None) -> bool:
        """
        Met à jour le statut d'un feedback.
        
        Args:
            feedback_id: Identifiant du feedback
            status: Nouveau statut ('new', 'reviewed', 'actioned', 'ignored')
            notes: Notes supplémentaires
            
        Returns:
            bool: True si la mise à jour a réussi
        """
        feedback = self.get_feedback(feedback_id)
        if not feedback:
            return False
        
        # Mettre à jour le statut
        feedback["status"] = status
        if notes:
            feedback["notes"] = notes
        feedback["updated_at"] = datetime.now().isoformat()
        
        # Sauvegarder les modifications
        category = feedback["category"]
        category_path = os.path.join(self.storage_path, category)
        filepath = os.path.join(category_path, f"{feedback_id}.json")
        
        with open(filepath, 'w') as f:
            json.dump(feedback, f, indent=2)
        
        logger.info(f"Statut du feedback {feedback_id} mis à jour: {status}")
        return True
    
    def analyze_feedback(self, 
                        category: Optional[str] = None,
                        time_period: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyse le feedback collecté.
        
        Args:
            category: Catégorie à analyser (None pour toutes)
            time_period: Période d'analyse ('day', 'week', 'month', None pour tout)
            
        Returns:
            Dict: Résultats de l'analyse
        """
        # Déterminer les catégories à analyser
        categories = ["general", "security", "support", "pentest"]
        if category:
            categories = [category]
        
        # Collecter tous les feedbacks des catégories sélectionnées
        all_feedback = []
        for cat in categories:
            category_path = os.path.join(self.storage_path, cat)
            for filename in os.listdir(category_path):
                if filename.endswith(".json"):
                    filepath = os.path.join(category_path, filename)
                    with open(filepath, 'r') as f:
                        feedback = json.load(f)
                        all_feedback.append(feedback)
        
        # Filtrer par période si spécifiée
        if time_period:
            cutoff = self._get_cutoff_date(time_period)
            all_feedback = [
                f for f in all_feedback 
                if datetime.fromisoformat(f["timestamp"]) >= cutoff
            ]
        
        # Analyser les données
        analysis = self._perform_analysis(all_feedback)
        
        # Enregistrer l'analyse
        analysis_path = os.path.join(self.storage_path, "analysis")
        os.makedirs(analysis_path, exist_ok=True)
        
        analysis_id = f"analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        filepath = os.path.join(analysis_path, f"{analysis_id}.json")
        
        with open(filepath, 'w') as f:
            json.dump(analysis, f, indent=2)
        
        logger.info(f"Analyse de feedback complétée: {analysis_id}")
        
        # Envoyer des notifications si activé
        if self.notification_enabled:
            self._send_analysis_notification(analysis)
        
        return analysis
    
    def _check_for_analysis_trigger(self, feedback_type: str, category: str) -> None:
        """
        Vérifie si une analyse doit être déclenchée.
        
        Args:
            feedback_type: Type de feedback
            category: Catégorie du feedback
        """
        # Logique pour déterminer si une analyse doit être déclenchée
        # Par exemple, déclencher une analyse pour les feedbacks critiques
        if feedback_type in ["report", "critical"]:
            logger.info(f"Déclenchement d'une analyse pour un feedback critique dans la catégorie {category}")
            self.analyze_feedback(category=category, time_period="day")
    
    def _get_cutoff_date(self, time_period: str) -> datetime:
        """
        Calcule la date limite pour une période donnée.
        
        Args:
            time_period: Période ('day', 'week', 'month')
            
        Returns:
            datetime: Date limite
        """
        now = datetime.now()
        
        if time_period == "day":
            return datetime(now.year, now.month, now.day, 0, 0, 0)
        
        if time_period == "week":
            # Retourner le début de la semaine (lundi)
            days_since_monday = now.weekday()
            return datetime(now.year, now.month, now.day, 0, 0, 0) - datetime.timedelta(days=days_since_monday)
        
        if time_period == "month":
            return datetime(now.year, now.month, 1, 0, 0, 0)
        
        # Par défaut, retourner le début de la journée
        return datetime(now.year, now.month, now.day, 0, 0, 0)
    
    def _perform_analysis(self, feedback_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Effectue l'analyse du feedback.
        
        Args:
            feedback_list: Liste des feedbacks à analyser
            
        Returns:
            Dict: Résultats de l'analyse
        """
        # Initialiser les compteurs
        total = len(feedback_list)
        by_type = {}
        by_category = {}
        by_status = {}
        ratings = []
        
        # Analyser chaque feedback
        for feedback in feedback_list:
            # Compter par type
            feedback_type = feedback.get("type", "unknown")
            by_type[feedback_type] = by_type.get(feedback_type, 0) + 1
            
            # Compter par catégorie
            category = feedback.get("category", "unknown")
            by_category[category] = by_category.get(category, 0) + 1
            
            # Compter par statut
            status = feedback.get("status", "unknown")
            by_status[status] = by_status.get(status, 0) + 1
            
            # Collecter les ratings
            if feedback_type == "rating" and "rating" in feedback.get("content", {}):
                ratings.append(feedback["content"]["rating"])
        
        # Calculer la moyenne des ratings
        avg_rating = sum(ratings) / len(ratings) if ratings else 0
        
        # Préparer les résultats
        return {
            "timestamp": datetime.now().isoformat(),
            "total_feedback": total,
            "by_type": by_type,
            "by_category": by_category,
            "by_status": by_status,
            "average_rating": avg_rating,
            "rating_count": len(ratings),
            "period": "custom"
        }
    
    def _send_analysis_notification(self, analysis: Dict[str, Any]) -> None:
        """
        Envoie une notification d'analyse.
        
        Args:
            analysis: Résultats de l'analyse
        """
        logger.info(f"Envoi de notification d'analyse: {len(analysis['total_feedback'])} feedbacks analysés")
        
        # Logique pour envoyer des notifications (email, Slack, etc.)
        # Cette implémentation est un placeholder

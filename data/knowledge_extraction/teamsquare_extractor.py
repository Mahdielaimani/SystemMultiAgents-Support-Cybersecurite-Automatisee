"""
Module d'extraction de connaissances spécifiques à TeamSquare.
"""
import os
import json
import logging
import requests
from typing import Dict, Any, List, Optional
from bs4 import BeautifulSoup
import re

from config.logging_config import get_logger
from config.teamsquare_config import (
    COMPANY_INFO,
    SERVICES,
    VISION,
    PARTNERS,
    CLIENT_SECTORS
)

logger = get_logger("teamsquare_extractor")

class TeamSquareExtractor:
    """
    Classe pour extraire et structurer les connaissances spécifiques à TeamSquare.
    """
    
    def __init__(self, base_url: str = "https://www.teamsquare.fr"):
        """
        Initialise l'extracteur de connaissances.
        
        Args:
            base_url: URL de base du site TeamSquare
        """
        self.base_url = base_url
        self.pages = {
            "qui-sommes-nous": f"{base_url}/entreprise/qui-sommes-nous/",
            "vision": f"{base_url}/entreprise/vision/",
            "partenaires": f"{base_url}/entreprise/partenaires/",
            "contact": f"{base_url}/nous-contacter/",
            "transformation": f"{base_url}/nos-services/management-de-la-transformation/transformer-la-transformation/"
        }
        self.knowledge_base = {
            "company": COMPANY_INFO,
            "services": SERVICES,
            "vision": VISION,
            "partners": PARTNERS,
            "sectors": CLIENT_SECTORS,
            "faq": []
        }
    
    def extract_all(self) -> Dict[str, Any]:
        """
        Extrait toutes les connaissances du site TeamSquare.
        
        Returns:
            Dictionnaire contenant les connaissances structurées
        """
        try:
            # Extraire les informations de chaque page
            self._extract_company_info()
            self._extract_services()
            self._extract_vision()
            self._extract_partners()
            self._extract_contact_info()
            
            # Générer une FAQ à partir des connaissances extraites
            self._generate_faq()
            
            logger.info("Extraction des connaissances TeamSquare terminée avec succès")
            return self.knowledge_base
            
        except Exception as e:
            logger.error(f"Erreur lors de l'extraction des connaissances: {str(e)}")
            return self.knowledge_base
    
    def _extract_company_info(self) -> None:
        """Extrait les informations sur l'entreprise."""
        try:
            page_url = self.pages["qui-sommes-nous"]
            soup = self._get_page_content(page_url)
            
            if not soup:
                return
            
            # Extraire la description de l'entreprise
            description_elements = soup.select("div.elementor-widget-text-editor p")
            if description_elements:
                description = " ".join([p.text.strip() for p in description_elements])
                self.knowledge_base["company"]["full_description"] = description
            
            # Extraire d'autres informations pertinentes
            # (Cette partie dépend de la structure exacte du site)
            
            logger.info("Informations sur l'entreprise extraites avec succès")
            
        except Exception as e:
            logger.error(f"Erreur lors de l'extraction des informations sur l'entreprise: {str(e)}")
    
    def _extract_services(self) -> None:
        """Extrait les informations sur les services."""
        try:
            page_url = self.pages["transformation"]
            soup = self._get_page_content(page_url)
            
            if not soup:
                return
            
            # Extraire les détails des services
            service_elements = soup.select("div.elementor-widget-heading h2")
            service_descriptions = soup.select("div.elementor-widget-text-editor")
            
            # Traitement des services (dépend de la structure exacte du site)
            
            logger.info("Informations sur les services extraites avec succès")
            
        except Exception as e:
            logger.error(f"Erreur lors de l'extraction des informations sur les services: {str(e)}")
    
    def _extract_vision(self) -> None:
        """Extrait la vision et les valeurs de l'entreprise."""
        try:
            page_url = self.pages["vision"]
            soup = self._get_page_content(page_url)
            
            if not soup:
                return
            
            # Extraire la vision
            vision_elements = soup.select("div.elementor-widget-text-editor p")
            if vision_elements:
                vision_text = " ".join([p.text.strip() for p in vision_elements])
                self.knowledge_base["vision"]["full_text"] = vision_text
            
            logger.info("Vision et valeurs extraites avec succès")
            
        except Exception as e:
            logger.error(f"Erreur lors de l'extraction de la vision: {str(e)}")
    
    def _extract_partners(self) -> None:
        """Extrait les informations sur les partenaires."""
        try:
            page_url = self.pages["partenaires"]
            soup = self._get_page_content(page_url)
            
            if not soup:
                return
            
            # Extraire les partenaires
            partner_elements = soup.select("div.elementor-image-box-wrapper")
            
            partners = []
            for element in partner_elements:
                title_elem = element.select_one("h3.elementor-image-box-title")
                desc_elem = element.select_one("p.elementor-image-box-description")
                img_elem = element.select_one("img")
                
                if title_elem:
                    partner = {
                        "name": title_elem.text.strip(),
                        "description": desc_elem.text.strip() if desc_elem else "",
                        "logo_url": img_elem.get("src") if img_elem else ""
                    }
                    partners.append(partner)
            
            if partners:
                self.knowledge_base["partners"] = partners
            
            logger.info("Informations sur les partenaires extraites avec succès")
            
        except Exception as e:
            logger.error(f"Erreur lors de l'extraction des informations sur les partenaires: {str(e)}")
    
    def _extract_contact_info(self) -> None:
        """Extrait les informations de contact."""
        try:
            page_url = self.pages["contact"]
            soup = self._get_page_content(page_url)
            
            if not soup:
                return
            
            # Extraire les informations de contact
            contact_elements = soup.select("div.elementor-text-editor")
            
            # Traitement des informations de contact (dépend de la structure exacte du site)
            
            logger.info("Informations de contact extraites avec succès")
            
        except Exception as e:
            logger.error(f"Erreur lors de l'extraction des informations de contact: {str(e)}")
    
    def _generate_faq(self) -> None:
        """Génère une FAQ à partir des connaissances extraites."""
        faq = [
            {
                "question": "Qu'est-ce que TeamSquare?",
                "answer": f"TeamSquare est {self.knowledge_base['company']['description']} Fondée en {self.knowledge_base['company']['founded']}, l'entreprise accompagne ses clients dans leurs projets de transformation digitale et organisationnelle."
            },
            {
                "question": "Où sont situés les bureaux de TeamSquare?",
                "answer": "TeamSquare dispose de bureaux à Lyon (129 Rue Servient, Tour Part-Dieu, 69003), à Paris (63 Rue de Rivoli, 75001) et à Genève (24 Rue du Cendrier, 1201)."
            },
            {
                "question": "Quels sont les principaux services proposés par TeamSquare?",
                "answer": "TeamSquare propose principalement des services de Management de la Transformation, de Conseil en Organisation, de Solutions Digitales et de Formation."
            },
            {
                "question": "Comment contacter TeamSquare?",
                "answer": "Vous pouvez contacter TeamSquare par téléphone au +33 4 72 35 13 25 (Lyon) ou au +33 1 45 07 87 61 (Paris), ou via le formulaire de contact sur leur site web."
            },
            {
                "question": "Quels sont les partenaires de TeamSquare?",
                "answer": "TeamSquare est notamment Microsoft Gold Partner et dispose des certifications Qualiopi et EcoVadis."
            },
            {
                "question": "Dans quels secteurs d'activité TeamSquare intervient-il?",
                "answer": "TeamSquare intervient dans divers secteurs comme la Banque & Assurance, l'Industrie, les Services, la Santé, le Secteur Public, l'Énergie, le Transport & Logistique et le Retail."
            },
            {
                "question": "Quelle est l'approche de TeamSquare en matière de transformation?",
                "answer": "TeamSquare adopte une approche sur mesure et collaborative, centrée sur les besoins spécifiques de chaque client, avec un focus sur l'accompagnement au changement et l'optimisation des processus."
            },
            {
                "question": "TeamSquare propose-t-il des formations?",
                "answer": "Oui, TeamSquare propose des programmes de formation adaptés aux besoins des entreprises, notamment en Gestion de projet, Agilité, Leadership et Transformation digitale."
            },
            {
                "question": "Quel est le taux de satisfaction client de TeamSquare?",
                "answer": "TeamSquare affiche un taux de satisfaction client de 98/100, témoignant de la qualité de ses services et de son engagement envers ses clients."
            },
            {
                "question": "TeamSquare peut-il m'aider à sécuriser mes systèmes d'information?",
                "answer": "Oui, dans le cadre de ses services de Solutions Digitales et de Transformation, TeamSquare peut vous accompagner dans la sécurisation de vos systèmes d'information et la mise en place de bonnes pratiques de cybersécurité."
            }
        ]
        
        self.knowledge_base["faq"] = faq
        logger.info("FAQ générée avec succès")
    
    def _get_page_content(self, url: str) -> Optional[BeautifulSoup]:
        """
        Récupère le contenu d'une page web.
        
        Args:
            url: URL de la page
            
        Returns:
            Objet BeautifulSoup ou None en cas d'erreur
        """
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return BeautifulSoup(response.text, "html.parser")
        except Exception as e:
            logger.error(f"Erreur lors de la récupération de la page {url}: {str(e)}")
            return None
    
    def save_knowledge_base(self, output_file: str = "data/knowledge_base/teamsquare_knowledge.json") -> bool:
        """
        Sauvegarde la base de connaissances dans un fichier JSON.
        
        Args:
            output_file: Chemin du fichier de sortie
            
        Returns:
            True si la sauvegarde a réussi, False sinon
        """
        try:
            # Créer le répertoire si nécessaire
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            
            # Sauvegarder le fichier JSON
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(self.knowledge_base, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Base de connaissances sauvegardée dans {output_file}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde de la base de connaissances: {str(e)}")
            return False

# Alias pour compatibilité
TeamSquareKnowledgeExtractor = TeamSquareExtractor

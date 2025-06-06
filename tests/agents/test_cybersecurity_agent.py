"""
Tests pour l'agent de cybersécurité.
"""
import pytest
from unittest.mock import MagicMock, patch
import json
import os
import asyncio

# Import des modules à tester
from agents.cybersecurity_agent.agent import CybersecurityAgent
from agents.cybersecurity_agent.classifier import VulnerabilityClassifier
from agents.cybersecurity_agent.scanner import WebScanner
from agents.cybersecurity_agent.recommender import SecurityRecommender
from agents.cybersecurity_agent.report import ReportGenerator
from core.event_bus import EventBus
from core.memory import ConversationMemory

class TestCybersecurityAgent:
    """Tests pour l'agent de cybersécurité."""
    
    @pytest.fixture
    def mock_event_bus(self):
        """Fixture pour créer un bus d'événements simulé."""
        event_bus = MagicMock(spec=EventBus)
        return event_bus
    
    @pytest.fixture
    def mock_memory(self):
        """Fixture pour créer une mémoire conversationnelle simulée."""
        memory = MagicMock(spec=ConversationMemory)
        return memory
    
    @pytest.fixture
    def mock_classifier(self):
        """Fixture pour créer un classificateur de vulnérabilités simulé."""
        classifier = MagicMock(spec=VulnerabilityClassifier)
        classifier.classify.return_value = {
            "label": "sql_injection",
            "score": 0.92
        }
        return classifier
    
    @pytest.fixture
    def mock_scanner(self):
        """Fixture pour créer un scanner web simulé."""
        scanner = MagicMock(spec=WebScanner)
        scanner.scan_url.return_value = asyncio.Future()
        scanner.scan_url.return_value.set_result({
            "success": True,
            "vulnerabilities": [
                {
                    "name": "Absence d'en-tête X-Content-Type-Options",
                    "severity": "low",
                    "description": "L'en-tête X-Content-Type-Options n'est pas défini."
                }
            ]
        })
        return scanner
    
    @pytest.fixture
    def cybersecurity_agent(self, mock_event_bus, mock_memory):
        """Fixture pour créer un agent de cybersécurité."""
        settings = {
            "vulnerability_model_path": "models/vulnerability_classifier",
            "device": -1,
            "zap_api_key": "",
            "zap_proxy": "localhost:8080"
        }
        
        agent = CybersecurityAgent(settings, mock_event_bus, mock_memory)
        return agent
    
    @pytest.mark.asyncio
    async def test_agent_initialization(self, cybersecurity_agent):
        """Teste l'initialisation de l'agent de cybersécurité."""
        # Patcher les méthodes qui chargent les modèles
        with patch.object(cybersecurity_agent, '_load_model', return_value=None):
            await cybersecurity_agent.initialize()
            assert cybersecurity_agent is not None
    
    @pytest.mark.asyncio
    async def test_security_analysis(self, cybersecurity_agent, mock_classifier):
        """Teste l'analyse de sécurité."""
        # Remplacer le classificateur par notre mock
        cybersecurity_agent.vulnerability_classifier = mock_classifier
        
        # Données de test
        test_query = "Comment puis-je me protéger contre les injections SQL?"
        
        # Effectuer l'analyse
        result = await cybersecurity_agent.analyze_security_query(test_query)
        
        # Vérifications
        assert result is not None
        assert result["is_security_related"] == True
        assert "sql_injection" in result["vulnerability_type"]
        assert "detected_keywords" in result
        assert len(result["detected_keywords"]) > 0
    
    @pytest.mark.asyncio
    async def test_scan_request_detection(self, cybersecurity_agent):
        """Teste la détection des demandes de scan."""
        # Données de test
        scan_request = "Pouvez-vous scanner https://example.com pour des vulnérabilités?"
        regular_question = "Qu'est-ce qu'une injection SQL?"
        
        # Vérifications
        assert cybersecurity_agent._is_scan_request(scan_request) == True
        assert cybersecurity_agent._is_scan_request(regular_question) == False
    
    @pytest.mark.asyncio
    async def test_scan_url(self, cybersecurity_agent, mock_scanner):
        """Teste le scan d'URL."""
        # Remplacer le scanner par notre mock
        cybersecurity_agent.scanner = mock_scanner
        
        # Données de test
        url = "https://example.com"
        session_id = "test_session"
        
        # Patcher la méthode _run_scan_simulation pour éviter l'exécution asynchrone
        with patch.object(cybersecurity_agent, '_run_scan_simulation', return_value=None):
            scan_id = await cybersecurity_agent._start_scan(url, session_id)
            
            # Vérifications
            assert scan_id is not None
            assert session_id in cybersecurity_agent.active_scans
            assert cybersecurity_agent.active_scans[session_id]["target"] == url
            assert cybersecurity_agent.active_scans[session_id]["status"] == "running"
    
    @pytest.mark.asyncio
    async def test_process_security_query(self, cybersecurity_agent, mock_classifier):
        """Teste le traitement d'une requête de sécurité."""
        # Remplacer le classificateur par notre mock
        cybersecurity_agent.vulnerability_classifier = mock_classifier
        
        # Patcher les méthodes nécessaires
        with patch.object(cybersecurity_agent, '_generate_security_response', return_value="Réponse de sécurité"):
            # Données de test
            query = "Comment puis-je me protéger contre les injections SQL?"
            session_id = "test_session"
            
            # Traiter la requête
            response = await cybersecurity_agent._handle_security_analysis(query, session_id)
            
            # Vérifications
            assert response is not None
            assert "content" in response
            assert response["content"] == "Réponse de sécurité"
    
    @pytest.mark.asyncio
    async def test_process_scan_request(self, cybersecurity_agent):
        """Teste le traitement d'une demande de scan."""
        # Patcher les méthodes nécessaires
        with patch.object(cybersecurity_agent, '_start_scan', return_value="scan_123"):
            # Données de test
            query = "Scannez https://example.com pour des vulnérabilités"
            session_id = "test_session"
            
            # Traiter la requête
            response = await cybersecurity_agent._handle_scan_request(query, session_id)
            
            # Vérifications
            assert response is not None
            assert "content" in response
            assert "https://example.com" in response["content"]

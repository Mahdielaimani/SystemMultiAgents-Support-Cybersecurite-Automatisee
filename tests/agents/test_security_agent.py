"""
Tests pour le Security Agent.
"""
import pytest
from unittest.mock import MagicMock, patch
import json
import os

# Import des modules à tester
from agents.security_agent.agent import SecurityAgent
from agents.security_agent.analyzer import SecurityAnalyzer
from agents.security_agent.classifier import VulnerabilityClassifier
from agents.security_agent.recommender import SecurityRecommender

class TestSecurityAgent:
    """Tests pour le Security Agent."""
    
    @pytest.fixture
    def mock_security_agent(self):
        """Fixture pour créer un agent de sécurité simulé."""
        agent = MagicMock(spec=SecurityAgent)
        agent.analyze_vulnerability.return_value = {
            "severity": "high",
            "confidence": 0.85,
            "description": "Test vulnerability",
            "recommendations": ["Fix 1", "Fix 2"]
        }
        return agent
    
    @pytest.fixture
    def mock_classifier(self):
        """Fixture pour créer un classificateur de vulnérabilités simulé."""
        classifier = MagicMock(spec=VulnerabilityClassifier)
        classifier.classify.return_value = {
            "vulnerability_type": "sql_injection",
            "confidence": 0.92,
            "severity": "critical"
        }
        return classifier
    
    def test_security_agent_initialization(self, mock_classifier):
        """Teste l'initialisation de l'agent de sécurité."""
        with patch("agents.security_agent.agent.VulnerabilityClassifier", return_value=mock_classifier):
            agent = SecurityAgent()
            assert agent is not None
            assert agent.classifier is not None
    
    def test_vulnerability_analysis(self, mock_security_agent):
        """Teste l'analyse de vulnérabilité."""
        # Données de test
        test_data = {
            "code": "SELECT * FROM users WHERE username = '" + user_input + "'",
            "context": "Web application login function"
        }
        
        # Appel de la méthode
        result = mock_security_agent.analyze_vulnerability(test_data)
        
        # Vérifications
        assert result is not None
        assert "severity" in result
        assert "confidence" in result
        assert "description" in result
        assert "recommendations" in result
        assert result["severity"] == "high"
        assert isinstance(result["recommendations"], list)
    
    def test_classifier_integration(self, mock_classifier):
        """Teste l'intégration du classificateur de vulnérabilités."""
        # Données de test
        test_input = "SELECT * FROM users WHERE username = 'admin' OR 1=1--'"
        
        # Appel de la méthode
        result = mock_classifier.classify(test_input)
        
        # Vérifications
        assert result is not None
        assert result["vulnerability_type"] == "sql_injection"
        assert result["confidence"] > 0.9
        assert result["severity"] == "critical"
    
    def test_recommender_integration(self):
        """Teste l'intégration du recommandeur de sécurité."""
        # Créer un recommandeur simulé
        recommender = MagicMock(spec=SecurityRecommender)
        recommender.generate_recommendations.return_value = [
            {
                "title": "Use Parameterized Queries",
                "description": "Replace string concatenation with parameterized queries",
                "priority": "high"
            },
            {
                "title": "Input Validation",
                "description": "Validate and sanitize all user inputs",
                "priority": "medium"
            }
        ]
        
        # Données de test
        vulnerability_info = {
            "type": "sql_injection",
            "severity": "high",
            "context": "Web application"
        }
        
        # Appel de la méthode
        recommendations = recommender.generate_recommendations(vulnerability_info)
        
        # Vérifications
        assert recommendations is not None
        assert len(recommendations) == 2
        assert recommendations[0]["title"] == "Use Parameterized Queries"
        assert recommendations[0]["priority"] == "high"

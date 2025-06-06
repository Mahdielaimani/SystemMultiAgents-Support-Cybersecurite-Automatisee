"""
Tests pour le scanner web.
"""
import pytest
from unittest.mock import MagicMock, patch
import asyncio
import requests

from agents.cybersecurity_agent.scanner import WebScanner

class TestWebScanner:
    """Tests pour le scanner web."""
    
    @pytest.fixture
    def mock_requests_get(self):
        """Fixture pour simuler requests.get."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {
            "Server": "nginx/1.18.0",
            "Content-Type": "text/html; charset=utf-8"
        }
        
        with patch('requests.get', return_value=mock_response) as mock_get:
            yield mock_get
    
    def test_scanner_initialization(self, mock_requests_get):
        """Teste l'initialisation du scanner."""
        # Simuler une réponse positive pour la vérification de ZAP
        mock_requests_get.return_value.status_code = 200
        
        scanner = WebScanner(zap_api_key="test_key", zap_proxy="localhost:8080")
        
        assert scanner is not None
        assert scanner.zap_api_key == "test_key"
        assert scanner.zap_proxy == "localhost:8080"
        assert scanner.zap_available == True
    
    def test_scanner_initialization_no_zap(self, mock_requests_get):
        """Teste l'initialisation du scanner sans ZAP disponible."""
        # Simuler une erreur pour la vérification de ZAP
        mock_requests_get.side_effect = requests.exceptions.ConnectionError("Connection refused")
        
        scanner = WebScanner(zap_api_key="test_key", zap_proxy="localhost:8080")
        
        assert scanner is not None
        assert scanner.zap_available == False
    
    @pytest.mark.asyncio
    async def test_basic_scan(self, mock_requests_get):
        """Teste le scan basique d'une URL."""
        # Simuler une réponse HTTP
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {}  # Aucun en-tête de sécurité
        mock_requests_get.return_value = mock_response
        
        scanner = WebScanner()
        scanner.zap_available = False
        
        # Effectuer le scan
        result = await scanner._basic_scan("https://example.com")
        
        # Vérifications
        assert result is not None
        assert result["success"] == True
        assert len(result["vulnerabilities"]) > 0
        
        # Vérifier que les vulnérabilités liées aux en-têtes manquants sont détectées
        header_vulnerabilities = [v for v in result["vulnerabilities"] if "en-tête" in v["name"]]
        assert len(header_vulnerabilities) > 0
    
    @pytest.mark.asyncio
    async def test_scan_url_invalid(self):
        """Teste le scan d'une URL invalide."""
        scanner = WebScanner()
        
        # Effectuer le scan avec une URL invalide
        result = await scanner.scan_url("not_a_valid_url")
        
        # Vérifications
        assert result is not None
        assert result["success"] == False
        assert "error" in result
        assert len(result["vulnerabilities"]) == 0
    
    @pytest.mark.asyncio
    async def test_scan_with_zap(self):
        """Teste le scan avec ZAP."""
        scanner = WebScanner()
        scanner.zap_available = True
        
        # Patcher la méthode _scan_with_zap
        with patch.object(scanner, '_scan_with_zap') as mock_scan:
            mock_scan.return_value = {
                "success": True,
                "scan_id": "zap_scan_123",
                "vulnerabilities": [
                    {
                        "name": "Test Vulnerability",
                        "severity": "high",
                        "description": "Test description"
                    }
                ]
            }
            
            # Effectuer le scan
            result = await scanner.scan_url("https://example.com")
            
            # Vérifications
            assert result is not None
            assert result["success"] == True
            assert result["scan_id"] == "zap_scan_123"
            assert len(result["vulnerabilities"]) == 1
            assert result["vulnerabilities"][0]["name"] == "Test Vulnerability"

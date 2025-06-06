"""
Configuration et fixtures pour les tests pytest.
"""
import pytest
from unittest.mock import MagicMock

@pytest.fixture
def mock_llm():
    """Fixture pour simuler un LLM."""
    mock = MagicMock()
    mock.generate.return_value = {"text": "Réponse simulée du LLM"}
    return mock

@pytest.fixture
def mock_vector_db():
    """Fixture pour simuler une base de données vectorielle."""
    mock = MagicMock()
    mock.search.return_value = [
        {"id": "doc1", "text": "Document 1", "metadata": {}, "score": 0.95},
        {"id": "doc2", "text": "Document 2", "metadata": {}, "score": 0.85}
    ]
    return mock

@pytest.fixture
def mock_graph_db():
    """Fixture pour simuler une base de données graphe."""
    mock = MagicMock()
    mock.query.return_value = [{"node": {"id": "node1", "type": "vulnerability"}}]
    return mock

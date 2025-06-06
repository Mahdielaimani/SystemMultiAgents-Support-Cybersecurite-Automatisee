"""
Outils pour l'agent support agentic
"""

# Imports des outils disponibles
try:
    from .knowledge_retriever import KnowledgeRetriever
    KNOWLEDGE_RETRIEVER_AVAILABLE = True
except ImportError:
    KNOWLEDGE_RETRIEVER_AVAILABLE = False

try:
    from .web_browser import WebBrowser
    WEB_BROWSER_AVAILABLE = True
except ImportError:
    WEB_BROWSER_AVAILABLE = False

__all__ = []

if KNOWLEDGE_RETRIEVER_AVAILABLE:
    __all__.append('KnowledgeRetriever')

if WEB_BROWSER_AVAILABLE:
    __all__.append('WebBrowser')

"""
Module for LangChain tools in NetGuardian.
"""
from typing import Dict, List, Any, Optional
from langchain_core.tools import BaseTool, Tool
from pydantic import BaseModel, Field

from config.logging_config import get_logger

logger = get_logger("langchain_tools")

class SearchVectorDBInput(BaseModel):
    """Input for the search vector database tool."""
    query: str = Field(..., description="The query to search for in the vector database")
    collection_name: str = Field(default="default", description="The name of the collection to search in")
    n_results: int = Field(default=5, description="The number of results to return")

def search_vector_db(input_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Search the vector database for similar documents."""
    from data.vector_db.chroma_manager import ChromaManager
    
    query = input_data.get("query")
    collection_name = input_data.get("collection_name", "default")
    n_results = input_data.get("n_results", 5)
    
    chroma_manager = ChromaManager()
    results = chroma_manager.search(
        collection_name=collection_name,
        query_texts=[query],
        n_results=n_results
    )
    
    return results[0] if results else []

class QueryKnowledgeGraphInput(BaseModel):
    """Input for the query knowledge graph tool."""
    query: str = Field(..., description="The Cypher query to execute on the knowledge graph")

def query_knowledge_graph(input_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Execute a Cypher query on the knowledge graph."""
    from core.graph_manager import KnowledgeGraphManager
    
    query = input_data.get("query")
    
    kg_manager = KnowledgeGraphManager()
    results = kg_manager.search_entities(query)
    
    return results

class SecurityScanInput(BaseModel):
    """Input for the security scan tool."""
    target: str = Field(..., description="The target to scan (URL, IP, domain, etc.)")
    scan_type: str = Field(default="basic", description="The type of scan to perform")

def security_scan(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """Perform a security scan on a target."""
    from agents.security_agent.analyzer import analyze_security_issue
    
    target = input_data.get("target")
    scan_type = input_data.get("scan_type", "basic")
    
    # Créer une description fictive pour la démonstration
    issue_description = f"Security scan of {target} using {scan_type} scan type"
    
    results = analyze_security_issue(issue_description)
    return results

def get_default_tools() -> List[BaseTool]:
    """Get the default set of tools for the agent."""
    tools = [
        Tool.from_function(
            func=search_vector_db,
            name="search_vector_db",
            description="Search the vector database for documents similar to the query",
            args_schema=SearchVectorDBInput
        ),
        Tool.from_function(
            func=query_knowledge_graph,
            name="query_knowledge_graph",
            description="Search the knowledge graph for entities related to the query",
            args_schema=QueryKnowledgeGraphInput
        ),
        Tool.from_function(
            func=security_scan,
            name="security_scan",
            description="Perform a security scan on a target",
            args_schema=SecurityScanInput
        )
    ]
    
    return tools

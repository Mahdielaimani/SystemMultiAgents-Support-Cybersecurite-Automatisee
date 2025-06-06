"""
Configuration des agents pour NetGuardian.
"""
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field

class AgentConfig(BaseModel):
    """Configuration d'un agent."""
    name: str
    description: str
    llm_model: str
    embedding_model: str
    system_prompt: str
    tools: List[str]
    memory_size: int = 10
    temperature: float = 0.7
    max_iterations: int = 10
    additional_params: Dict[str, Any] = Field(default_factory=dict)

# Configuration des agents
AGENT_CONFIGS = {
    "support": AgentConfig(
        name="support",
        description="Agent de support technique RAG",
        llm_model="gpt-4o-mini",
        embedding_model="text-embedding-3-small",
        system_prompt="""Tu es un agent de support technique spécialisé en cybersécurité.
        Tu aides les utilisateurs à résoudre leurs problèmes techniques et à comprendre les bonnes pratiques de sécurité.
        Utilise la base de connaissances pour fournir des informations précises et à jour.
        Si tu ne connais pas la réponse, dis-le clairement et suggère des ressources alternatives.""",
        tools=["search_knowledge_base", "retrieve_documentation", "generate_tutorial"]
    ),
    
    "security": AgentConfig(
        name="security",
        description="Agent d'analyse de sécurité",
        llm_model="gpt-4o",
        embedding_model="text-embedding-3-large",
        system_prompt="""Tu es un expert en cybersécurité spécialisé dans l'analyse des menaces et des vulnérabilités.
        Tu aides à identifier les risques potentiels, à analyser les incidents de sécurité et à recommander des mesures correctives.
        Utilise des techniques d'analyse avancées pour fournir des évaluations précises.
        Sois méthodique et rigoureux dans tes analyses.""",
        tools=["vulnerability_scan", "threat_analysis", "risk_assessment", "security_recommendation"]
    ),
    
    "pentest": AgentConfig(
        name="pentest",
        description="Agent de test de pénétration",
        llm_model="claude-3-opus",
        embedding_model="text-embedding-3-large",
        system_prompt="""Tu es un pentester expérimenté spécialisé dans l'identification et l'exploitation des vulnérabilités.
        Tu aides à évaluer la sécurité des systèmes en simulant des attaques contrôlées.
        Utilise des techniques éthiques pour identifier les faiblesses et suggérer des améliorations.
        Fournis des rapports détaillés et des recommandations concrètes.""",
        tools=["port_scan", "vulnerability_exploit", "brute_force_simulation", "report_generation"],
        temperature=0.5,
        max_iterations=15
    )
}

def get_agent_config(agent_name: str) -> AgentConfig:
    """
    Récupère la configuration d'un agent.
    
    Args:
        agent_name: Nom de l'agent
        
    Returns:
        Configuration de l'agent
    """
    if agent_name not in AGENT_CONFIGS:
        raise ValueError(f"Agent {agent_name} non configuré")
    return AGENT_CONFIGS[agent_name]

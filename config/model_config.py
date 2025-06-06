"""
Configuration des modèles pour NetGuardian.
"""
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field

class ModelConfig(BaseModel):
    """Configuration d'un modèle."""
    name: str
    provider: str
    api_key_env: str
    max_tokens: int = 4096
    temperature: float = 0.7
    top_p: float = 1.0
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    stop_sequences: List[str] = []
    system_prompt: Optional[str] = None
    additional_params: Dict[str, Any] = Field(default_factory=dict)

class EmbeddingModelConfig(BaseModel):
    """Configuration d'un modèle d'embedding."""
    name: str
    provider: str
    api_key_env: str
    dimensions: int
    additional_params: Dict[str, Any] = Field(default_factory=dict)

# Configuration des modèles LLM
LLM_MODELS = {
    "gpt-4o-mini": ModelConfig(
        name="gpt-4o-mini",
        provider="openai",
        api_key_env="OPENAI_API_KEY",
        max_tokens=4096,
        temperature=0.7,
        system_prompt="Tu es un assistant spécialisé en cybersécurité, capable d'aider avec des questions techniques et de sécurité."
    ),
    "gpt-4o": ModelConfig(
        name="gpt-4o",
        provider="openai",
        api_key_env="OPENAI_API_KEY",
        max_tokens=8192,
        temperature=0.7,
        system_prompt="Tu es un expert en cybersécurité avancée, capable d'analyser des situations complexes et de fournir des conseils détaillés."
    ),
    "claude-3-opus": ModelConfig(
        name="claude-3-opus-20240229",
        provider="anthropic",
        api_key_env="ANTHROPIC_API_KEY",
        max_tokens=4096,
        temperature=0.7,
        system_prompt="Tu es un expert en cybersécurité spécialisé dans l'analyse approfondie et les recommandations stratégiques."
    ),
    "mistral-large": ModelConfig(
        name="mistral-large-latest",
        provider="mistral",
        api_key_env="MISTRAL_API_KEY",
        max_tokens=4096,
        temperature=0.7,
        system_prompt="Tu es un spécialiste en cybersécurité qui fournit des analyses techniques précises et des recommandations pratiques."
    )
}

# Configuration des modèles d'embedding
EMBEDDING_MODELS = {
    "text-embedding-3-small": EmbeddingModelConfig(
        name="text-embedding-3-small",
        provider="openai",
        api_key_env="OPENAI_API_KEY",
        dimensions=1536
    ),
    "text-embedding-3-large": EmbeddingModelConfig(
        name="text-embedding-3-large",
        provider="openai",
        api_key_env="OPENAI_API_KEY",
        dimensions=3072
    ),
    "mistral-embed": EmbeddingModelConfig(
        name="mistral-embed",
        provider="mistral",
        api_key_env="MISTRAL_API_KEY",
        dimensions=1024
    )
}

def get_model_config(model_name: str) -> ModelConfig:
    """
    Récupère la configuration d'un modèle LLM.
    
    Args:
        model_name: Nom du modèle
        
    Returns:
        Configuration du modèle
    """
    if model_name not in LLM_MODELS:
        raise ValueError(f"Modèle {model_name} non configuré")
    return LLM_MODELS[model_name]

def get_embedding_config(model_name: str) -> EmbeddingModelConfig:
    """
    Récupère la configuration d'un modèle d'embedding.
    
    Args:
        model_name: Nom du modèle
        
    Returns:
        Configuration du modèle d'embedding
    """
    if model_name not in EMBEDDING_MODELS:
        raise ValueError(f"Modèle d'embedding {model_name} non configuré")
    return EMBEDDING_MODELS[model_name]

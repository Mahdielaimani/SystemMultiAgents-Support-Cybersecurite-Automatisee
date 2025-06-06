"""
Configuration settings for the NextGen-Agent.
"""

import os
from pathlib import Path
from typing import Dict, List, Optional

from dotenv import load_dotenv
from pydantic import BaseSettings, Field

# Load environment variables
load_dotenv()

class Settings(BaseSettings):
    """Application settings."""
    
    # Base paths
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
    CACHE_DIR: str = Field(default="./cache")
    DATA_DIR: str = Field(default="./data")
    MODELS_DIR: str = Field(default="./models")
    
    # API keys
    OPENAI_API_KEY: str = Field(default="")
    OPENAI_ORG_ID: Optional[str] = Field(default=None)
    WANDB_API_KEY: Optional[str] = Field(default=None)
    
    # Model configuration
    DEFAULT_LLM_MODEL: str = Field(default="gpt-4")
    EMBEDDING_MODEL: str = Field(default="text-embedding-ada-002")
    TEMPERATURE: float = Field(default=0.7)
    MAX_TOKENS: int = Field(default=2000)
    
    # Vector database configuration
    CHROMA_DB_PATH: str = Field(default="./data/chromadb")
    
    # Neo4j configuration
    NEO4J_URI: str = Field(default="bolt://localhost:7687")
    NEO4J_USERNAME: str = Field(default="neo4j")
    NEO4J_PASSWORD: str = Field(default="password")
    
    # Weights & Biases configuration
    WANDB_PROJECT: str = Field(default="nextgen-agent")
    WANDB_ENTITY: Optional[str] = Field(default=None)
    
    # Logging configuration
    LOG_LEVEL: str = Field(default="INFO")
    LOG_FILE: str = Field(default="./logs/agent.log")
    
    # Application configuration
    DEBUG_MODE: bool = Field(default=False)
    
    # Agent configuration
    AGENT_MEMORY_SIZE: int = Field(default=10)
    AGENT_REFLECTION_THRESHOLD: float = Field(default=0.7)
    
    # Tool configuration
    ENABLED_TOOLS: List[str] = Field(default=["search", "calculator", "knowledge_graph"])
    
    # Prompt templates
    PROMPT_TEMPLATES: Dict[str, str] = Field(default={
        "default": "You are an advanced AI assistant. Answer the following question: {query}",
        "reflection": "Reflect on the following interaction and identify areas for improvement: {interaction}",
        "planning": "Create a step-by-step plan to solve the following problem: {problem}",
        "reasoning": "Reason through the following problem step by step: {problem}",
    })
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Create a global settings instance
settings = Settings()

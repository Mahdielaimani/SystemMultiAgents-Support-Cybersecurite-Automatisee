"""
Base module for LangChain integration in NetGuardian.
"""
from typing import Dict, List, Any, Optional
from langchain_core.language_models import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_mistralai import ChatMistralAI
from langchain.chains import LLMChain
from langchain.callbacks.base import BaseCallbackHandler

from config.settings import settings
from config.logging_config import get_logger

logger = get_logger("langchain_base")

class LangChainModelFactory:
    """Factory for creating LangChain models."""
    
    @staticmethod
    def create_model(
        model_type: str,
        model_name: str,
        temperature: float = 0.7,
        streaming: bool = False,
        callbacks: Optional[List[BaseCallbackHandler]] = None
    ) -> BaseChatModel:
        """Create a LangChain model based on type and name."""
        if model_type.lower() == "openai":
            return ChatOpenAI(
                model=model_name,
                temperature=temperature,
                openai_api_key=settings.OPENAI_API_KEY,
                streaming=streaming,
                callbacks=callbacks
            )
        elif model_type.lower() == "anthropic":
            return ChatAnthropic(
                model=model_name,
                temperature=temperature,
                anthropic_api_key=settings.ANTHROPIC_API_KEY,
                streaming=streaming,
                callbacks=callbacks
            )
        elif model_type.lower() == "mistral":
            return ChatMistralAI(
                model=model_name,
                temperature=temperature,
                mistral_api_key=settings.MISTRAL_API_KEY,
                streaming=streaming,
                callbacks=callbacks
            )
        else:
            raise ValueError(f"Unsupported model type: {model_type}")

class ChainFactory:
    """Factory for creating LangChain chains."""
    
    @staticmethod
    def create_basic_chain(
        llm: BaseChatModel,
        prompt_template: str,
        input_variables: List[str],
        output_parser: Any = None
    ) -> LLMChain:
        """Create a basic LLMChain with the given parameters."""
        prompt = ChatPromptTemplate.from_template(prompt_template)
        
        if output_parser is None:
            output_parser = StrOutputParser()
            
        chain = prompt | llm | output_parser
        return chain

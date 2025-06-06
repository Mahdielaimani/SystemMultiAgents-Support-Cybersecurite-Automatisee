"""
Module for LangChain agents in NetGuardian.
"""
from typing import List, Dict, Any, Optional
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain_core.language_models import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import BaseTool

from core.langchain_integration.base import LangChainModelFactory
from config.logging_config import get_logger

logger = get_logger("langchain_agents")

class AgentFactory:
    """Factory for creating LangChain agents."""
    
    @staticmethod
    def create_openai_functions_agent(
        llm: Optional[BaseChatModel] = None,
        tools: List[BaseTool] = None,
        system_message: str = None,
        verbose: bool = False
    ) -> AgentExecutor:
        """Create an OpenAI functions agent."""
        if llm is None:
            llm = LangChainModelFactory.create_model(
                model_type="openai",
                model_name="gpt-4o-mini",
                temperature=0.7
            )
            
        if tools is None:
            tools = []
            
        if system_message is None:
            system_message = """You are an advanced AI assistant that helps users with their tasks.
            You have access to tools that you can use to help users. Use these tools wisely."""
            
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_message),
            ("user", "{input}"),
        ])
        
        agent = create_openai_functions_agent(llm, tools, prompt)
        agent_executor = AgentExecutor(
            agent=agent,
            tools=tools,
            verbose=verbose,
            handle_parsing_errors=True
        )
        
        return agent_executor

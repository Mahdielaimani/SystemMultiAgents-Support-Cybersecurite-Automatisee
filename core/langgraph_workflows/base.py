"""
Base module for LangGraph workflows in NetGuardian.
"""
from typing import Dict, List, Any, Annotated, TypedDict, Literal
from enum import Enum
import operator
import json

from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolExecutor

from core.langchain_integration.agents import AgentFactory
from core.langchain_integration.tools import get_default_tools
from config.logging_config import get_logger

logger = get_logger("langgraph_base")

class AgentState(TypedDict):
    """State for the agent workflow."""
    messages: Annotated[List[BaseMessage], operator.add]
    next: str

class AgentStateAction(str, Enum):
    """Actions for the agent state."""
    AGENT = "agent"
    TOOL = "tool"
    END = "end"

def create_basic_agent_workflow(
    system_message: str = None,
    tools: List[Any] = None,
    verbose: bool = False
) -> StateGraph:
    """Create a basic agent workflow using LangGraph."""
    if tools is None:
        tools = get_default_tools()
        
    # Create the agent
    agent_executor = AgentFactory.create_openai_functions_agent(
        system_message=system_message,
        tools=tools,
        verbose=verbose
    )
    
    # Create the tool executor
    tool_executor = ToolExecutor(tools)
    
    # Define the workflow
    workflow = StateGraph(AgentState)
    
    # Define the nodes
    def agent_node(state: AgentState) -> AgentState:
        """Agent node in the workflow."""
        messages = state["messages"]
        result = agent_executor.invoke({"messages": messages})
        return {"messages": [result], "next": AgentStateAction.TOOL.value}
    
    def tool_node(state: AgentState) -> AgentState:
        """Tool node in the workflow."""
        messages = state["messages"]
        last_message = messages[-1]
        
        # Check if the message has a tool call
        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            tool_calls = last_message.tool_calls
            actions = []
            
            for tool_call in tool_calls:
                action = {
                    "tool": tool_call["name"],
                    "tool_input": json.loads(tool_call["args"])
                }
                actions.append(action)
                
            # Execute the tools
            responses = []
            for action in actions:
                response = tool_executor.invoke(action)
                responses.append(response)
                
            # Create tool response messages
            tool_response_messages = []
            for i, response in enumerate(responses):
                tool_response_messages.append(
                    AIMessage(content=str(response), name=actions[i]["tool"])
                )
                
            return {"messages": tool_response_messages, "next": AgentStateAction.AGENT.value}
        else:
            # No tool calls, end the workflow
            return {"messages": messages, "next": AgentStateAction.END.value}
    
    # Add nodes to the workflow
    workflow.add_node(AgentStateAction.AGENT.value, agent_node)
    workflow.add_node(AgentStateAction.TOOL.value, tool_node)
    
    # Add edges
    workflow.add_edge(AgentStateAction.AGENT.value, AgentStateAction.TOOL.value)
    workflow.add_edge(AgentStateAction.TOOL.value, AgentStateAction.AGENT.value)
    workflow.add_edge(AgentStateAction.TOOL.value, END)
    
    # Set the entry point
    workflow.set_entry_point(AgentStateAction.AGENT.value)
    
    return workflow.compile()

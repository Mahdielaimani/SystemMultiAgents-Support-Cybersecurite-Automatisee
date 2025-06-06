"""
Module for specific LangGraph workflows in NetGuardian.
"""
from typing import Dict, List, Any, Optional, TypedDict, Annotated, Union, Literal
import operator
from enum import Enum

from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolExecutor

from core.langchain_integration.base import LangChainModelFactory
from core.langchain_integration.tools import get_default_tools
from core.langgraph_workflows.base import create_basic_agent_workflow
from config.logging_config import get_logger

logger = get_logger("langgraph_workflows")

class ReasoningState(TypedDict):
    """State for the reasoning workflow."""
    messages: Annotated[List[BaseMessage], operator.add]
    reasoning: Optional[str]
    plan: Optional[List[str]]
    current_step: Optional[int]
    results: Optional[Dict[str, Any]]
    next: str

class ReasoningAction(str, Enum):
    """Actions for the reasoning workflow."""
    PLANNER = "planner"
    REASONER = "reasoner"
    EXECUTOR = "executor"
    SYNTHESIZER = "synthesizer"
    END = "end"

def create_reasoning_workflow(
    system_message: str = None,
    tools: List[Any] = None,
    verbose: bool = False
) -> StateGraph:
    """Create a reasoning workflow using LangGraph."""
    if tools is None:
        tools = get_default_tools()
        
    if system_message is None:
        system_message = """You are an advanced AI assistant that helps users with complex tasks.
        You follow a structured reasoning process:
        1. Understand the problem
        2. Create a plan
        3. Execute the plan step by step
        4. Synthesize the results
        """
    
    # Create the LLMs
    planner_llm = LangChainModelFactory.create_model(
        model_type="openai",
        model_name="gpt-4o-mini",
        temperature=0.7
    )
    
    reasoner_llm = LangChainModelFactory.create_model(
        model_type="openai",
        model_name="gpt-4o-mini",
        temperature=0.2
    )
    
    executor_llm = LangChainModelFactory.create_model(
        model_type="openai",
        model_name="gpt-4o-mini",
        temperature=0.5
    )
    
    synthesizer_llm = LangChainModelFactory.create_model(
        model_type="openai",
        model_name="gpt-4o-mini",
        temperature=0.7
    )
    
    # Create the tool executor
    tool_executor = ToolExecutor(tools)
    
    # Define the workflow
    workflow = StateGraph(ReasoningState)
    
    # Define the nodes
    def planner_node(state: ReasoningState) -> ReasoningState:
        """Planner node in the workflow."""
        messages = state["messages"]
        
        # Create a planning prompt
        planning_prompt = HumanMessage(
            content=f"""Based on the following conversation, create a step-by-step plan to address the user's request.
            
            {messages[-1].content}
            
            Provide a clear, numbered list of steps to follow.
            """
        )
        
        # Get the plan
        response = planner_llm.invoke([planning_prompt])
        
        # Parse the plan
        plan_text = response.content
        plan_lines = [line.strip() for line in plan_text.split("\n") if line.strip()]
        plan = [line for line in plan_lines if any(c.isdigit() for c in line[:2])]
        
        return {
            "messages": messages,
            "plan": plan,
            "current_step": 0,
            "reasoning": "",
            "results": {},
            "next": ReasoningAction.REASONER.value
        }
    
    def reasoner_node(state: ReasoningState) -> ReasoningState:
        """Reasoner node in the workflow."""
        messages = state["messages"]
        plan = state["plan"]
        current_step = state["current_step"]
        
        if current_step >= len(plan):
            return {
                "messages": messages,
                "plan": plan,
                "current_step": current_step,
                "reasoning": state["reasoning"],
                "results": state["results"],
                "next": ReasoningAction.SYNTHESIZER.value
            }
        
        current_task = plan[current_step]
        
        # Create a reasoning prompt
        reasoning_prompt = HumanMessage(
            content=f"""I need to complete this task: {current_task}
            
            Think step by step about how to approach this. What information do I need?
            What tools might be helpful? What's the best way to solve this?
            """
        )
        
        # Get the reasoning
        response = reasoner_llm.invoke([reasoning_prompt])
        
        # Update the reasoning
        reasoning = state["reasoning"] + f"\nStep {current_step + 1}: {current_task}\n{response.content}\n"
        
        return {
            "messages": messages,
            "plan": plan,
            "current_step": current_step,
            "reasoning": reasoning,
            "results": state["results"],
            "next": ReasoningAction.EXECUTOR.value
        }
    
    def executor_node(state: ReasoningState) -> ReasoningState:
        """Executor node in the workflow."""
        messages = state["messages"]
        plan = state["plan"]
        current_step = state["current_step"]
        reasoning = state["reasoning"]
        results = state["results"] or {}
        
        current_task = plan[current_step]
        
        # Create an execution prompt
        execution_prompt = HumanMessage(
            content=f"""I need to execute this task: {current_task}
            
            My reasoning so far:
            {reasoning}
            
            Based on this reasoning, determine if I need to use any tools to complete this task.
            If yes, specify which tool to use and what input to provide.
            If no, provide the direct answer or solution.
            """
        )
        
        # Get the execution plan
        response = executor_llm.invoke([execution_prompt])
        execution_plan = response.content
        
        # Check if we need to use a tool
        if any(tool.name in execution_plan for tool in tools):
            # Extract the tool name and input
            for tool in tools:
                if tool.name in execution_plan:
                    # Simple extraction logic - this could be improved
                    tool_name = tool.name
                    tool_input_start = execution_plan.find(tool_name) + len(tool_name)
                    tool_input_text = execution_plan[tool_input_start:].strip()
                    
                    try:
                        # Try to parse as JSON
                        import json
                        tool_input = json.loads(tool_input_text)
                    except:
                        # Fallback to simple key-value parsing
                        tool_input = {}
                        for line in tool_input_text.split("\n"):
                            if ":" in line:
                                key, value = line.split(":", 1)
                                tool_input[key.strip()] = value.strip()
                    
                    # Execute the tool
                    tool_result = tool_executor.invoke({
                        "tool": tool_name,
                        "tool_input": tool_input
                    })
                    
                    # Store the result
                    results[f"step_{current_step + 1}"] = {
                        "task": current_task,
                        "tool": tool_name,
                        "input": tool_input,
                        "result": tool_result
                    }
                    break
        else:
            # No tool needed, store the direct answer
            results[f"step_{current_step + 1}"] = {
                "task": current_task,
                "result": execution_plan
            }
        
        # Move to the next step
        next_step = current_step + 1
        next_action = ReasoningAction.REASONER.value if next_step < len(plan) else ReasoningAction.SYNTHESIZER.value
        
        return {
            "messages": messages,
            "plan": plan,
            "current_step": next_step,
            "reasoning": reasoning,
            "results": results,
            "next": next_action
        }
    
    def synthesizer_node(state: ReasoningState) -> ReasoningState:
        """Synthesizer node in the workflow."""
        messages = state["messages"]
        plan = state["plan"]
        reasoning = state["reasoning"]
        results = state["results"]
        
        # Create a synthesis prompt
        results_text = "\n".join([
            f"Step {step_num}: {step_data['task']}\nResult: {step_data['result']}"
            for step_num, step_data in sorted(results.items())
        ])
        
        synthesis_prompt = HumanMessage(
            content=f"""I have completed all the steps in my plan:
            
            {plan}
            
            Here are the results for each step:
            
            {results_text}
            
            Please synthesize these results into a comprehensive answer to the original request:
            {messages[-1].content}
            """
        )
        
        # Get the synthesis
        response = synthesizer_llm.invoke([synthesis_prompt])
        
        # Create the final response
        final_response = AIMessage(content=response.content)
        
        return {
            "messages": messages + [final_response],
            "plan": plan,
            "current_step": len(plan),
            "reasoning": reasoning,
            "results": results,
            "next": ReasoningAction.END.value
        }
    
    # Add nodes to the workflow
    workflow.add_node(ReasoningAction.PLANNER.value, planner_node)
    workflow.add_node(ReasoningAction.REASONER.value, reasoner_node)
    workflow.add_node(ReasoningAction.EXECUTOR.value, executor_node)
    workflow.add_node(ReasoningAction.SYNTHESIZER.value, synthesizer_node)
    
    # Add conditional edges
    workflow.add_conditional_edges(
        ReasoningAction.PLANNER.value,
        lambda state: state["next"]
    )
    
    workflow.add_conditional_edges(
        ReasoningAction.REASONER.value,
        lambda state: state["next"]
    )
    
    workflow.add_conditional_edges(
        ReasoningAction.EXECUTOR.value,
        lambda state: state["next"]
    )
    
    workflow.add_conditional_edges(
        ReasoningAction.SYNTHESIZER.value,
        lambda state: state["next"]
    )
    
    # Add the end edge
    workflow.add_edge(ReasoningAction.END.value, END)
    
    # Set the entry point
    workflow.set_entry_point(ReasoningAction.PLANNER.value)
    
    return workflow.compile()

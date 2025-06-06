"""
Module for LangChain callbacks in NetGuardian.
"""
from typing import Dict, List, Any, Optional
from langchain.callbacks.base import BaseCallbackHandler
import wandb
import time

from config.logging_config import get_logger

logger = get_logger("langchain_callbacks")

class WandbCallbackHandler(BaseCallbackHandler):
    """Callback handler for logging to Weights & Biases."""
    
    def __init__(self, run_name: str = None):
        """Initialize the callback handler."""
        super().__init__()
        self.run_name = run_name or "netguardian-run"
        self.steps = []
        self.current_step = {}
        
    def on_llm_start(self, serialized: Dict[str, Any], prompts: List[str], **kwargs: Any) -> None:
        """Log when LLM starts."""
        self.current_step = {
            "type": "llm",
            "name": serialized.get("name", "Unknown LLM"),
            "prompts": prompts,
            "start_time": time.time()
        }
        
    def on_llm_end(self, response, **kwargs: Any) -> None:
        """Log when LLM ends."""
        if self.current_step.get("type") == "llm":
            self.current_step["response"] = response.generations
            self.current_step["end_time"] = time.time()
            self.steps.append(self.current_step)
            self.current_step = {}
            
            if wandb.run:
                wandb.log({
                    "llm_calls": len([s for s in self.steps if s.get("type") == "llm"])
                })
                
    def on_chain_start(self, serialized: Dict[str, Any], inputs: Dict[str, Any], **kwargs: Any) -> None:
        """Log when chain starts."""
        self.current_step = {
            "type": "chain",
            "name": serialized.get("name", "Unknown Chain"),
            "inputs": inputs,
            "start_time": time.time()
        }
        
    def on_chain_end(self, outputs: Dict[str, Any], **kwargs: Any) -> None:
        """Log when chain ends."""
        if self.current_step.get("type") == "chain":
            self.current_step["outputs"] = outputs
            self.current_step["end_time"] = time.time()
            self.steps.append(self.current_step)
            self.current_step = {}
            
            if wandb.run:
                wandb.log({
                    "chain_calls": len([s for s in self.steps if s.get("type") == "chain"])
                })
                
    def on_tool_start(self, serialized: Dict[str, Any], input_str: str, **kwargs: Any) -> None:
        """Log when tool starts."""
        self.current_step = {
            "type": "tool",
            "name": serialized.get("name", "Unknown Tool"),
            "input": input_str,
            "start_time": time.time()
        }
        
    def on_tool_end(self, output: str, **kwargs: Any) -> None:
        """Log when tool ends."""
        if self.current_step.get("type") == "tool":
            self.current_step["output"] = output
            self.current_step["end_time"] = time.time()
            self.steps.append(self.current_step)
            self.current_step = {}
            
            if wandb.run:
                wandb.log({
                    "tool_calls": len([s for s in self.steps if s.get("type") == "tool"])
                })
                
    def flush(self) -> None:
        """Flush the logs."""
        if wandb.run:
            wandb.log({
                "total_steps": len(self.steps),
                "llm_calls": len([s for s in self.steps if s.get("type") == "llm"]),
                "chain_calls": len([s for s in self.steps if s.get("type") == "chain"]),
                "tool_calls": len([s for s in self.steps if s.get("type") == "tool"])
            })

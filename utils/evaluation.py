"""
Evaluation utilities for NetGuardian.
"""
from typing import Dict, List, Any, Optional
import time
import json
import os
from pathlib import Path

from config.logging_config import get_logger

logger = get_logger("evaluation")

class EvaluationMetrics:
    """
    Class for tracking and computing evaluation metrics.
    """
    
    def __init__(self):
        """Initialize the evaluation metrics."""
        self.metrics = {
            "response_times": [],
            "query_counts": {},
            "tool_usage": {},
            "error_counts": 0,
            "user_feedback": []
        }
        
        # Create metrics directory if it doesn't exist
        self.metrics_dir = Path("./data/logs/metrics")
        self.metrics_dir.mkdir(parents=True, exist_ok=True)
    
    def log_response_time(self, response_time: float) -> None:
        """
        Log a response time.
        
        Args:
            response_time: Response time in seconds
        """
        self.metrics["response_times"].append(response_time)
    
    def log_query(self, query_type: str) -> None:
        """
        Log a query.
        
        Args:
            query_type: Type of query
        """
        self.metrics["query_counts"][query_type] = self.metrics["query_counts"].get(query_type, 0) + 1
    
    def log_tool_usage(self, tool_name: str) -> None:
        """
        Log tool usage.
        
        Args:
            tool_name: Name of the tool
        """
        self.metrics["tool_usage"][tool_name] = self.metrics["tool_usage"].get(tool_name, 0) + 1
    
    def log_error(self) -> None:
        """Log an error."""
        self.metrics["error_counts"] += 1
    
    def log_user_feedback(self, feedback: Dict[str, Any]) -> None:
        """
        Log user feedback.
        
        Args:
            feedback: User feedback
        """
        self.metrics["user_feedback"].append(feedback)
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """
        Get a summary of all metrics.
        
        Returns:
            Dictionary containing metrics summary
        """
        return {
            "total_queries": sum(self.metrics["query_counts"].values()),
            "average_response_time": sum(self.metrics["response_times"]) / len(self.metrics["response_times"]) if self.metrics["response_times"] else 0,
            "error_rate": self.metrics["error_counts"] / max(1, sum(self.metrics["query_counts"].values())),
            "tool_usage": self.metrics["tool_usage"],
            "feedback_count": len(self.metrics["user_feedback"])
        }

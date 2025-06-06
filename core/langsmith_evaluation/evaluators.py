"""
Module for LangSmith evaluators in NetGuardian.
"""
from typing import Dict, List, Any, Optional, Callable
from langsmith import Client
from langsmith.evaluation import RunEvaluator, EvaluationResult

from config.langsmith_config import LANGCHAIN_API_KEY
from config.logging_config import get_logger

logger = get_logger("langsmith_evaluators")

class CorrectnessCriterion(RunEvaluator):
    """Evaluator for correctness criterion."""
    
    def __init__(self, reference_key: str = "reference"):
        self.reference_key = reference_key
        self.client = Client(api_key=LANGCHAIN_API_KEY)
        
    def evaluate_run(self, run, example=None) -> EvaluationResult:
        """Evaluate the run for correctness."""
        # Get the reference answer
        reference = None
        if example and self.reference_key in example.outputs:
            reference = example.outputs[self.reference_key]
        
        # Get the prediction
        prediction = run.outputs.get("output")
        if not prediction:
            return EvaluationResult(
                key="correctness",
                score=0.0,
                comment="No prediction found"
            )
            
        if not reference:
            return EvaluationResult(
                key="correctness",
                score=None,
                comment="No reference found for comparison"
            )
            
        # Use LangSmith's built-in correctness evaluator
        eval_result = self.client.evaluate_run(
            run,
            evaluator="correctness",
            reference_key=self.reference_key,
            input_key="input"
        )
        
        return EvaluationResult(
            key="correctness",
            score=eval_result.score,
            comment=eval_result.comment
        )

class RelevanceCriterion(RunEvaluator):
    """Evaluator for relevance criterion."""
    
    def __init__(self):
        self.client = Client(api_key=LANGCHAIN_API_KEY)
        
    def evaluate_run(self, run, example=None) -> EvaluationResult:
        """Evaluate the run for relevance."""
        # Get the input and prediction
        input_text = run.inputs.get("input")
        prediction = run.outputs.get("output")
        
        if not input_text or not prediction:
            return EvaluationResult(
                key="relevance",
                score=0.0,
                comment="Missing input or prediction"
            )
            
        # Use LangSmith's built-in relevance evaluator
        eval_result = self.client.evaluate_run(
            run,
            evaluator="relevance"
        )
        
        return EvaluationResult(
            key="relevance",
            score=eval_result.score,
            comment=eval_result.comment
        )

class SecurityAccuracyCriterion(RunEvaluator):
    """Evaluator for security accuracy criterion."""
    
    def __init__(self):
        self.client = Client(api_key=LANGCHAIN_API_KEY)
        
    def evaluate_run(self, run, example=None) -> EvaluationResult:
        """Evaluate the run for security accuracy."""
        # Get the input and prediction
        input_text = run.inputs.get("input")
        prediction = run.outputs.get("output")
        
        if not input_text or not prediction:
            return EvaluationResult(
                key="security_accuracy",
                score=0.0,
                comment="Missing input or prediction"
            )
            
        # Use a custom prompt to evaluate security accuracy
        prompt = f"""
        Evaluate the accuracy of the following security-related response.
        
        User query: {input_text}
        
        AI response: {prediction}
        
        Rate the security accuracy on a scale from 0 to 1, where:
        - 0: Completely inaccurate, contains dangerous or incorrect security advice
        - 0.5: Partially accurate, but has some issues or omissions
        - 1: Highly accurate, provides correct and comprehensive security advice
        
        Provide your rating as a number between 0 and 1, followed by a brief explanation.
        """
        
        # Use LangSmith's custom evaluator
        eval_result = self.client.evaluate_run(
            run,
            evaluator="custom_prompt",
            custom_prompt=prompt
        )
        
        return EvaluationResult(
            key="security_accuracy",
            score=eval_result.score,
            comment=eval_result.comment
        )

def get_default_evaluators() -> List[RunEvaluator]:
    """Get the default set of evaluators."""
    return [
        CorrectnessCriterion(),
        RelevanceCriterion(),
        SecurityAccuracyCriterion()
    ]

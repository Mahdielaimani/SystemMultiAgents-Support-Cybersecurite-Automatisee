"""
Configuration for LangSmith integration in NetGuardian.
"""
import os
from dotenv import load_dotenv

load_dotenv()

# LangSmith configuration
LANGCHAIN_TRACING_V2 = os.getenv("LANGCHAIN_TRACING_V2", "true").lower() == "true"
LANGCHAIN_ENDPOINT = os.getenv("LANGCHAIN_ENDPOINT", "https://api.smith.langchain.com")
LANGCHAIN_API_KEY = os.getenv("LANGCHAIN_API_KEY", "")
LANGCHAIN_PROJECT = os.getenv("LANGCHAIN_PROJECT", "netguardian")

def configure_langsmith():
    """Configure LangSmith for tracing and evaluation."""
    os.environ["LANGCHAIN_TRACING_V2"] = str(LANGCHAIN_TRACING_V2).lower()
    os.environ["LANGCHAIN_ENDPOINT"] = LANGCHAIN_ENDPOINT
    os.environ["LANGCHAIN_API_KEY"] = LANGCHAIN_API_KEY
    os.environ["LANGCHAIN_PROJECT"] = LANGCHAIN_PROJECT
    
    if not LANGCHAIN_API_KEY and LANGCHAIN_TRACING_V2:
        print("Warning: LANGCHAIN_API_KEY not set. LangSmith tracing will not work.")
        os.environ["LANGCHAIN_TRACING_V2"] = "false"

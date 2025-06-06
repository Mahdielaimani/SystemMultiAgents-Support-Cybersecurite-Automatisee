from setuptools import setup, find_packages

setup(
    name="netguardian",
    version="0.1.0",
    description="Système avancé d'agents IA pour la cybersécurité",
    author="NetGuardian Team",
    author_email="contact@netguardian.ai",
    packages=find_packages(),
    install_requires=[
        "python-dotenv>=1.0.0",
        "pydantic>=2.0.0",
        "fastapi>=0.100.0",
        "uvicorn>=0.22.0",
        "langchain>=0.1.0",
        "langgraph>=0.0.20",
        "langsmith>=0.0.60",
        "chromadb>=0.4.6",
        "neo4j>=5.8.1",
        "openai>=1.3.0",
        "anthropic>=0.5.0",
        "mistralai>=0.0.7",
    ],
    python_requires=">=3.9",
    entry_points={
        "console_scripts": [
            "netguardian=main:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Information Technology",
        "Topic :: Security",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)

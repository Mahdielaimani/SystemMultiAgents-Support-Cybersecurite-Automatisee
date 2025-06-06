"""
Module de génération de réponses pour l'agent de support.
"""
from typing import Dict, List, Optional, Any, Union

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from config.logging_config import get_logger

logger = get_logger("support_generation")

def generate_response(context: Dict[str, Any], llm: BaseChatModel, system_prompt: str) -> str:
    """
    Génère une réponse en fonction du contexte.
    
    Args:
        context: Contexte pour la génération
        llm: Modèle de langage
        system_prompt: Prompt système
        
    Returns:
        Réponse générée
    """
    query = context["query"]
    conversation_history = context.get("conversation_history", [])
    retrieved_documents = context.get("retrieved_documents", [])
    relevant_entities = context.get("relevant_entities", [])
    
    # Construire le contexte documentaire
    document_context = ""
    if retrieved_documents:
        document_context = "\n\n".join([doc.page_content for doc in retrieved_documents])
    
    # Construire le contexte des entités
    entity_context = ""
    if relevant_entities:
        entity_context = "Entités pertinentes:\n" + "\n".join([
            f"- {entity['name']} (Type: {entity['type']})" 
            for entity in relevant_entities
        ])
    
    # Construire l'historique de conversation
    conversation_context = ""
    if conversation_history:
        # Prendre les 5 derniers messages
        recent_history = conversation_history[-5:]
        conversation_context = "\n".join([
            f"{msg['role'].upper()}: {msg['content']}" 
            for msg in recent_history
        ])
    
    # Construire le prompt complet
    prompt_template = f"""
    Contexte de la conversation:
    {conversation_context}
    
    Documents pertinents:
    {document_context}
    
    {entity_context}
    
    Question de l'utilisateur: {query}
    
    Réponds à la question de l'utilisateur en te basant sur le contexte fourni.
    Si tu ne trouves pas l'information dans le contexte, dis-le clairement et suggère des ressources alternatives.
    """
    
    # Générer la réponse
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=prompt_template)
    ]
    
    try:
        response = llm.invoke(messages)
        return response.content
    except Exception as e:
        logger.error(f"Erreur lors de la génération de la réponse: {e}")
        return "Je suis désolé, mais j'ai rencontré une erreur lors de la génération de la réponse. Veuillez réessayer."

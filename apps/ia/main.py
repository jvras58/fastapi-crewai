"""IA module for CrewAI agents and LangChain integration."""

from apps.ia.agents.conversation_agent import ConversationAgent
from apps.ia.services.rag_service import RAGService

__all__ = ['ConversationAgent', 'RAGService']

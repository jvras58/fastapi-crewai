"""AI clients integration module."""

from apps.ia.agents.conversation_agent import ConversationAgent, SimpleConversationAgent
from apps.ia.services.rag_service import RAGService

# Instância global do serviço RAG
_global_rag_service = None
_global_conversation_agent = None


def get_rag_service() -> RAGService:
    """Get global RAG service instance."""
    global _global_rag_service
    if _global_rag_service is None:
        _global_rag_service = RAGService()
    return _global_rag_service


def get_conversation_agent() -> ConversationAgent:
    """Get global conversation agent instance."""
    global _global_conversation_agent
    if _global_conversation_agent is None:
        rag_service = get_rag_service()
        _global_conversation_agent = ConversationAgent(rag_service)
    return _global_conversation_agent


def get_simple_agent() -> SimpleConversationAgent:
    """Get simple conversation agent for basic interactions."""
    return SimpleConversationAgent()

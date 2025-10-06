"""AI clients integration module."""

from apps.ia.agents.conversation_agent import ConversationAgent

_global_conversation_agent = None

def get_conversation_agent() -> ConversationAgent:
    """Get global conversation agent instance with RagTool integration."""
    global _global_conversation_agent
    if _global_conversation_agent is None:
        _global_conversation_agent = ConversationAgent()
    return _global_conversation_agent

def get_simple_agent() -> ConversationAgent:
    """Get simple conversation agent for basic interactions."""
    return get_conversation_agent()

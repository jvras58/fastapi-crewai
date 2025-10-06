"""RAG client module - separated to avoid circular imports."""

from crewai_tools import RagTool

_global_rag_tool = None

def get_rag_tool():
    """Get global RagTool instance."""
    global _global_rag_tool
    if _global_rag_tool is None:
        # FIXME: Configurações reais do RagTool devem ser feitas aqui.
        # Aparentemente precisamos de chaves para o embeddings.
        _global_rag_tool = RagTool()
    return _global_rag_tool

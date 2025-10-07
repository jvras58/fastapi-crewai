"""RAG client module - separated to avoid circular imports."""

from crewai_tools import RagTool

_global_rag_tool = None

config = {
    "embedding_model": {
        "provider": "google-generativeai",
        "config": {
            "model": "models/gemini-embedding-001",
            "task_type": "retrieval_document",
        },
    }
}


def get_rag_tool():
    """Get global RagTool instance."""
    global _global_rag_tool
    if _global_rag_tool is None:
        _global_rag_tool = RagTool(config=config)
    return _global_rag_tool

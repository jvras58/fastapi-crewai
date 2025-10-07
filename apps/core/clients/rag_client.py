"""RAG client module - separated to avoid circular imports."""

from crewai_tools import RagTool

_global_rag_tool = None


# FIXME: DENTRO DO DEVCONTAINER APARENTIMENTE ESTÁ GUARDANDO UM CACHE RUIM
# An embedding function already exists in the collection configuration, and a new one is
# provided. If this is intentional, please embed documents separately.
# Embedding function conflict: new: google_generative_ai vs persisted:
#  openai [type=value_error,
# input_value={'collection_name': 'rag_...logservice_port=50052))}, input_type=dict]
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

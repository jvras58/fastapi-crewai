"""RAG Search Tool for CrewAI agents."""

from crewai.tools import tool

from apps.core.clients.rag_client import get_rag_tool


@tool('rag_search')
def rag_search_tool(query: str) -> str:
    """
    Busca na base de conhecimento usando RAGTool diretamente.
    Args:
        query (str): Consulta.
    Returns:
        str: Contexto relevante.
    """
    rag_tool = get_rag_tool()
    return rag_tool.run(query)

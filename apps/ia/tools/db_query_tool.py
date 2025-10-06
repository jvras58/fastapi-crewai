"""DB Query Tool for CrewAI agents."""

from crewai.tools import tool

from apps.core.clients.ai_clients import get_rag_tool
from apps.packpage.settings import get_settings


@tool('db_query')
def db_query_tool(query: str) -> str:
    """
    Consulta PostgreSQL e adiciona ao RagTool diretamente.
    Args:
        query (str): SQL query.
    Returns:
        str: Resultados com contexto RAG.
    """
    rag_tool = get_rag_tool()
    rag_tool.add(data_type="postgres", config=get_settings().DB_URL)

    return rag_tool.run(f"Results for query: {query}")

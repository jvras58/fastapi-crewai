from crewai.tools import tool

from apps.ia.services.rag_service import RAGService


@tool('Enriquecer CSV')
def enrich_csv_tool(csv_path: str) -> str:
    """Processa e enriquece CSV com IA, persistindo dados."""
    rag_service = RAGService()
    rag_service.enrich_and_load_data(csv_path)
    return f'CSV {csv_path} enriquecido e carregado com sucesso.'

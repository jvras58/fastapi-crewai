"""RAG Search Tool for CrewAI agents."""

from crewai.tools import tool

from apps.ia.services.rag_service import RAGService


def rag_search_function(query: str) -> str:
    """
    Função base para buscar informações na base de conhecimento.
    Fornece contexto relevante baseado em similaridade semântica.

    Args:
        query (str): A consulta para buscar na base de conhecimento

    Returns:
        str: Contexto relevante encontrado na base de conhecimento
    """
    try:
        # Criar instância do RAG service
        rag_service = RAGService()

        # Buscar documentos relevantes
        docs = rag_service.similarity_search(query, k=3)

        if not docs:
            return 'Nenhuma informação relevante encontrada na base de conhecimento.'

        # Formatar o contexto encontrado
        context_parts = []
        for i, doc in enumerate(docs, 1):
            source = doc.metadata.get('source', 'Desconhecido')
            content = doc.page_content.strip()
            context_parts.append(f'Fonte {i} ({source}):\n{content}')

        return '\n\n'.join(context_parts)

    except Exception as e:
        return f'Erro ao buscar na base de conhecimento: {str(e)}'


@tool('rag_search')
def rag_search_tool(query: str) -> str:
    """
    Use esta ferramenta para buscar informações na base de conhecimento.
    Fornece contexto relevante baseado em similaridade semântica.

    Args:
        query (str): A consulta para buscar na base de conhecimento

    Returns:
        str: Contexto relevante encontrado na base de conhecimento
    """
    return rag_search_function(query)


class RAGSearchTool:
    """Tool wrapper for searching the RAG knowledge base."""

    def __init__(self, rag_service: RAGService):
        """Initialize the RAG search tool."""
        self.rag_service = rag_service
        self.name = 'rag_search'
        self.description = """
        Use esta ferramenta para buscar informações na base de conhecimento.
        Fornece contexto relevante baseado em similaridade semântica.
        Input: query (string) - A consulta para buscar na base de conhecimento
        Output: Contexto relevante encontrado na base de conhecimento
        """

    def search(self, query: str) -> str:
        """Execute the RAG search."""
        try:
            # Buscar documentos relevantes
            docs = self.rag_service.similarity_search(query, k=3)

            if not docs:
                return (
                    'Nenhuma informação relevante encontrada na '
                    'base de conhecimento.'
                )

            # Formatar o contexto encontrado
            context_parts = []
            for i, doc in enumerate(docs, 1):
                source = doc.metadata.get('source', 'Desconhecido')
                content = doc.page_content.strip()
                context_parts.append(f'Fonte {i} ({source}):\n{content}')

            return '\n\n'.join(context_parts)

        except Exception as e:
            return f'Erro ao buscar na base de conhecimento: {str(e)}'

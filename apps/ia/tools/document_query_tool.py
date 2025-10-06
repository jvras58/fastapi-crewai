"""Document Query Tool for CrewAI agents."""

from crewai.tools import tool
from sqlalchemy.orm import Session

from apps.core.clients.ai_clients import get_rag_tool
from apps.core.database.session import get_session
from apps.ia.models.document import Document


@tool('document_query')
def document_query_tool(search_term: str = '', status: str = 'active') -> str:
    """
    Busca documentos e adiciona ao RagTool como JSON ou text.
    Args:
        search_term (str): Termo de busca.
        status (str): Status do documento.
    Returns:
        str: Resultados com contexto RAG.
    """
    session: Session = next(get_session())
    query = session.query(Document).filter(Document.str_status == status)
    if search_term:
        query = query.filter(
            (Document.str_title.ilike(f"%{search_term}%"))
            | (Document.txt_content.ilike(f"%{search_term}%"))
        )
    documents = query.limit(10).all()

    rag_tool = get_rag_tool()
    for doc in documents:
        rag_tool.add(doc.txt_content, data_type="text")

    if not documents:
        return "Nenhum documento encontrado."

    return rag_tool.run(search_term)

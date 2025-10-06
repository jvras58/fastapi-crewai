"""Document Query Tool for CrewAI agents."""

from crewai.tools import tool
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from apps.ia.models.document import Document
from apps.packpage.settings import get_settings


@tool('document_query')
def document_query_tool(search_term: str = '', status: str = 'active') -> str:
    """
    Busca documentos na base de conhecimento.

    Args:
        search_term (str): Termo para buscar no título ou conteúdo
        status (str): Status do documento (active, processed, deleted)

    Returns:
        str: Lista de documentos encontrados
    """
    settings = get_settings()
    engine = create_engine(settings.DB_URL)
    Session = sessionmaker(bind=engine)

    try:
        with Session() as session:
            query = session.query(Document).filter(
                Document.str_status == status
            )

            if search_term:
                query = query.filter(
                    (Document.str_title.ilike(f'%{search_term}%'))
                    | (Document.txt_content.ilike(f'%{search_term}%'))
                )

            documents = query.limit(10).all()

            if not documents:
                return 'Nenhum documento encontrado.'

            result = []
            for doc in documents:
                result.append(
                    f'ID: {doc.id}\n'
                    f'Título: {doc.str_title}\n'
                    f'Conteúdo (preview): {doc.txt_content[:200]}...\n'
                    f'Status: {doc.str_status}\n'
                    f'Uploaded: {doc.dt_uploaded_at}\n'
                    f'---'
                )

            return '\n\n'.join(result)

    except Exception as e:
        return f'Erro ao buscar documentos: {str(e)}'
    finally:
        engine.dispose()


@tool('document_content')
def document_content_tool(document_id: int) -> str:
    """
    Obtém o conteúdo completo de um documento específico.

    Args:
        document_id (int): ID do documento

    Returns:
        str: Conteúdo completo do documento
    """
    settings = get_settings()
    engine = create_engine(settings.DB_URL)
    Session = sessionmaker(bind=engine)

    try:
        with Session() as session:
            document = (
                session.query(Document)
                .filter(
                    Document.id == document_id, Document.str_status == 'active'
                )
                .first()
            )

            if not document:
                return f'Documento com ID {document_id} não encontrado.'

            return (
                f'Título: {document.str_title}\n'
                f"Filename: {document.str_filename or 'N/A'}\n"
                f"Content Type: {document.str_content_type or 'N/A'}\n"
                f'Uploaded: {document.dt_uploaded_at}\n'
                f'Size: {document.int_size_bytes or 0} bytes\n\n'
                f'Conteúdo:\n{document.txt_content}'
            )

    except Exception as e:
        return f'Erro ao obter documento: {str(e)}'
    finally:
        engine.dispose()

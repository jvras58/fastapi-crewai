"""Router for chat and conversation endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from apps.core.api.authentication.controller import get_current_user
from apps.core.database.session import get_session
from apps.core.models.user import User
from apps.ia.api.documents.controller import DocController
from apps.ia.api.documents.schemas import (
    DocumentListSchema,
    DocumentSchema,
    DocumentUploadSchema,
)
from apps.packpage.client_ip import get_client_ip

router = APIRouter()
doc_controller = DocController()

# Dependency types
DbSession = Annotated[Session, Depends(get_session)]
CurrentUser = Annotated[User, Depends(get_current_user)]

@router.post('/documents', response_model=DocumentSchema)
async def upload_document(
    request: Request,
    document_data: DocumentUploadSchema,
    session: DbSession,
    current_user: CurrentUser,
):
    """Upload a document to the knowledge base."""
    client_ip = get_client_ip(request)

    try:
        document = doc_controller.upload_document(
            session, document_data, current_user, client_ip
        )
        return document
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='Erro ao fazer upload do documento',
        ) from e


@router.get('/documents', response_model=DocumentListSchema)
async def list_documents(
    session: DbSession,
    current_user: CurrentUser,
    page: int = 1,
    per_page: int = 20,
    status: str = None,  # Filter by status
    title: str = None,  # Filter by title (uses ilike)
    content_type: str = None,  # Filter by content type
):
    """List documents in knowledge base with optional filters."""
    if per_page > 100:
        per_page = 100

    # Build dynamic filters
    filters = {}
    if status:
        filters["str_status"] = status
    if title:
        filters["str_title"] = title
    if content_type:
        filters["str_content_type"] = content_type

    result = doc_controller.get_documents(session, page, per_page, **filters)
    return result


@router.get("/documents/{document_id}", response_model=DocumentSchema)
async def get_document(
    document_id: int,
    session: DbSession,
    current_user: CurrentUser,
):
    """Get a specific document by ID."""
    try:
        document = doc_controller.get_document_by_id(session, document_id)
        return document
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Documento não encontrado",
        ) from e


@router.delete("/documents/{document_id}")
async def delete_document(
    document_id: int,
    session: DbSession,
    current_user: CurrentUser,
):
    """Delete a document from the knowledge base."""
    try:
        doc_controller.delete_document(session, document_id)
        return {"message": "Documento deletado com sucesso"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Documento não encontrado",
        ) from e


@router.patch("/documents/{document_id}/status")
async def update_document_status(
    document_id: int,
    status: str,
    session: DbSession,
    current_user: CurrentUser,
):
    """Update document status."""
    if status not in ["active", "processed", "deleted"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Status deve ser: active, processed ou deleted",
        )

    try:
        document = doc_controller.update_document_status(session, document_id, status)
        return document
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Documento não encontrado",
        ) from e


@router.get('/search')
async def search_knowledge_base(q: str, current_user: CurrentUser, k: int = 5):
    """Search the knowledge base using RAG."""
    if k > 20:
        k = 20

    try:
        results = doc_controller.search_knowledge_base(q, k)
        return {'query': q, 'results': results, 'count': len(results)}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='Erro na busca',
        ) from e


@router.get("/documents/search/content")
async def search_documents_content(
    q: str,
    session: DbSession,
    current_user: CurrentUser,
    limit: int = 10,
):
    """Search documents by content in database."""
    if limit > 50:
        limit = 50

    try:
        documents = doc_controller.search_documents_by_content(session, q, limit)
        return {"query": q, "documents": documents, "count": len(documents)}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro na busca de documentos",
        ) from e

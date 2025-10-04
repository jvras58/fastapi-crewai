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
):
    """List documents in knowledge base."""
    if per_page > 100:
        per_page = 100

    result = doc_controller.get_documents(session, page, per_page)
    return result


@router.get('/search')
async def search_knowledge_base(q: str, current_user: CurrentUser, k: int = 5):
    """Search the knowledge base."""
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

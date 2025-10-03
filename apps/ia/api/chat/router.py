"""Router for chat and conversation endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from apps.core.api.authentication.controller import get_current_user
from apps.core.database.session import get_session
from apps.core.models.user import User
from apps.ia.api.chat.controller import ChatController
from apps.ia.api.chat.schemas import (
    ChatMessageSchema,
    ChatResponseSchema,
    ConversationCreateSchema,
    ConversationListSchema,
    ConversationSchema,
    ConversationUpdateSchema,
    ConversationWithMessagesSchema,
    DocumentListSchema,
    DocumentSchema,
    DocumentUploadSchema,
)
from apps.packpage.client_ip import get_client_ip

router = APIRouter()

# Dependency types
DbSession = Annotated[Session, Depends(get_session)]
CurrentUser = Annotated[User, Depends(get_current_user)]


@router.post('/chat', response_model=ChatResponseSchema)
async def send_chat_message(
    request: Request,
    chat_data: ChatMessageSchema,
    session: DbSession,
    current_user: CurrentUser,
):
    """Send a chat message and get AI response."""
    controller = ChatController()
    client_ip = get_client_ip(request)

    try:
        return controller.send_message(
            session, chat_data, current_user, client_ip
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='Erro interno do servidor',
        ) from e


@router.post('/conversations', response_model=ConversationSchema)
async def create_conversation(
    request: Request,
    conversation_data: ConversationCreateSchema,
    session: DbSession,
    current_user: CurrentUser,
):
    """Create a new conversation."""
    controller = ChatController()
    client_ip = get_client_ip(request)

    conversation = controller.create_conversation(
        session, conversation_data, current_user, client_ip
    )
    return conversation


@router.get('/conversations', response_model=ConversationListSchema)
async def list_conversations(
    session: DbSession,
    current_user: CurrentUser,
    page: int = 1,
    per_page: int = 20,
):
    """List user conversations."""
    controller = ChatController()

    if per_page > 100:
        per_page = 100

    result = controller.get_user_conversations(
        session, current_user.id, page, per_page
    )
    return result


@router.get(
    '/conversations/{conversation_id}',
    response_model=ConversationWithMessagesSchema,
)
async def get_conversation(
    conversation_id: int, session: DbSession, current_user: CurrentUser
):
    """Get conversation with messages."""
    controller = ChatController()

    conversation = controller.get_conversation_with_messages(
        session, conversation_id, current_user.id
    )

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Conversa não encontrada',
        )

    return conversation


@router.put(
    '/conversations/{conversation_id}', response_model=ConversationSchema
)
async def update_conversation(
    request: Request,
    conversation_id: int,
    conversation_data: ConversationUpdateSchema,
    session: DbSession,
    current_user: CurrentUser,
):
    """Update a conversation."""
    controller = ChatController()
    client_ip = get_client_ip(request)

    conversation = controller.update_conversation(
        session, conversation_id, conversation_data, current_user, client_ip
    )

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Conversa não encontrada',
        )

    return conversation


@router.post('/documents', response_model=DocumentSchema)
async def upload_document(
    request: Request,
    document_data: DocumentUploadSchema,
    session: DbSession,
    current_user: CurrentUser,
):
    """Upload a document to the knowledge base."""
    controller = ChatController()
    client_ip = get_client_ip(request)

    try:
        document = controller.upload_document(
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
    controller = ChatController()

    if per_page > 100:
        per_page = 100

    result = controller.get_documents(session, page, per_page)
    return result


@router.get('/search')
async def search_knowledge_base(q: str, current_user: CurrentUser, k: int = 5):
    """Search the knowledge base."""
    controller = ChatController()

    if k > 20:
        k = 20

    try:
        results = controller.search_knowledge_base(q, k)
        return {'query': q, 'results': results, 'count': len(results)}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='Erro na busca',
        ) from e

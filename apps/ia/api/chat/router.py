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
)
from apps.packpage.client_ip import get_client_ip

router = APIRouter()

DbSession = Annotated[Session, Depends(get_session)]
CurrentUser = Annotated[User, Depends(get_current_user)]
ChatControllerDep = Annotated[
    ChatController, Depends(lambda: ChatController())
]

# TODO: implements Validations and Permissions com o (validate_transaction_access)
@router.post('/chat', response_model=ChatResponseSchema)
async def send_chat_message(
    request: Request,
    chat_data: ChatMessageSchema,
    session: DbSession,
    current_user: CurrentUser,
    chat_controller: ChatControllerDep,
):
    """Send a chat message and get AI response."""
    client_ip = get_client_ip(request)

    try:
        return chat_controller.send_message(
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
    chat_controller: ChatControllerDep,
):
    """Create a new conversation."""
    client_ip = get_client_ip(request)

    conversation = chat_controller.create_conversation(
        session, conversation_data, current_user, client_ip
    )
    return conversation


@router.get('/conversations', response_model=ConversationListSchema)
async def list_conversations(
    session: DbSession,
    current_user: CurrentUser,
    chat_controller: ChatControllerDep,
    page: int = 1,
    per_page: int = 20,
):
    """List user conversations."""
    if per_page > 100:
        per_page = 100

    result = chat_controller.get_user_conversations(
        session, current_user.id, page, per_page
    )
    return result


@router.get(
    '/conversations/{conversation_id}',
    response_model=ConversationWithMessagesSchema,
)
async def get_conversation(
    conversation_id: int,
    session: DbSession,
    current_user: CurrentUser,
    chat_controller: ChatControllerDep,
):
    """Get conversation with messages."""
    conversation = chat_controller.get_conversation_with_messages(
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
    chat_controller: ChatControllerDep,
):
    """Update a conversation."""
    client_ip = get_client_ip(request)

    conversation = chat_controller.update_conversation(
        session, conversation_id, conversation_data, current_user, client_ip
    )

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Conversa não encontrada',
        )

    return conversation

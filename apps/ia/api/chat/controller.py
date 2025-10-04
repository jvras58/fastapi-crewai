"""Controller for chat and conversation management."""

from datetime import UTC, datetime
from typing import Any

from sqlalchemy import and_
from sqlalchemy.orm import Session

from apps.core.models.user import User
from apps.ia.agents.conversation_agent import ConversationAgent
from apps.ia.api.chat.schemas import (
    ChatMessageSchema,
    ChatResponseSchema,
    ConversationCreateSchema,
    ConversationUpdateSchema,
)
from apps.ia.models.conversation import Conversation
from apps.ia.models.message import Message
from apps.ia.services.rag_service import RAGService
from apps.packpage.generic_controller import GenericController


class ChatController(GenericController):
    """Controller for chat operations."""

    def __init__(self, conversation_agent: ConversationAgent | None = None) -> None:
        """Initialize chat controller."""
        super().__init__(Conversation)
        if conversation_agent is None:
            rag_service = RAGService()
            conversation_agent = ConversationAgent(rag_service)
        self.conversation_agent = conversation_agent

    def save(self, db_session: Session, obj: Conversation) -> Conversation:
        """Save a new conversation with additional processing."""
        # Definir valores padrão se não fornecidos
        if not obj.str_status:
            obj.str_status = "active"

        saved_conversation = super().save(db_session, obj)

        # Lógica adicional específica de conversas pode ser adicionada aqui
        # Por exemplo: notificações, logs, etc.

        return saved_conversation

    def update(self, db_session: Session, obj: Conversation) -> Conversation:
        """Update an existing conversation with additional processing."""
        # Lógica específica antes da atualização
        # Por exemplo: validações específicas, auditoria adicional, etc.

        # Usar o método update do GenericController
        updated_conversation = super().update(db_session, obj)

        # Lógica adicional após a atualização pode ser adicionada aqui

        return updated_conversation

    def get_user_conversation(
        self, session: Session, conversation_id: int, user_id: int
    ) -> Conversation | None:
        """Get a specific conversation for a user."""
        try:
            conversation = self.get(session, conversation_id)
            if conversation.user_id != user_id or conversation.str_status == "deleted":
                return None
            return conversation
        except Exception:
            return None

    def send_message(
        self,
        session: Session,
        chat_data: ChatMessageSchema,
        current_user: User,
        request_ip: str,
    ) -> ChatResponseSchema:
        """Send a chat message and get AI response."""

        # Encontrar ou criar conversa
        if chat_data.conversation_id:
            conversation = self.get_user_conversation(
                session, chat_data.conversation_id, current_user.id
            )

            if not conversation or conversation.str_status != "active":
                raise ValueError(
                    'Conversa não encontrada ou não pertence ao usuário'
                )
        else:
            # Criar nova conversa
            conversation = self._create_new_conversation(
                session, current_user, request_ip, chat_data.message
            )

        # Salvar mensagem do usuário
        user_message = self._save_user_message(
            session, conversation, chat_data.message, current_user, request_ip
        )

        # Obter resposta da IA
        ai_response = self.conversation_agent.chat(
            chat_data.message, chat_data.context or ''
        )

        # Salvar mensagem da IA
        ai_message = self._save_ai_message(
            session, conversation, ai_response, current_user, request_ip
        )

        # Atualizar timestamp da última mensagem
        conversation.dt_last_message_at = datetime.now(UTC)
        session.commit()

        return ChatResponseSchema(
            response=ai_response,
            conversation_id=conversation.id,
            message_id=ai_message.id,
            user_message_id=user_message.id,
        )

    def _create_new_conversation(
        self, session: Session, user: User, request_ip: str, first_message: str
    ) -> Conversation:
        """Create a new conversation."""
        # Gerar título baseado na primeira mensagem
        title = self._generate_conversation_title(first_message)

        conversation = Conversation(
            str_title=title,
            str_description='Conversa iniciada automaticamente',
            user_id=user.id,
            str_status='active',
            audit_user_ip=request_ip,
            audit_user_login=user.username,
        )

        session.add(conversation)
        session.flush()  # Para obter o ID
        return conversation

    def _generate_conversation_title(self, message: str) -> str:
        """Generate a conversation title from the first message."""
        # Pegar primeiras palavras da mensagem
        words = message.split()[:8]
        title = ' '.join(words)

        # Limitar tamanho
        if len(title) > 50:
            title = title[:47] + '...'

        return title or 'Nova Conversa'

    def _save_user_message(
        self,
        session: Session,
        conversation: Conversation,
        content: str,
        user: User,
        request_ip: str,
    ) -> Message:
        """Save user message to database."""
        message = Message(
            txt_content=content,
            str_role='user',
            conversation_id=conversation.id,
            str_status='active',
            audit_user_ip=request_ip,
            audit_user_login=user.username,
        )

        session.add(message)
        session.flush()
        return message

    def _save_ai_message(
        self,
        session: Session,
        conversation: Conversation,
        content: str,
        user: User,
        request_ip: str,
    ) -> Message:
        """Save AI response message to database."""
        message = Message(
            txt_content=content,
            str_role='assistant',
            conversation_id=conversation.id,
            str_status='active',
            audit_user_ip=request_ip,
            audit_user_login=user.username,
        )

        session.add(message)
        session.flush()
        return message

    def create_conversation(
        self,
        session: Session,
        conversation_data: ConversationCreateSchema,
        current_user: User,
        request_ip: str,
    ) -> Conversation:
        """Create a new conversation."""
        conversation = Conversation(
            str_title=conversation_data.title,
            str_description=conversation_data.description,
            user_id=current_user.id,
            str_status='active',
            audit_user_ip=request_ip,
            audit_user_login=current_user.username,
        )

        return self.save(session, conversation)

    def get_user_conversations(
        self, session: Session, user_id: int, page: int = 1, per_page: int = 20
    ) -> dict[str, Any]:
        """Get user conversations with pagination."""
        query = (
            session.query(Conversation)
            .filter(
                and_(
                    Conversation.user_id == user_id,
                    Conversation.str_status.in_(['active', 'archived']),
                )
            )
            .order_by(Conversation.dt_last_message_at.desc())
        )

        total = query.count()
        conversations = (
            query.offset((page - 1) * per_page).limit(per_page).all()
        )

        return {
            'conversations': conversations,
            'total': total,
            'page': page,
            'per_page': per_page,
        }

    def get_conversation_with_messages(
        self, session: Session, conversation_id: int, user_id: int
    ) -> Conversation | None:
        """Get conversation with messages."""
        return self.get_user_conversation(session, conversation_id, user_id)

    def update_conversation(
        self,
        session: Session,
        conversation_id: int,
        conversation_data: ConversationUpdateSchema,
        current_user: User,
        request_ip: str,
    ) -> Conversation | None:
        """Update a conversation."""
        try:
            conversation = self.get(session, conversation_id)

            # Verificar se a conversa pertence ao usuário
            if conversation.user_id != current_user.id:
                return None

            # Atualizar campos se fornecidos
            if conversation_data.title is not None:
                conversation.str_title = conversation_data.title
            if conversation_data.description is not None:
                conversation.str_description = conversation_data.description
            if conversation_data.status is not None:
                conversation.str_status = conversation_data.status

            # Atualizar auditoria
            conversation.audit_user_ip = request_ip
            conversation.audit_user_login = current_user.username

            return self.update(session, conversation)
        except Exception:
            return None

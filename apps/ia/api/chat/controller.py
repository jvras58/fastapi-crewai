"""Controller for chat and conversation management."""

import hashlib
import json
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import and_
from sqlalchemy.orm import Session

from apps.core.models.user import User
from apps.core.utils.generic_controller import GenericController
from apps.ia.agents.conversation_agent import ConversationAgent
from apps.ia.api.chat.schemas import (
    ChatMessageSchema,
    ChatResponseSchema,
    ConversationCreateSchema,
    ConversationUpdateSchema,
    DocumentUploadSchema,
)
from apps.ia.models.conversation import Conversation
from apps.ia.models.document import Document
from apps.ia.models.message import Message
from apps.ia.services.rag_service import RAGService


class ChatController(GenericController):
    """Controller for chat operations."""

    def __init__(self):
        """Initialize chat controller."""
        super().__init__(Conversation)
        self.rag_service = RAGService()
        self.conversation_agent = ConversationAgent(self.rag_service)

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
            conversation = (
                session.query(Conversation)
                .filter(
                    and_(
                        Conversation.id == chat_data.conversation_id,
                        Conversation.user_id == current_user.id,
                        Conversation.str_status == 'active',
                    )
                )
                .first()
            )

            if not conversation:
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

        session.add(conversation)
        session.commit()
        return conversation

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
        return (
            session.query(Conversation)
            .filter(
                and_(
                    Conversation.id == conversation_id,
                    Conversation.user_id == user_id,
                    Conversation.str_status != 'deleted',
                )
            )
            .first()
        )

    def update_conversation(
        self,
        session: Session,
        conversation_id: int,
        conversation_data: ConversationUpdateSchema,
        current_user: User,
        request_ip: str,
    ) -> Conversation | None:
        """Update a conversation."""
        conversation = (
            session.query(Conversation)
            .filter(
                and_(
                    Conversation.id == conversation_id,
                    Conversation.user_id == current_user.id,
                )
            )
            .first()
        )

        if not conversation:
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

        session.commit()
        return conversation

    def upload_document(
        self,
        session: Session,
        document_data: DocumentUploadSchema,
        current_user: User,
        request_ip: str,
    ) -> Document:
        """Upload document to knowledge base."""

        # Calcular hash do conteúdo
        content_hash = hashlib.sha256(
            document_data.content.encode('utf-8')
        ).hexdigest()

        # Verificar se documento já existe
        existing_doc = (
            session.query(Document)
            .filter(Document.str_content_hash == content_hash)
            .first()
        )

        if existing_doc:
            raise ValueError('Documento com este conteúdo já existe')

        # Criar documento
        document = Document(
            str_title=document_data.title,
            str_filename=document_data.filename,
            txt_content=document_data.content,
            str_content_type=document_data.content_type,
            json_metadata=(
                json.dumps(document_data.metadata)
                if document_data.metadata
                else None
            ),
            int_size_bytes=len(document_data.content.encode('utf-8')),
            str_content_hash=content_hash,
            str_status='active',
            audit_user_ip=request_ip,
            audit_user_login=current_user.username,
        )

        session.add(document)
        session.commit()

        # Adicionar ao RAG
        metadata = document_data.metadata or {}
        metadata.update(
            {
                'doc_id': document.id,
                'title': document.str_title,
                'source': f'document_{document.id}',
            }
        )

        self.rag_service.add_document_from_text(
            document_data.content, metadata
        )

        # Marcar como processado
        document.dt_processed_at = datetime.now(UTC)
        session.commit()

        return document

    def get_documents(
        self, session: Session, page: int = 1, per_page: int = 20
    ) -> dict[str, Any]:
        """Get documents with pagination."""
        query = (
            session.query(Document)
            .filter(Document.str_status == 'active')
            .order_by(Document.dt_uploaded_at.desc())
        )

        total = query.count()
        documents = query.offset((page - 1) * per_page).limit(per_page).all()

        return {
            'documents': documents,
            'total': total,
            'page': page,
            'per_page': per_page,
        }

    def search_knowledge_base(
        self, query: str, k: int = 5
    ) -> list[dict[str, Any]]:
        """Search the knowledge base."""
        docs = self.rag_service.similarity_search(query, k=k)

        results = []
        for doc in docs:
            results.append(
                {
                    'content': doc.page_content,
                    'metadata': doc.metadata,
                    'source': doc.metadata.get('source', 'unknown'),
                }
            )

        return results

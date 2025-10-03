"""Message model for storing individual messages in conversations."""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from apps.packpage.base_model import AbstractBaseModel

if TYPE_CHECKING:
    from apps.ia.models.conversation import Conversation


class Message(AbstractBaseModel):
    """Model for storing individual messages in conversations."""

    __tablename__ = 'ia_messages'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, name='id')

    # Conteúdo da mensagem
    txt_content: Mapped[str] = mapped_column(
        Text, nullable=False, name='txt_content'
    )

    # Tipo da mensagem (user, assistant, system)
    str_role: Mapped[str] = mapped_column(
        String(20), nullable=False, name='str_role'
    )

    # Relacionamento com conversa
    conversation_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey('ia_conversations.id'),
        nullable=False,
        name='conversation_id',
    )

    # Timestamp da mensagem
    dt_created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text('CURRENT_TIMESTAMP'),
        name='dt_created_at',
    )

    # Metadados opcionais
    json_metadata: Mapped[str | None] = mapped_column(
        Text, nullable=True, name='json_metadata'
    )

    # Status da mensagem
    str_status: Mapped[str] = mapped_column(
        String(20),
        server_default=text("'active'"),
        name='str_status',  # active, edited, deleted
    )

    # Relacionamentos
    conversation: Mapped['Conversation'] = relationship(
        'Conversation', back_populates='messages', lazy='subquery'
    )

    def __repr__(self) -> str:
        """String representation of message."""
        content_preview = (
            self.txt_content[:50] + '...'
            if len(self.txt_content) > 50
            else self.txt_content
        )
        return (
            f"<Message(id={self.id}, role='{self.str_role}', "
            f"content='{content_preview}')>"
        )

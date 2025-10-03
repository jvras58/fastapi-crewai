"""Conversation model for storing chat conversations."""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from apps.core.utils.base_model import AbstractBaseModel

if TYPE_CHECKING:
    from apps.core.models.user import User
    from apps.ia.models.message import Message


class Conversation(AbstractBaseModel):
    """Model for storing chat conversations."""

    __tablename__ = 'ia_conversations'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, name='id')
    str_title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        name='str_title'
    )
    str_description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        name='str_description'
    )

    # Relacionamento com usuário
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey('users.id'),
        nullable=False,
        name='user_id'
    )

    # Timestamps específicos da conversa
    dt_started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text('CURRENT_TIMESTAMP'),
        name='dt_started_at'
    )
    dt_last_message_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        name='dt_last_message_at'
    )

    # Status da conversa
    str_status: Mapped[str] = mapped_column(
        String(20),
        server_default=text("'active'"),
        name='str_status'  # active, archived, deleted
    )

    # Relacionamentos
    user: Mapped["User"] = relationship(
        "User",
        back_populates="conversations"
    )
    messages: Mapped[list["Message"]] = relationship(
        "Message",
        back_populates="conversation",
        cascade="all, delete-orphan",
        order_by="Message.dt_created_at"
    )

    def __repr__(self) -> str:
        """String representation of conversation."""
        return f"<Conversation(id={self.id}, title='{self.str_title}')>"

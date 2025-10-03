"""Document model for storing knowledge base documents."""

from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text, text
from sqlalchemy.orm import Mapped, mapped_column

from apps.core.utils.base_model import AbstractBaseModel


class Document(AbstractBaseModel):
    """Model for storing documents in the knowledge base."""

    __tablename__ = 'ia_documents'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, name='id')

    # Informações do documento
    str_title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        name='str_title'
    )

    str_filename: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        name='str_filename'
    )

    # Conteúdo
    txt_content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        name='txt_content'
    )

    # Metadados
    str_content_type: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        name='str_content_type'
    )

    json_metadata: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        name='json_metadata'
    )

    # Status e controle
    str_status: Mapped[str] = mapped_column(
        String(20),
        server_default=text("'active'"),
        name='str_status'  # active, processed, deleted
    )

    dt_uploaded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text('CURRENT_TIMESTAMP'),
        name='dt_uploaded_at'
    )

    dt_processed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        name='dt_processed_at'
    )

    # Tamanho e hash para controle
    int_size_bytes: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        name='int_size_bytes'
    )

    str_content_hash: Mapped[str | None] = mapped_column(
        String(64),
        nullable=True,
        name='str_content_hash'
    )

    def __repr__(self) -> str:
        """String representation of document."""
        return f"<Document(id={self.id}, title='{self.str_title}')>"

"""Schemas for chat API endpoints."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from apps.core.utils.base_schemas import BaseAuditModelSchema


# Schemas para mensagens
class MessageCreateSchema(BaseModel):
    """Schema for creating a new message."""

    content: str = Field(..., min_length=1, max_length=10000)
    role: str = Field(..., pattern=r'^(user|assistant|system)$')
    metadata: dict[str, Any] | None = None


class MessageSchema(BaseAuditModelSchema):
    """Schema for message response."""

    id: int
    content: str
    role: str
    conversation_id: int
    created_at: datetime
    metadata: dict[str, Any] | None = None
    status: str


# Schemas para conversas
class ConversationCreateSchema(BaseModel):
    """Schema for creating a new conversation."""

    title: str = Field(..., min_length=1, max_length=255)
    description: str | None = Field(None, max_length=1000)


class ConversationUpdateSchema(BaseModel):
    """Schema for updating a conversation."""

    title: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = Field(None, max_length=1000)
    status: str | None = Field(None, pattern=r'^(active|archived|deleted)$')


class ConversationSchema(BaseAuditModelSchema):
    """Schema for conversation response."""

    id: int
    title: str
    description: str | None
    user_id: int
    started_at: datetime
    last_message_at: datetime | None
    status: str
    message_count: int | None = None


class ConversationWithMessagesSchema(ConversationSchema):
    """Schema for conversation with messages included."""

    messages: list[MessageSchema] = []


# Schemas para chat
class ChatMessageSchema(BaseModel):
    """Schema for sending a chat message."""

    message: str = Field(..., min_length=1, max_length=10000)
    conversation_id: int | None = None
    context: str | None = Field(None, max_length=5000)


class ChatResponseSchema(BaseModel):
    """Schema for chat response."""

    response: str
    conversation_id: int
    message_id: int
    user_message_id: int


# Schemas para documentos da base de conhecimento
class DocumentUploadSchema(BaseModel):
    """Schema for uploading a document to knowledge base."""

    title: str = Field(..., min_length=1, max_length=255)
    content: str = Field(..., min_length=1)
    content_type: str | None = Field(None, max_length=100)
    filename: str | None = Field(None, max_length=255)
    metadata: dict[str, Any] | None = None


class DocumentSchema(BaseAuditModelSchema):
    """Schema for document response."""

    id: int
    title: str
    filename: str | None
    content_type: str | None
    uploaded_at: datetime
    processed_at: datetime | None
    status: str
    size_bytes: int | None
    content_hash: str | None


# Schemas de lista
class ConversationListSchema(BaseModel):
    """Schema for conversation list response."""

    conversations: list[ConversationSchema]
    total: int
    page: int
    per_page: int


class DocumentListSchema(BaseModel):
    """Schema for document list response."""

    documents: list[DocumentSchema]
    total: int
    page: int
    per_page: int

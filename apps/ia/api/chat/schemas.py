"""Schemas for chat API endpoints."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from apps.packpage.base_schemas import BaseAuditModelSchema


class MessageCreateSchema(BaseModel):
    """Schema for creating a new message."""

    content: str = Field(..., min_length=1, max_length=10000)
    role: str = Field(..., pattern=r'^(user|assistant|system)$')
    metadata: dict[str, Any] | None = None


class MessageSchema(BaseAuditModelSchema):
    """Schema for message response."""

    id: int
    txt_content: str
    str_role: str
    conversation_id: int
    dt_created_at: datetime
    json_metadata: dict[str, Any] | None = None
    str_status: str


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
    str_title: str
    str_description: str | None
    user_id: int
    dt_started_at: datetime
    dt_last_message_at: datetime | None
    str_status: str
    message_count: int | None = None


class ConversationWithMessagesSchema(ConversationSchema):
    """Schema for conversation with messages included."""

    messages: list[MessageSchema] = []


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


class ConversationListSchema(BaseModel):
    """Schema for conversation list response."""

    conversations: list[ConversationSchema]
    total: int
    page: int
    per_page: int

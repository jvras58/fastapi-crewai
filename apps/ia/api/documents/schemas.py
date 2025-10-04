"""Schemas for chat API endpoints."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from apps.packpage.base_schemas import BaseAuditModelSchema


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


class DocumentListSchema(BaseModel):
    """Schema for document list response."""

    documents: list[DocumentSchema]
    total: int
    page: int
    per_page: int

"""Schemas for chat API endpoints."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from apps.packpage.base_schemas import BaseAuditModelSchema


class DocumentUploadSchema(BaseModel):
    """Schema for uploading a document to knowledge base."""

    str_title: str = Field(..., min_length=1, max_length=255)
    txt_content: str = Field(..., min_length=1)
    str_content_type: str | None = Field(None, max_length=100)
    str_filename: str | None = Field(None, max_length=255)
    json_metadata: dict[str, Any] | None = None


class DocumentSchema(BaseAuditModelSchema):
    """Schema for document response."""

    id: int
    str_title: str
    str_filename: str | None
    txt_content: str
    str_content_type: str | None
    json_metadata: str | None
    str_status: str
    dt_uploaded_at: datetime
    dt_processed_at: datetime | None
    int_size_bytes: int | None
    str_content_hash: str | None


class DocumentListSchema(BaseModel):
    """Schema for document list response."""

    documents: list[DocumentSchema]
    total: int
    page: int
    per_page: int

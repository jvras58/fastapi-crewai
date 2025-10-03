"""Schemas for text processing API requests and responses."""
from pydantic import BaseModel, Field


class TextProcessRequest(BaseModel):
    """Request schema for text processing."""

    input_text: str = Field(
        description='Texto a ser processado pela IA',
        min_length=1,
        max_length=5000,
        examples=['Este é um exemplo de texto que precisa ser melhorado.'],
    )


class TextProcessResponse(BaseModel):
    """Response schema for text processing."""

    processed_result: str = Field(
        description='Resultado do processamento de texto pela IA'
    )

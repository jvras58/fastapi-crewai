from pydantic import BaseModel, Field


class TextProcessRequest(BaseModel):
    input_text: str = Field(
        ...,
        description='Texto a ser processado pela IA',
        min_length=1,
        max_length=5000,
        example='Este é um exemplo de texto que precisa ser melhorado.',
    )


class TextProcessResponse(BaseModel):
    processed_result: str = Field(
        ..., description='Resultado do processamento de texto pela IA'
    )

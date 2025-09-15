from pydantic import BaseModel


class DataProcessRequest(BaseModel):
    input_text: str


class DataProcessResponse(BaseModel):
    processed_result: str

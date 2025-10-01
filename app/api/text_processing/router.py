"""Router for text processing with AI."""
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.api.authentication.controller import get_current_user
from app.api.authorization.controller import validate_transaction_access
from app.api.text_processing.controller import TextProcessingController
from app.api.text_processing.schemas import (
    TextProcessRequest,
    TextProcessResponse,
)
from app.api.transaction.enum_operation_code import EnumOperationCode as op
from app.database.session import get_session
from app.models.user import User
from app.utils.client_ip import get_client_ip

router = APIRouter()
text_processing_controller = TextProcessingController()

DbSession = Annotated[Session, Depends(get_session)]
CurrentUser = Annotated[User, Depends(get_current_user)]


@router.post(
    '/process-text',
    response_model=TextProcessResponse,
    status_code=status.HTTP_201_CREATED,
    summary='Processar texto com IA',
    description='Processa e melhora texto usando inteligência artificial',
)
def process_text(
    request: TextProcessRequest,
    db_session: DbSession,
    current_user: CurrentUser,
    http_request: Request,
):
    """Processes and enhances text using AI, saving the result."""
    validate_transaction_access(db_session, current_user, op.OP_2000001.value)
    try:
        result = text_processing_controller.process_text_and_persist(
            db_session,
            request.input_text,
            current_user,
            get_client_ip(http_request),
        )
        if result.processed_result is None:
            raise HTTPException(
                status_code=500,
                detail="Falha no processamento do texto - resultado vazio",
            )

        return TextProcessResponse(processed_result=result.processed_result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e

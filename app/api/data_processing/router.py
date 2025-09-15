from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.api.authentication.controller import get_current_user
from app.api.authorization.controller import validate_transaction_access
from app.api.data_processing.controller import DataProcessingController
from app.api.data_processing.schemas import (
    DataProcessRequest,
    DataProcessResponse,
)
from app.api.transaction.enum_operation_code import EnumOperationCode as op
from app.database.session import get_session
from app.models.user import User

router = APIRouter()
data_processing_controller = DataProcessingController()

DbSession = Annotated[Session, Depends(get_session)]
CurrentUser = Annotated[User, Depends(get_current_user)]


@router.post(
    '/process',
    response_model=DataProcessResponse,
    status_code=status.HTTP_201_CREATED,
)
def process_data(
    request: DataProcessRequest,
    db_session: DbSession,
    current_user: CurrentUser,
    http_request: Request,
):
    validate_transaction_access(db_session, current_user, op.OP_2000001.value)
    try:
        result = data_processing_controller.process_and_persist(
            db_session,
            request.input_text,
            current_user,
            http_request.client.host,
        )
        return DataProcessResponse(processed_result=result.processed_result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e

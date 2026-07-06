from typing import Any

from fastapi import status as http_status
from pydantic import BaseModel

from app.core.message import ErrorMessage, SuccessMessage


# Error Message Format
class ErrorMessageResponse(BaseModel):
    status: int | None = http_status.HTTP_500_INTERNAL_SERVER_ERROR
    msg: str | None = ErrorMessage.INTERNAL_SERVER_ERROR
    data: Any | None = None


# Success Message Format
class SuccessMessageResponse(BaseModel):
    status: int | None = http_status.HTTP_200_OK
    msg: str | None = SuccessMessage.RESPONSE_FETCHED_SUCCESSFULLY
    data: Any | None = {}

from app.schema.response import ErrorMessageResponse, SuccessMessageResponse
from typing import Optional, Any
from fastapi.responses import JSONResponse
from app.core.message import ErrorMessage
from fastapi import status as http_status


# success_response
def success_response(
    status_code: Optional[int] = http_status.HTTP_200_OK,
    msg: Optional[str] = None,
    data: Optional[Any] = None,
):
    message = SuccessMessageResponse(status=status_code, msg=msg, data=data)

    return JSONResponse(status_code=status_code, content=message.model_dump())


# error_response
def error_response(
    status_code: Optional[int] = http_status.HTTP_500_INTERNAL_SERVER_ERROR,
    msg: Optional[str] = ErrorMessage.INTERNAL_SERVER_ERROR,
    data: Optional[Any] = None,
):
    message = ErrorMessageResponse(status=status_code, msg=msg, data=data)

    return JSONResponse(status_code=status_code, content=message.model_dump())

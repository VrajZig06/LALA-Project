from app.schema.response import ErrorMessageResponse, SuccessMessageResponse
from typing import Optional, Any
from fastapi.responses import JSONResponse


# success_response
def success_response(
    status_code: Optional[int] = 200,
    msg: Optional[str] = None,
    data: Optional[Any] = None,
):
    message = SuccessMessageResponse(status=status_code, msg=msg, data=data)

    return JSONResponse(status_code=status_code, content=message.model_dump())


# error_response
def error_response(
    status_code: Optional[int] = None,
    msg: Optional[str] = None,
    data: Optional[Any] = None,
):
    message = ErrorMessageResponse(status=status_code, msg=msg, data=data)

    return JSONResponse(status_code=status_code, content=message.model_dump())

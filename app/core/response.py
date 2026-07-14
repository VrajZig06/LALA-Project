from typing import Any

from fastapi import status as http_status
from fastapi.responses import JSONResponse

from app.core.message import ErrorMessage
from app.schema.response import ErrorMessageResponse, SuccessMessageResponse


# success_response
def success_response(
    status_code: int | None = http_status.HTTP_200_OK,
    msg: str | None = None,
    data: Any | None = None,
):
    message = SuccessMessageResponse(status=status_code, msg=msg, data=data)

    return JSONResponse(status_code=status_code, content=message.model_dump())


# error_response
def error_response(
    status_code: int | None = http_status.HTTP_500_INTERNAL_SERVER_ERROR,
    msg: str | None = ErrorMessage.INTERNAL_SERVER_ERROR,
    data: Any | None = None,
):
    message = ErrorMessageResponse(status=status_code, msg=msg, data=data)

    return JSONResponse(status_code=status_code, content=message.model_dump())

# pagination_response
def pagination_response(
    data: Any,
    message: str,
    total_pages: int,
    total_items: int,
    current_page: int,
    page_size: int,
) -> dict[str, Any]:
    """Pagination response payload."""

    # Create Pagination Payload
    pagination_payload = {
        "data": data,
        "total_pages": total_pages,
        "total_items": total_items,
        "current_page": current_page,
        "page_size": page_size
    }

    message = SuccessMessageResponse(status=http_status.HTTP_200_OK, msg=message, data=pagination_payload)
    return JSONResponse(status_code=http_status.HTTP_200_OK, content=message.model_dump())
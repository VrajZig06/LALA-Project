from fastapi import HTTPException, Request

from app.core.exception import ServerException
from app.core.logger import get_logger
from app.core.response import error_response

logger = get_logger(__name__)


# HttpException Handler
async def http_exception_handler(request: Request, exc: HTTPException):
    return error_response(status_code=exc.status_code, msg=exc.detail)


# ServerError Handler
async def server_exception_handler(request: Request, exc: ServerException):
    logger.error(exc.message, exc_info=True)

    return error_response(status_code=exc.status_code, msg=exc.message)

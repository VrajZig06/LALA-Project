from fastapi import Request, HTTPException
from app.core.response import error_response


# HttpException Handler
async def http_exception_handler(request: Request, exc: HTTPException):
    return error_response(status_code=exc.status_code, msg=exc.detail)

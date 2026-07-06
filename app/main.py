from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse

from app.api.routes import app_router
from app.common.utils import generate_otp
from app.core.config import get_settings
from app.core.exception import ServerException
from app.core.exception_handler import http_exception_handler, server_exception_handler
from app.core.jwt import generate_token
from app.core.logger import get_logger
from app.core.message import SuccessMessage
from app.core.response import success_response


# GET Settings Object
settings = get_settings()

# Set Up Logger
logger = get_logger(__name__)


# Lifespan Function
@asynccontextmanager
async def lifespan(app: FastAPI):
    # App Start
    logger.info(f"{settings.APP_NAME} Started...")

    yield

    # App Close
    logger.info(f"{settings.APP_NAME} Shut Down...")


# FastAPI Server
app = FastAPI(lifespan=lifespan)

# Handle Exception
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(ServerException, server_exception_handler)

# Add App Routes
app.include_router(app_router, prefix="/api/v1")


# Health API
@app.get("/health")
async def health_check():
    print(f"generate_otp :: {generate_otp()}")
    print(
        f"generate_token :: {generate_token({'user_id': '123', 'email': 'user@gmail.com'}, expiry_time_in_min=1)}"
    )
    return success_response(msg=SuccessMessage.SERVER_HEALTHY)


# Serve Google Signup/Login Page
@app.get("/", response_class=HTMLResponse)
async def serve_login_page():
    try:
        with open("static/google_signup.html", "r") as f:
            html_content = f.read()
        return HTMLResponse(content=html_content)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Frontend file not found")


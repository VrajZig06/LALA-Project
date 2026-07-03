from fastapi import FastAPI, HTTPException
from app.core.exception import ServerException
from app.core.config import get_settings
from app.core.logger import get_logger
from contextlib import asynccontextmanager
from app.core.response import success_response
from app.core.exception_handler import http_exception_handler, server_exception_handler
from app.db import models
from app.core.message import SuccessMessage
from app.api.routes import app_router

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
    return success_response(msg=SuccessMessage.SERVER_HEALTHY)

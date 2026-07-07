from fastapi import Query
from app.schema.user import RefreshTokenRequestData
from fastapi import APIRouter, BackgroundTasks, Depends, Request
from sqlalchemy.orm import Session

from app.core.dependecy import current_user
from app.core.logger import get_logger
from app.core.message import LoggerMessage
from app.db.session import get_db
from app.schema.user import (
    ResetPassword,
    UserForgotPassword,
    UserGoogleAuth,
    UserLogin,
    UserOtpVerify,
    UserRegistration,
    ValidateUserForgotPassword,
)
from app.services.user_service import UserService

logger = get_logger(__name__)

router = APIRouter(prefix="/users", tags=["Authentication"])


@router.post("/signup", summary="Register a new user")
async def signup(
    payload: UserRegistration, request: Request, db: Session = Depends(get_db)
):
    """
    Register a new user in the system.
    Sends a verification email with a 4-digit OTP.
    """
    logger.info(LoggerMessage.API_SIGNUP_ATTEMPT.format(email=payload.email))
    user_service = UserService(request, db)
    response = await user_service.register_user(payload)
    logger.info(LoggerMessage.API_SIGNUP_COMPLETED.format(email=payload.email))
    return response


@router.post("/user-login", summary="Login with email and password")
async def email_login(
    payload: UserLogin, request: Request, db: Session = Depends(get_db)
):
    """
    Authenticate a user using their email and password.
    Returns access and refresh tokens upon successful authentication.
    """
    logger.info(LoggerMessage.API_LOGIN_ATTEMPT.format(email=payload.email))
    user_service = UserService(request, db)
    response = await user_service.user_login(payload)
    logger.info(LoggerMessage.API_LOGIN_SUCCESS.format(email=payload.email))
    return response


@router.post("/verify-otp", summary="Verify user OTP")
async def verify_otp(
    payload: UserOtpVerify, request: Request, db: Session = Depends(get_db)
):
    """
    Verify the 4-digit OTP code sent to the user's email during signup/verification.
    """
    logger.info(LoggerMessage.API_VERIFY_OTP_ATTEMPT.format(user_id=payload.user_id))
    user_service = UserService(request, db)
    response = await user_service.verify_otp(payload)
    logger.info(LoggerMessage.API_VERIFY_OTP_SUCCESS.format(user_id=payload.user_id))
    return response


@router.post("/reset-password", summary="Reset password (authenticated)")
async def reset_password(
    payload: ResetPassword,
    request: Request,
    current_user=Depends(current_user),
    db: Session = Depends(get_db),
):
    """
    Reset user password. User must be authenticated and provide the old and new passwords.
    """
    user_id = current_user.get("id") if current_user else "unknown"
    logger.info(LoggerMessage.API_RESET_PASSWORD_REQUEST.format(user_id=user_id))
    user_service = UserService(request, db)
    response = await user_service.reset_password(payload, current_user)
    logger.info(LoggerMessage.API_RESET_PASSWORD_SUCCESS.format(user_id=user_id))
    return response


@router.post("/google-auth", summary="Google SSO Authentication")
async def google_auth(
    payload: UserGoogleAuth, request: Request, db: Session = Depends(get_db)
):
    """
    Authenticate/Sign up a user via Google OAuth Identity token.
    """
    logger.info(LoggerMessage.API_GOOGLE_AUTH_REQUEST)
    user_service = UserService(request, db)
    response = await user_service.google_auth(payload)
    logger.info(LoggerMessage.API_GOOGLE_AUTH_SUCCESS)
    return response


@router.post("/forgot-password", summary="Request forgot password reset link")
async def forgot_password(
    payload: UserForgotPassword,
    request: Request,
    background_task: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """
    Initiate password recovery. Generates a signed reset link and sends it via email service.
    """
    logger.info(LoggerMessage.API_FORGOT_PASSWORD_REQUEST.format(email=payload.email))
    user_service = UserService(request, db)
    response = await user_service.forgot_password(payload, background_task)
    logger.info(LoggerMessage.API_FORGOT_PASSWORD_COMPLETED.format(email=payload.email))
    return response


@router.post("/validate-password", summary="Validate password reset and update password")
async def validate_forgot_password(
    payload: ValidateUserForgotPassword,
    request: Request,
    db: Session = Depends(get_db),
):
    """
    Validate recovery token and update user's password to the new password.
    """
    logger.info(LoggerMessage.API_VALIDATE_PASSWORD_REQUEST)
    user_service = UserService(request, db)
    response = await user_service.validate_forgot_password(payload)
    logger.info(LoggerMessage.API_VALIDATE_PASSWORD_SUCCESS)
    return response

@router.get("/refresh-token" ,summary="Get Access Token from Refresh Token")
async def refresh_token(
    request: Request,
    token: str =  Query(),
    db: Session = Depends(get_db)
):
    """
    Validate Refresh Token and Generate New Access Token and Refresh Token
    """
    logger.info(LoggerMessage.API_REFRESH_TOKEN_REQUEST)
    user_service = UserService(request, db)
    response = await user_service.refresh_token(token)
    logger.info(LoggerMessage.API_REFRESH_TOKEN_SUCCESS)
    return response
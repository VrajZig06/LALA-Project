from app.schema.user import UserLogin
from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schema.user import UserOtpVerify, UserRegistration, ResetPassword
from app.services.user_service import UserService
from app.core.dependecy import current_user

router = APIRouter(prefix="/users")


@router.post("/signup")
async def get_users(
    payload: UserRegistration, request: Request, db: Session = Depends(get_db)
):
    user_service = UserService(request, db)
    return await user_service.register_user(payload)

@router.post("/user-login")
async def email_login(
    payload: UserLogin, request: Request, db: Session = Depends(get_db)
):
    user_service = UserService(request, db)
    return await user_service.user_login(payload)

@router.post("/verify-otp")
async def verify_otp(
    payload: UserOtpVerify, request: Request, db: Session = Depends(get_db)
):
    user_service = UserService(request, db)
    return await user_service.verify_otp(payload)

@router.post("/reset-password")
async def reset_password(
    payload: ResetPassword, request: Request, current_user = Depends(current_user), db: Session = Depends(get_db)
):
    user_service = UserService(request, db)
    return await user_service.reset_password(payload, current_user)


from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schema.user import UserOtpVerify, UserRegistration
from app.services.user_service import UserService

router = APIRouter(prefix="/users")


@router.post("/signup")
async def get_users(
    payload: UserRegistration, request: Request, db: Session = Depends(get_db)
):
    user_service = UserService(request, db)
    return await user_service.register_user(payload)


@router.post("/verify-otp")
async def verify_otp(
    payload: UserOtpVerify, request: Request, db: Session = Depends(get_db)
):
    user_service = UserService(request, db)
    return await user_service.verify_otp(payload)

from fastapi import APIRouter, Request, Depends
from sqlalchemy.orm import Session
from app.core.response import success_response
from app.db.session import get_db
from app.services.user_service import UserService
from app.core.dependecy import current_user
from app.schema.user import UserRegistration

router = APIRouter(prefix="/users")


@router.post("/signup")
async def get_users(payload: UserRegistration, request: Request, db: Session = Depends(get_db)):
    user_service = UserService(request, db)
    return await user_service.register_user(payload)
    

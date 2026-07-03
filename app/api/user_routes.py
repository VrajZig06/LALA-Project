from fastapi import APIRouter, Request, Depends
from sqlalchemy.orm import Session
from app.core.response import success_response
from app.db.session import get_db
from app.services.user_service import UserService

router = APIRouter(prefix="/users")


@router.get("/")
def get_users(request: Request, db: Session = Depends(get_db)):
    user_service = UserService(request, db)
    return user_service.register_user()
    

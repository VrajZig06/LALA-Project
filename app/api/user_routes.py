from fastapi import APIRouter, Request, Depends
from sqlalchemy.orm import Session
from app.core.response import success_response
from app.db.session import get_db
from app.services.user_service import UserService
from app.core.dependecy import current_user

router = APIRouter(prefix="/users")


@router.get("/")
def get_users(request: Request,current_user = Depends(current_user), db: Session = Depends(get_db)):

    print(f"current_user :: {current_user}")

    user_service = UserService(request, db)
    return user_service.register_user()
    

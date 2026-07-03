from app.db.session import Session
from fastapi import status as http_status, HTTPException, Request
from app.core.response import success_response, error_response
from app.core.message import ErrorMessage, SuccessMessage
from app.core.exception import ServerException
from app.core.logger import get_logger

logger = get_logger(__name__)


class UserService:
    # Constructor
    def __init__(self, request: Request, db: Session):
        """
        Constructor: Takes request and DB connection object
        """
        self.request = request
        self.db = db

    # Method: Register User
    def register_user(self):
        try:
            return success_response(
                msg="user Registered"
            )
        except HTTPException as e:
            raise
        except Exception as e:
            raise ServerException(f"{e} \n {e}")
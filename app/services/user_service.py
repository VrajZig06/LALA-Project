from app.db.session import Session
from fastapi import Request
from fastapi import status as http_status, HTTPException
from app.core.response import success_response, error_response
from app.core.message import ErrorMessage, SuccessMessage


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
        return success_response(
            msg="DONE"
        )

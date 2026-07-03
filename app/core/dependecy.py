from fastapi import status as http_status, HTTPException, Request, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.message import ErrorMessage
from app.core.jwt import verify_token
from app.db.models.role import Role
from app.repository.role_repository import RoleRepository

# Function: Take Request as Input and Returns Payload after validating Access token
def validate_token(request: Request):
    # Get Authorization Token
    headers = request.headers
    berear_token = headers.get("authorization")

    # Check bearer token is none or len(list) < 2 
    if berear_token is None or len(berear_token.split(" ")) < 2:
        raise HTTPException(
            status_code = http_status.HTTP_401_UNAUTHORIZED,
            detail = ErrorMessage.INVALID_TOKEN
        )

    # Extract Bearer Token
    token = berear_token.split(" ")[1]

    # Now Instend of Finding from the DB decode this token and check expiry
    payload = verify_token(token)

    return payload

def current_user(request: Request, db: Session = Depends(get_db)):
    return validate_token(request)

# Note: We need to take list of roles from the dependecy so handle that using class
class RoleCheck:
    # Take Parameter from the Dependecy
    def __init__(self, roles: list[str], db: Session = Depends(get_db)):
        self.allowed_roles = roles
        self.db = db

    # Then Handle role checking logic for current user
    def __call__(self, request: Request):
        payload = validate_token(request)

        # Check for role_id in payload
        role_id = payload.get("role_id", None)

        if not role_id:
            raise HTTPException(
                status_code = http_status.HTTP_401_UNAUTHORIZED,
                detail = ErrorMessage.UNAUTHORIZED_ACCESS
            )

        # Check In Role Table for given role_id and fetch role_name
        role_repo = RoleRepository(self.db)
        role_detail = role_repo.get(role_id)

        # Extract Role Name from role_detail
        role_name = (role_detail.role_name).strip()

        # Check if current role is in Allowed Roles for API
        if role_name not in self.allowed_roles:
            raise HTTPException(
                status_code = http_status.HTTP_401_UNAUTHORIZED,
                detail = ErrorMessage.UNAUTHORIZED_ACCESS
            )

        # If All good then return current user dict
        return payload





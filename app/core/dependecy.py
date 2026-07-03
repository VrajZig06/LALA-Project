from fastapi import status as http_status, HTTPException, Request, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.message import ErrorMessage
from app.core.jwt import verify_token

def current_user(request: Request, db: Session = Depends(get_db)):

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

    return request

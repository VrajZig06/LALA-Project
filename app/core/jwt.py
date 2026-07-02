from jose import jwt
from jose.exceptions import ExpiredSignatureError, JWTError
from datetime import datetime, timezone, timedelta
from app.core.config import get_settings
from fastapi import HTTPException, status as http_status
from app.core.message import ErrorMessage, SuccessMessage

# Setting object
settings = get_settings()

# ENV Variables
JWT_SECRET_KEY = settings.JWT_SECRET_KEY
JWT_ALGORITHM = settings.JWT_ALGORITHM
JWT_ACCESS_TOKEN_EXPIRY = settings.JWT_ACCESS_TOKEN_EXPIRY
JWT_REFRESH_TOKEN_EXPIRY = settings.JWT_REFRESH_TOKEN_EXPIRY


# Function: Generate Token
def generate_token(payload: dict, expiry_time_in_min: int = 10):

    # Update Payload with Expiry Time
    payload.update(
        {
            "exp": int(
                (
                    datetime.now(tz=timezone.utc)
                    + timedelta(minutes=expiry_time_in_min)
                ).timestamp()
            )
        }
    )

    # Generate Token
    token = jwt.encode(payload, key=JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return token


# Function: Verify Token
def verify_token(token: str):
    try:
        payload = jwt.decode(token=token, key=JWT_SECRET_KEY, algorithms=JWT_ALGORITHM)

        return payload

    except ExpiredSignatureError:
        raise HTTPException(
            status_code=http_status.HTTP_401_UNAUTHORIZED,
            detail=ErrorMessage.TOKEN_EXPIRE,
        )
    except JWTError:
        raise HTTPException(
            status_code=http_status.HTTP_401_UNAUTHORIZED,
            detail=ErrorMessage.INVALID_TOKEN,
        )

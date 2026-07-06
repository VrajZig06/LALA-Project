from datetime import UTC, datetime, timedelta

from fastapi import HTTPException
from fastapi import status as http_status
from jose import jwt
from jose.exceptions import ExpiredSignatureError, JWTError

from app.core.config import get_settings
from app.core.constants import JWT_ACCESS_TOKEN_EXPIRY_TIME
from app.core.logger import get_logger
from app.core.message import ErrorMessage, LoggerMessage

# Setting object
settings = get_settings()

# Logger Initialization
logger = get_logger(__name__)

# ENV Variables
JWT_SECRET_KEY = settings.JWT_SECRET_KEY
JWT_ALGORITHM = settings.JWT_ALGORITHM
JWT_ACCESS_TOKEN_EXPIRY = settings.JWT_ACCESS_TOKEN_EXPIRY
JWT_REFRESH_TOKEN_EXPIRY = settings.JWT_REFRESH_TOKEN_EXPIRY


# Function: Generate Token
def generate_token(
    payload: dict, expiry_time_in_min: int = JWT_ACCESS_TOKEN_EXPIRY_TIME
):
    # Update Payload with Expiry Time
    payload.update(
        {
            "exp": int(
                (
                    datetime.now(tz=UTC) + timedelta(minutes=expiry_time_in_min)
                ).timestamp()
            )
        }
    )

    # Generate Token
    token = jwt.encode(payload, key=JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return token


# Function: Verify Token
def verify_token(token: str):
    user_id = None
    try:
        payload = jwt.decode(token=token, key=JWT_SECRET_KEY, algorithms=JWT_ALGORITHM)

        # Set User Id
        user_id = payload.get("user_id", "Unknown")
        return payload

    except ExpiredSignatureError as e:
        logger.error(
            LoggerMessage.ExpiredSignatureError_Logtext.format(user_id=user_id, e=e),
            exc_info=True,
        )
        raise HTTPException(
            status_code=http_status.HTTP_401_UNAUTHORIZED,
            detail=ErrorMessage.TOKEN_EXPIRE,
        )
    except JWTError as e:
        logger.error(
            LoggerMessage.ExpiredSignatureError_Logtext.format(user_id=user_id, e=e),
            exc_info=True,
        )
        raise HTTPException(
            status_code=http_status.HTTP_401_UNAUTHORIZED,
            detail=ErrorMessage.INVALID_TOKEN,
        )

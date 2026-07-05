from app.db.session import Session
from fastapi import status as http_status, HTTPException, Request
from app.core.response import success_response, error_response
from app.core.message import ErrorMessage, SuccessMessage
from app.core.exception import ServerException
from app.core.logger import get_logger
from app.schema.user import UserRegistration, UserRegistrationResponse
from app.db.models.user import User
from app.repository.user_repository import UserRepository
from app.repository.role_repository import RoleRepository
from app.common.utils import get_unix_time, generate_otp, send_email_verification_email
from app.services.email_service import email_service
from app.core.constants import DEFAULT_ROLE_NAME

logger = get_logger(__name__)


class UserService:
    # Constructor
    def __init__(self, request: Request, db: Session):
        """
        Constructor: Takes request and DB connection object
        """
        self.request = request
        self.db = db

        # Initialize Repository
        self.user_repo = UserRepository(self.db)
        self.role_repo = RoleRepository(self.db)


    # Method: Register User
    async def register_user(self, payload: UserRegistration):
        try:
            # Extract Email 
            email = payload.email
            first_name = payload.first_name
            last_name = payload.last_name
            full_name = first_name + " " + last_name

            # Check user already exist
            user_detail = self.user_repo.get_by_field("email", email)

            # Validate User Details 
            if user_detail and user_detail.is_verified:
                raise HTTPException(
                    status_code = http_status.HTTP_400_BAD_REQUEST,
                    detail = ErrorMessage.USER_ALREADY_EXIST
                )
            elif user_detail and not user_detail.is_verified:
                await send_email_verification_email(email, full_name)

                return success_response(
                    status_code=http_status.HTTP_200_OK,
                    msg=SuccessMessage.USER_VERIFICATION_EMAIL_SEND,
                    data=UserRegistrationResponse.model_validate(user_detail)
                )

            # Convert Pydantic Model to Dictionary
            user_data = payload.model_dump()

            # Add New fields otp_expiry and otp
            user_data.update({
                "otp_expiry": get_unix_time() + (5 * 60 * 1000),
                "otp": generate_otp()
            })

            await send_email_verification_email(email, full_name, user_data.get("otp"), user_data.get("otp_expiry"))

            # Find Roles 
            role_detail = self.role_repo.get_by_field(
                "role_name", DEFAULT_ROLE_NAME
            )

            if not role_detail:
                raise HTTPException(
                    status_code = http_status.HTTP_400_BAD_REQUEST,
                    detail = ErrorMessage.ROLE_NOT_FOUND
                )

            # Insert Role Id to User Data
            user_data.update({
                "role_id": role_detail.id,
                "is_active": False
            })

            # Create New User
            new_user = User(**user_data)

            self.db.add(new_user)
            self.db.commit()
            self.db.refresh(new_user)

            response_data = UserRegistrationResponse.model_validate(new_user).model_dump()

            return success_response(
                status_code= http_status.HTTP_201_CREATED,
                msg=SuccessMessage.USER_REGISTERED_SUCCESSFULLY,
                data=response_data
            )
            
        except HTTPException as e:
            raise
        except Exception as e:
            raise ServerException(e)
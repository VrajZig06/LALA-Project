from app.schema.user import ResetPassword, UserGoogleAuth
from fastapi import HTTPException, Request
from fastapi import status as http_status

import base64
import json
import httpx
from jose import jwt
from app.core.config import get_settings
from app.core.enums import LoginType

from app.common.utils import generate_otp, get_unix_time, send_email_verification_email
from app.core.constants import DEFAULT_ROLE_NAME
from app.core.jwt import generate_token
from app.core.exception import ServerException
from app.core.logger import get_logger
from app.core.message import ErrorMessage, SuccessMessage
from app.core.response import success_response
from app.db.models.user import User
from app.db.session import Session
from app.repository.role_repository import RoleRepository

from app.repository.user_repository import UserRepository
from app.core.hash import check_password, password_hash
from app.schema.user import UserOtpVerify, UserRegistration, UserRegistrationResponse, UserOtpVerifyResponse, UserLogin, UserInfo, UserLoginResponse
from app.core.constants import JWT_ACCESS_TOKEN_EXPIRY_TIME, JWT_REFRESH_TOKEN_EXPIRY_TIME

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
                    status_code=http_status.HTTP_400_BAD_REQUEST,
                    detail=ErrorMessage.USER_ALREADY_EXIST,
                )
            elif user_detail and not user_detail.is_verified:
                otp_expiry = (get_unix_time() + (5 * 60 * 1000),)
                otp = generate_otp()

                await send_email_verification_email(email, full_name, otp, otp_expiry)

                # Store New OTP
                user_detail.otp = otp
                user_detail.otp_expiry = otp_expiry

                self.db.commit()
                self.db.refresh(user_detail)

                return success_response(
                    status_code=http_status.HTTP_200_OK,
                    msg=SuccessMessage.USER_VERIFICATION_EMAIL_SEND,
                    data=UserRegistrationResponse.model_validate(user_detail),
                )

            # Convert Pydantic Model to Dictionary
            user_data = payload.model_dump()

            # Add New fields otp_expiry and otp
            user_data.update(
                {"otp_expiry": get_unix_time() + (5 * 60 * 1000), "otp": generate_otp()}
            )

            await send_email_verification_email(
                email, full_name, user_data.get("otp"), user_data.get("otp_expiry")
            )

            # Find Roles
            role_detail = self.role_repo.get_by_field("role_name", DEFAULT_ROLE_NAME)

            if not role_detail:
                raise HTTPException(
                    status_code=http_status.HTTP_400_BAD_REQUEST,
                    detail=ErrorMessage.ROLE_NOT_FOUND,
                )

            # Insert Role Id to User Data
            user_data.update({"role_id": role_detail.id, "is_active": False})

            # Create New User
            new_user = User(**user_data)

            self.db.add(new_user)
            self.db.commit()
            self.db.refresh(new_user)

            response_data = UserRegistrationResponse.model_validate(
                new_user
            ).model_dump()

            return success_response(
                status_code=http_status.HTTP_201_CREATED,
                msg=SuccessMessage.USER_REGISTERED_SUCCESSFULLY,
                data=response_data,
            )

        except HTTPException:
            raise
        except Exception as e:
            raise ServerException(e)

    async def verify_otp(self, payload: UserOtpVerify):
        try:
            # Extract user_id and otp
            user_id = payload.user_id
            otp = payload.otp

            # Now Check user in DB with user_id
            user = self.user_repo.get(user_id)

            if not user:
                raise HTTPException(
                    status_code=http_status.HTTP_404_NOT_FOUND,
                    detail=ErrorMessage.USER_NOT_FOUND,
                )

            # Check if OTP is expired
            if user.otp_expiry is None or user.otp_expiry < get_unix_time():
                raise HTTPException(
                    status_code=http_status.HTTP_400_BAD_REQUEST,
                    detail=ErrorMessage.OTP_EXPIRED,
                )

            # Check if OTP matches
            if user.otp != otp:
                raise HTTPException(
                    status_code=http_status.HTTP_400_BAD_REQUEST,
                    detail=ErrorMessage.OTP_INVALID,
                )

            # OTP is valid, mark user as verified
            user.is_verified = True
            user.is_active = True
            user.otp = None
            user.otp_expiry = None

            self.db.commit()

            return success_response(
                status_code=http_status.HTTP_200_OK,
                msg=SuccessMessage.USER_OTP_VERIFIED_SUCCESSFULLY,
                data=UserOtpVerifyResponse.model_validate(user).model_dump(),
            )
        except HTTPException:
            raise
        except Exception as e:
            raise ServerException(e)

    async def user_login(self, payload: UserLogin):
        # Extract user email and password
        email = payload.email
        password = payload.password

        # Check User with email
        user = self.user_repo.get_by_field("email", email)

        # If User not Found
        if not user or user.is_deleted:
            raise HTTPException(
                status_code = http_status.HTTP_404_NOT_FOUND,
                detail = ErrorMessage.USER_NOT_FOUND
            )

        # if user is Inactive or not is_verified
        if not user.is_active or not user.is_verified:
            raise HTTPException(
                status_code = http_status.HTTP_400_BAD_REQUEST,
                detail = ErrorMessage.USER_EMAIL_VERIFICATION_PENDING
            )

        # Check Password
        is_password_match = check_password(password, user.password)

        if not is_password_match:
            raise HTTPException(
                status_code = http_status.HTTP_401_UNAUTHORIZED,
                detail = ErrorMessage.INCORRECT_PASSWORD
            )
        
        # Prepare Token payload
        payload = {
            "id" : user.id,
            "role_id" : user.role_id,
            "email": user.email
        }

        # Generate Tokens
        access_token = generate_token(payload, JWT_ACCESS_TOKEN_EXPIRY_TIME)
        refresh_token = generate_token(payload, JWT_REFRESH_TOKEN_EXPIRY_TIME)

        # Prepared UserInfo Data
        user = UserInfo.model_validate(user).model_dump()

        response_data = UserLoginResponse(
            access_token = access_token,
            refresh_token = refresh_token,
            user=user
        )

        return success_response(
            status_code=http_status.HTTP_200_OK,
            msg=SuccessMessage.USER_LOGIN_SUCCESSFULLY,
            data=response_data
        )

    async def reset_password(self, payload: ResetPassword, current_user):

        user_id = current_user.get("id")

        user = self.user_repo.get(user_id)

        # If user not found then raise User Not Found
        if not user or user.is_deleted or not user.is_verified:
            raise HTTPException(
                status_code = http_status.HTTP_404_NOT_FOUND,
                detail = ErrorMessage.USER_NOT_FOUND
            )

        # If Both same then Raise Error
        if payload.old_password == payload.new_password:
            raise HTTPException(
                status_code = http_status.HTTP_400_BAD_REQUEST,
                detail = ErrorMessage.OLD_PASSWORD_MUST_BE_DIFFERNT
            )

        is_password_correct = check_password(payload.old_password, user.password)

        # Password doesn't matched
        if not is_password_correct:
            raise HTTPException(
                status_code = http_status.HTTP_401_UNAUTHORIZED,
                detail = ErrorMessage.INCORRECT_OLD_PASSWORD
            )

        # If all done then convert new password to hash 
        new_password_hash = password_hash(payload.new_password)

        # Set to user
        user.password = new_password_hash

        self.db.commit()
        self.db.refresh(user)

        return success_response(
            status_code= http_status.HTTP_200_OK,
            msg=SuccessMessage.PASSWORD_RESET_SUCCESSFULLY,
        )

    async def google_auth(self, payload: UserGoogleAuth):
        try:
            token = payload.token
            settings = get_settings()

            # Retrieve Google public JWKS and verify the JWT signature properly
            async with httpx.AsyncClient() as client:
                response = await client.get("https://www.googleapis.com/oauth2/v3/certs")
                jwks = response.json()
            idinfo = jwt.decode(
                token,
                jwks,
                algorithms=["RS256"],
                audience=settings.GOOGLE_CLIENT_ID,
                issuer="https://accounts.google.com"
            )


            email = idinfo.get("email")
            first_name = idinfo.get("given_name", "")
            last_name = idinfo.get("family_name", "")
            social_id = idinfo.get("sub")

            if not email:
                raise HTTPException(
                    status_code=http_status.HTTP_400_BAD_REQUEST,
                    detail="Email not provided in Google token"
                )

            # Check if user already exists
            user = self.user_repo.get_by_field("email", email)

            if user:
                # User exists
                if user.is_deleted:
                    raise HTTPException(
                        status_code=http_status.HTTP_400_BAD_REQUEST,
                        detail="User account is deleted"
                    )
                # Update user details if not matching Google profile
                updated = False
                if not user.social_id:
                    user.social_id = social_id
                    updated = True
                if user.login_type != LoginType.GOOGLE.value:
                    user.login_type = LoginType.GOOGLE.value
                    updated = True
                if not user.is_verified:
                    user.is_verified = True
                    user.is_active = True
                    updated = True
                if updated:
                    self.db.commit()
                    self.db.refresh(user)
            else:
                # Create a new user
                role_detail = self.role_repo.get_by_field("role_name", DEFAULT_ROLE_NAME)
                if not role_detail:
                    raise HTTPException(
                        status_code=http_status.HTTP_400_BAD_REQUEST,
                        detail=ErrorMessage.ROLE_NOT_FOUND
                    )

                user_data = {
                    "email": email,
                    "first_name": first_name,
                    "last_name": last_name,
                    "social_id": social_id,
                    "login_type": LoginType.GOOGLE.value,
                    "is_verified": True,
                    "is_active": True,
                    "role_id": role_detail.id
                }
                user = User(**user_data)
                self.db.add(user)
                self.db.commit()
                self.db.refresh(user)

            # Generate Access and Refresh Tokens
            token_payload = {
                "id": user.id,
                "role_id": user.role_id,
                "email": user.email
            }
            access_token = generate_token(token_payload, JWT_ACCESS_TOKEN_EXPIRY_TIME)
            refresh_token = generate_token(token_payload, JWT_REFRESH_TOKEN_EXPIRY_TIME)

            user_info = UserInfo.model_validate(user)

            response_data = UserLoginResponse(
                access_token=access_token,
                refresh_token=refresh_token,
                user=user_info
            )

            return success_response(
                status_code=http_status.HTTP_200_OK,
                msg=SuccessMessage.USER_LOGIN_SUCCESSFULLY,
                data=response_data
            )
        except Exception as e:
            if isinstance(e, HTTPException):
                raise
            raise ServerException(e)


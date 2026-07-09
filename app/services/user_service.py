
from app.schema.user import RefreshTokenResponse
from app.schema.user import RefreshTokenRequestData
import httpx
from fastapi import BackgroundTasks, HTTPException, Request
from fastapi import status as http_status
from jose import jwt

from app.common.utils import generate_otp, get_unix_time, send_email_verification_email
from app.core.config import get_settings
from app.core.constants import (
    DEFAULT_ROLE_NAME,
    FORGOT_PASSWORD_EXPIRY_TIME,
    JWT_ACCESS_TOKEN_EXPIRY_TIME,
    JWT_REFRESH_TOKEN_EXPIRY_TIME,
)
from app.core.enums import LoginType
from app.core.exception import ServerException
from app.core.hash import check_password, password_hash
from app.core.jwt import generate_token, verify_token
from app.core.logger import get_logger
from app.core.message import ErrorMessage, LoggerMessage, SuccessMessage
from app.core.response import success_response
from app.db.models.user import User
from app.db.session import Session
from app.repository.role_repository import RoleRepository
from app.repository.user_forgot_password_repository import UserForgotPasswordRepository
from app.repository.user_repository import UserRepository
from app.repository.user_session_repository import UserSessionRepository
from app.schema.user import (
    ResetPassword,
    UserGoogleAuth,
    UserInfo,
    UserLogin,
    UserLoginResponse,
    UserOtpVerify,
    UserOtpVerifyResponse,
    UserRegistration,
    UserRegistrationResponse,
    ValidateUserForgotPassword,
)
from app.services.email_service import email_service

logger = get_logger(__name__)
settings = get_settings()


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
        self.forgot_password_repo = UserForgotPasswordRepository(self.db)
        self.user_session_repo = UserSessionRepository(self.db)

    # Method: Register User
    async def register_user(self, payload: UserRegistration):
        try:
            # Extract Email
            email = payload.email
            first_name = payload.first_name
            last_name = payload.last_name
            full_name = first_name + " " + last_name

            logger.info(LoggerMessage.REGISTER_USER_START.format(email=email))

            # Check user already exist
            user_detail = self.user_repo.get_by_field("email", email)

            # Validate User Details
            if user_detail and user_detail.is_verified:
                logger.warning(LoggerMessage.REGISTER_USER_EXISTS_VERIFIED.format(email=email))
                raise HTTPException(
                    status_code=http_status.HTTP_400_BAD_REQUEST,
                    detail=ErrorMessage.USER_ALREADY_EXIST,
                )
            elif user_detail and not user_detail.is_verified:
                logger.info(LoggerMessage.REGISTER_USER_RESEND_OTP.format(email=email))
                otp_expiry = (get_unix_time() + (5 * 60 * 1000),)
                otp = generate_otp()

                await send_email_verification_email(email, full_name, otp, otp_expiry)

                # Store New OTP
                user_detail.otp = otp
                user_detail.otp_expiry = otp_expiry

                self.db.commit()
                self.db.refresh(user_detail)

                logger.info(LoggerMessage.REGISTER_USER_RESEND_SUCCESS.format(email=email))
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

            logger.info(LoggerMessage.REGISTER_USER_NEW_SEND.format(email=email))
            await send_email_verification_email(
                email, full_name, user_data.get("otp"), user_data.get("otp_expiry")
            )

            # Find Roles
            role_detail = self.role_repo.get_by_field("role_name", DEFAULT_ROLE_NAME)

            if not role_detail:
                logger.error(LoggerMessage.REGISTER_USER_ROLE_NOT_FOUND.format(role_name=DEFAULT_ROLE_NAME))
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

            logger.info(LoggerMessage.REGISTER_USER_CREATED.format(email=email, user_id=new_user.id))
            return success_response(
                status_code=http_status.HTTP_201_CREATED,
                msg=SuccessMessage.USER_REGISTERED_SUCCESSFULLY,
                data=response_data,
            )

        except HTTPException:
            raise
        except Exception as e:
            logger.error(LoggerMessage.REGISTER_USER_ERROR.format(error=e), exc_info=True)
            raise ServerException(e) from e

    async def verify_otp(self, payload: UserOtpVerify):
        try:
            # Extract user_id and otp
            user_id = payload.user_id
            otp = payload.otp

            logger.info(LoggerMessage.VERIFY_OTP_START.format(user_id=user_id))

            # Check user in DB with user_id
            user = self.user_repo.get(user_id)

            if not user:
                logger.warning(LoggerMessage.VERIFY_OTP_USER_NOT_FOUND.format(user_id=user_id))
                raise HTTPException(
                    status_code=http_status.HTTP_404_NOT_FOUND,
                    detail=ErrorMessage.USER_NOT_FOUND,
                )

            # Check if OTP is expired
            if user.otp_expiry is None or user.otp_expiry < get_unix_time():
                logger.warning(LoggerMessage.VERIFY_OTP_EXPIRED.format(user_id=user_id))
                raise HTTPException(
                    status_code=http_status.HTTP_400_BAD_REQUEST,
                    detail=ErrorMessage.OTP_EXPIRED,
                )

            # Check if OTP matches
            if user.otp != otp:
                logger.warning(LoggerMessage.VERIFY_OTP_INVALID.format(user_id=user_id))
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

            logger.info(LoggerMessage.VERIFY_OTP_SUCCESS.format(user_id=user_id))
            return success_response(
                status_code=http_status.HTTP_200_OK,
                msg=SuccessMessage.USER_OTP_VERIFIED_SUCCESSFULLY,
                data=UserOtpVerifyResponse.model_validate(user).model_dump(),
            )
        except HTTPException:
            raise
        except Exception as e:
            logger.error(LoggerMessage.VERIFY_OTP_ERROR.format(error=e), exc_info=True)
            raise ServerException(e) from e

    async def user_login(self, payload: UserLogin):
        try:
            # Extract user email and password
            email = payload.email
            password = payload.password
            fcm_token = payload.fcm_token or None

            logger.info(LoggerMessage.USER_LOGIN_START.format(email=email))

            # Check User with email
            user = self.user_repo.get_by_field("email", email)

            # If User not Found
            if not user or user.is_deleted:
                logger.warning(LoggerMessage.USER_LOGIN_USER_NOT_FOUND.format(email=email))
                raise HTTPException(
                    status_code = http_status.HTTP_404_NOT_FOUND,
                    detail = ErrorMessage.USER_NOT_FOUND
                )

            # If user is Inactive or not is_verified
            if not user.is_active or not user.is_verified:
                logger.warning(LoggerMessage.USER_LOGIN_PENDING_VERIFICATION.format(email=email))
                raise HTTPException(
                    status_code = http_status.HTTP_400_BAD_REQUEST,
                    detail = ErrorMessage.USER_EMAIL_VERIFICATION_PENDING
                )

            # Check Password
            is_password_match = check_password(password, user.password)

            if not is_password_match:
                logger.warning(LoggerMessage.USER_LOGIN_INCORRECT_PASSWORD.format(email=email))
                raise HTTPException(
                    status_code = http_status.HTTP_401_UNAUTHORIZED,
                    detail = ErrorMessage.INCORRECT_PASSWORD
                )

            # Prepare Token payload
            token_payload = {
                "id" : user.id,
                "role_id" : user.role_id,
                "email": user.email
            }

            # Generate Tokens
            access_token = generate_token(token_payload, JWT_ACCESS_TOKEN_EXPIRY_TIME)
            refresh_token = generate_token(token_payload, JWT_REFRESH_TOKEN_EXPIRY_TIME)

            # Find All Sessions with user_id and make inactive all sessions 
            self.db.query(self.user_session_repo.model).filter(self.user_session_repo.model.user_id == user.id,).update(
                {
                    "is_active": False
                }
            )  

            # Add To Session
            self.user_session_repo.create({
                "session": access_token,
                "refresh_token": refresh_token,
                'user_id': user.id,
                "fcm_token": fcm_token
            })

            # Prepared UserInfo Data
            user_info = UserInfo.model_validate(user).model_dump()

            response_data = UserLoginResponse(
                access_token = access_token,
                refresh_token = refresh_token,
                user=user_info
            )

            logger.info(LoggerMessage.USER_LOGIN_SUCCESS.format(email=email, user_id=user.id))
            return success_response(
                status_code=http_status.HTTP_200_OK,
                msg=SuccessMessage.USER_LOGIN_SUCCESSFULLY,
                data=response_data
            )
        except HTTPException:
            raise
        except Exception as e:
            logger.error(LoggerMessage.USER_LOGIN_ERROR.format(error=e), exc_info=True)
            raise ServerException(e) from e

    async def reset_password(self, payload: ResetPassword, current_user):
        try:
            user_id = current_user.get("id")

            logger.info(LoggerMessage.RESET_PASSWORD_START.format(user_id=user_id))

            user = self.user_repo.get(user_id)

            # If user not found then raise User Not Found
            if not user or user.is_deleted or not user.is_verified:
                logger.warning(LoggerMessage.RESET_PASSWORD_USER_NOT_FOUND.format(user_id=user_id))
                raise HTTPException(
                    status_code = http_status.HTTP_404_NOT_FOUND,
                    detail = ErrorMessage.USER_NOT_FOUND
                )

            # If Both same then Raise Error
            if payload.old_password == payload.new_password:
                logger.warning(LoggerMessage.RESET_PASSWORD_IDENTICAL.format(user_id=user_id))
                raise HTTPException(
                    status_code = http_status.HTTP_400_BAD_REQUEST,
                    detail = ErrorMessage.OLD_PASSWORD_MUST_BE_DIFFERNT
                )

            is_password_correct = check_password(payload.old_password, user.password)

            # Password doesn't matched
            if not is_password_correct:
                logger.warning(LoggerMessage.RESET_PASSWORD_INCORRECT_OLD.format(user_id=user_id))
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

            logger.info(LoggerMessage.RESET_PASSWORD_SUCCESS.format(user_id=user_id))
            return success_response(
                status_code= http_status.HTTP_200_OK,
                msg=SuccessMessage.PASSWORD_RESET_SUCCESSFULLY,
            )
        except HTTPException:
            raise
        except Exception as e:
            logger.error(LoggerMessage.RESET_PASSWORD_ERROR.format(error=e), exc_info=True)
            raise ServerException(e) from e

    async def google_auth(self, payload: UserGoogleAuth):
        try:
            token = payload.token
            logger.info(LoggerMessage.GOOGLE_AUTH_START)

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
                logger.error(LoggerMessage.GOOGLE_AUTH_NO_EMAIL)
                raise HTTPException(
                    status_code=http_status.HTTP_400_BAD_REQUEST,
                    detail=ErrorMessage.GOOGLE_EMAIL_NOT_PROVIDED
                )

            # Check if user already exists
            user = self.user_repo.get_by_field("email", email)

            if user:
                # User exists
                if user.is_deleted:
                    logger.warning(LoggerMessage.GOOGLE_AUTH_DELETED.format(email=email))
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
                    logger.info(LoggerMessage.GOOGLE_AUTH_UPDATE_PROFILE.format(email=email))
                    self.db.commit()
                    self.db.refresh(user)
            else:
                # Create a new user
                logger.info(LoggerMessage.GOOGLE_AUTH_PROVISION_NEW.format(email=email))
                role_detail = self.role_repo.get_by_field("role_name", DEFAULT_ROLE_NAME)
                if not role_detail:
                    logger.error(LoggerMessage.GOOGLE_AUTH_ROLE_NOT_FOUND.format(role_name=DEFAULT_ROLE_NAME))
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

            logger.info(LoggerMessage.GOOGLE_AUTH_SUCCESS.format(email=email, user_id=user.id))
            return success_response(
                status_code=http_status.HTTP_200_OK,
                msg=SuccessMessage.USER_LOGIN_SUCCESSFULLY,
                data=response_data
            )
        except Exception as e:
            if isinstance(e, HTTPException):
                raise
            logger.error(LoggerMessage.GOOGLE_AUTH_ERROR.format(error=e), exc_info=True)
            raise ServerException(e) from e

    async def forgot_password(self, payload, background_tasks: BackgroundTasks):
        try:
            # Extract User Email
            email = payload.email

            logger.info(LoggerMessage.FORGOT_PASSWORD_START.format(email=email))

            # Check User in DB
            user = self.user_repo.get_by_field("email", email)

            # user not in db
            if not user or user.is_deleted:
                logger.warning(LoggerMessage.FORGOT_PASSWORD_USER_NOT_FOUND.format(email=email))
                raise HTTPException(
                    status_code = http_status.HTTP_404_NOT_FOUND,
                    detail = ErrorMessage.FORGOT_PASSWORD_MSG
                )

            # if user is verified
            if not user.is_verified or not user.is_active:
                logger.warning(LoggerMessage.FORGOT_PASSWORD_UNVERIFIED.format(email=email))
                raise HTTPException(
                    status_code = http_status.HTTP_400_BAD_REQUEST,
                    detail = ErrorMessage.USER_NEEDS_TO_VERIFY
                )

            # Retrieve all active reset password tracks for this user
            active_tracks = self.db.query(self.forgot_password_repo.model).filter(
                self.forgot_password_repo.model.user_id == user.id,
                self.forgot_password_repo.model.is_active,
                not self.forgot_password_repo.model.is_deleted
            ).all()

            now = get_unix_time()
            active_valid_track = None
            for track in active_tracks:
                if now < track.link_expiry:
                    active_valid_track = track
                    break

            if active_valid_track:
                logger.info(LoggerMessage.FORGOT_PASSWORD_ACTIVE_LINK_EXISTS.format(user_id=user.id))
                return success_response(
                    status_code=http_status.HTTP_200_OK,
                    msg=SuccessMessage.ALREADY_SENT_RESET_PASSWORD_LINK
                )

            # Deactivate all existing active tracks (they are either expired, or we are issuing a new request)
            for track in active_tracks:
                track.is_active = False
            self.db.commit()

            # Generate Token for Reset Password Link
            token_payload = {
                "user_id": user.id,
                "email" : email
            }

            reset_password_token = generate_token(
                token_payload, expiry_time_in_min=FORGOT_PASSWORD_EXPIRY_TIME
            )

            reset_password_link = f"{settings.FRONTEND_BASE_URL}/forgot-password?token={reset_password_token}"

            full_name = f"{user.first_name} {user.last_name}" if user.first_name else None

            # Add To Background Tasks
            background_tasks.add_task(
                email_service.send_reset_password_email, email, reset_password_link, full_name, FORGOT_PASSWORD_EXPIRY_TIME
            )

            # Add to DB
            self.forgot_password_repo.create(
                {
                    "user_id": user.id,
                    "link_expiry": get_unix_time() + FORGOT_PASSWORD_EXPIRY_TIME * 60 * 1000,
                    "is_active": True
                }
            )

            logger.info(LoggerMessage.FORGOT_PASSWORD_LINK_GENERATED.format(email=email))
            return success_response(
                status_code=http_status.HTTP_200_OK,
                msg=ErrorMessage.FORGOT_PASSWORD_MSG,
            )
        except HTTPException:
            raise
        except Exception as e:
            logger.error(LoggerMessage.FORGOT_PASSWORD_ERROR.format(error=e), exc_info=True)
            raise ServerException(e) from e

    # Validate Forgot Password
    async def validate_forgot_password(self, payload: ValidateUserForgotPassword):
        try:
            # Extract Information from payload
            token = payload.token
            new_password = payload.new_password

            logger.info(LoggerMessage.VALIDATE_FORGOT_PASSWORD_START)

            # Verify the token
            decoded_payload = verify_token(token)
            user_id = decoded_payload.get("user_id")

            # Check User in DB
            user = self.user_repo.get(user_id)

            if not user or user.is_deleted or not user.is_verified:
                logger.warning(LoggerMessage.VALIDATE_FORGOT_PASSWORD_USER_NOT_FOUND.format(user_id=user_id))
                raise HTTPException(
                    status_code = http_status.HTTP_404_NOT_FOUND,
                    detail = ErrorMessage.USER_NOT_FOUND
                )

            # Check DB for active tracking record for this user
            active_tracks = self.db.query(self.forgot_password_repo.model).filter(
                self.forgot_password_repo.model.user_id == user.id,
                self.forgot_password_repo.model.is_active == True,
                # not self.forgot_password_repo.model.is_deleted
            ).all()

            if not active_tracks:
                logger.warning(LoggerMessage.VALIDATE_FORGOT_PASSWORD_NO_ACTIVE.format(user_id=user.id))
                raise HTTPException(
                    status_code = http_status.HTTP_400_BAD_REQUEST,
                    detail = ErrorMessage.INVALID_RESET_LINK
                )

            now = get_unix_time()
            valid_track = None
            for track in active_tracks:
                if now < track.link_expiry:
                    valid_track = track
                    break

            if not valid_track:
                logger.warning(LoggerMessage.VALIDATE_FORGOT_PASSWORD_EXPIRED.format(user_id=user.id))
                # Deactivate expired tracks
                for track in active_tracks:
                    track.is_active = False
                self.db.commit()
                raise HTTPException(
                    status_code = http_status.HTTP_400_BAD_REQUEST,
                    detail = ErrorMessage.TOKEN_EXPIRE
                )

            # Convert new password to hash
            new_password_hash = password_hash(new_password)

            # Update User password
            user.password = new_password_hash

            # Invalidate all active tracks so the link cannot be reused
            for track in active_tracks:
                track.is_active = False

            self.db.commit()
            self.db.refresh(user)

            logger.info(LoggerMessage.VALIDATE_FORGOT_PASSWORD_SUCCESS.format(user_id=user.id))
            return success_response(
                status_code = http_status.HTTP_200_OK,
                msg = SuccessMessage.PASSWORD_RESET_SUCCESSFULLY,
            )
        except HTTPException:
            raise
        except Exception as e:
            logger.error(LoggerMessage.VALIDATE_FORGOT_PASSWORD_ERROR.format(error=e), exc_info=True)
            raise ServerException(e) from e

    # Renew access token
    async def refresh_token(self, token):
        refresh_token = token

        # Now check the refresh_token in db
        user_session = self.user_session_repo.get_by_field("refresh_token", refresh_token)

        if not user_session:
            raise  HTTPException(
                status_code = http_status.HTTP_403_FORBIDDEN,
                detail = ErrorMessage.USER_SESSION_NOT_FOUND
            )

        # Check if user_session record is active
        if not user_session.is_active:
            raise HTTPException(
                status_code = http_status.HTTP_403_FORBIDDEN,
                detail = ErrorMessage.USER_SESSION_NOT_FOUND
            )

        # Validate Refresh Token 
        payload = verify_token(refresh_token)

        # If all good then we will get used_id as "id"
        user_id = payload.get("id")

        # Now check user in DB
        user = self.user_repo.get(user_id)

        if not user or not user.is_active or user.is_deleted:
            raise HTTPException(
                status_code = http_status.HTTP_403_FORBIDDEN,
                detail = ErrorMessage.USER_SESSION_NOT_FOUND
            )

        # Buid new payload
        token_payload = {
            "id" : user.id,
            "role_id": user.role_id,
            "email": user.email
        }

        access_token = generate_token(token_payload, JWT_ACCESS_TOKEN_EXPIRY_TIME)
        refresh_token = generate_token(token_payload, JWT_REFRESH_TOKEN_EXPIRY_TIME)

        # Invalidate all active sessions
        self.db.query(
                self.user_session_repo.model
            ).filter(
                self.user_session_repo.model.user_id == user.id, 
                self.user_session_repo.model.is_active == True
            ).update(
            {
                "is_active" : False
            }
        )

        # Now Add New Session 
        user_session = self.user_session_repo.create({
            "user_id" : user.id,
            "session" : access_token,
            "refresh_token" : refresh_token
        })

        return success_response(
            status_code= http_status.HTTP_200_OK,
            msg=SuccessMessage.TOKEN_REFRESHED_SUCCESSFULLY,
            data=RefreshTokenResponse(
                access_token = access_token, 
                refresh_token = refresh_token
            ).model_dump()
        )
        
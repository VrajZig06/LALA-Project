"""
This File Give All Static API Messages
"""


class SuccessMessage:
    SERVER_HEALTHY = "Server is Healthy!"
    RESPONSE_FETCHED_SUCCESSFULLY = "Response Fetched Successfully"
    USER_REGISTERED_SUCCESSFULLY = "User Registered Successfully!"
    USER_VERIFICATION_EMAIL_SEND = "User Verification Email Sent"
    USER_NOT_FOUND = "User Not Found!"
    USER_OTP_VERIFIED_SUCCESSFULLY = "User Verified Successfully!"
    USER_LOGIN_SUCCESSFULLY = "User Login Successfully"
    PASSWORD_RESET_SUCCESSFULLY = "User Password Reset Successfully"
    ALREADY_SENT_RESET_PASSWORD_LINK = (
        "Already Sent reset password Link, Please Check Your Inbox"
    )
    TOKEN_REFRESHED_SUCCESSFULLY = "Access Token Refreshsed Successfully"
    ROOM_CREATED_SUCCESSFULLY = "Call Room Created Successfully"
    ROOM_FETCHED_SUCCESSFULLY = "Call Room Details Fetched Successfully"
    NOTIFICATION_SENT_SUCCESSFULLY = "Notification Sent Successfully!"


class ErrorMessage:
    TOKEN_EXPIRE = "Token Expired"
    INVALID_TOKEN = "Token Invalid"
    INTERNAL_SERVER_ERROR = "Internal Server Error"
    UNAUTHORIZED_ACCESS = "You are not Authorize to Access!"
    INVALID_CREDENTIALS = "Invalid Credentials"
    USER_ALREADY_EXIST = "User Already Exist"
    ROLE_NOT_FOUND = "Role Not Found!"
    USER_NOT_FOUND = "User Not Found!"
    OTP_EXPIRED = "OTP Expired!"
    OTP_INVALID = "OTP Invalid"
    USER_EMAIL_VERIFICATION_PENDING = "User Email Verification is Pending!"
    INCORRECT_PASSWORD = "Incorrect Password"
    OLD_PASSWORD_MUST_BE_DIFFERNT = "Old Password must be different then New Password"
    INCORRECT_OLD_PASSWORD = "Incorrect Old Password"
    USER_NOT_FOUND_WITH_EMAL = "User not found with this email"
    USER_NEEDS_TO_VERIFY = "User is not Verify yet"
    FORGOT_PASSWORD_MSG = (
        "If an account exists for this email,we've sent password reset instructions."
    )
    GOOGLE_EMAIL_NOT_PROVIDED = "Email not provided in Google token"
    INVALID_RESET_LINK = "This reset link is invalid or has already been used."
    USER_SESSION_NOT_FOUND = "User Session not Found!"
    FILE_NOT_FOUND = "File not Found!"
    ROOM_NOT_FOUND = "Call Room Not Found!"
    ROOM_INACTIVE = "Call Room is inactive"


class LoggerMessage:
    ExpiredSignatureError_Logtext = "user_id :: {user_id} & error :: {e}"

    # API User Routes Logs
    API_SIGNUP_ATTEMPT = "API signup: registration attempt for email='{email}'"
    API_SIGNUP_COMPLETED = "API signup: registration completed for email='{email}'"
    API_LOGIN_ATTEMPT = "API login: login attempt for email='{email}'"
    API_LOGIN_SUCCESS = "API login: login successful for email='{email}'"
    API_VERIFY_OTP_ATTEMPT = (
        "API verify-otp: OTP verification attempt for user_id='{user_id}'"
    )
    API_VERIFY_OTP_SUCCESS = (
        "API verify-otp: OTP verification successful for user_id='{user_id}'"
    )
    API_RESET_PASSWORD_REQUEST = (
        "API reset-password: password reset request for user_id='{user_id}'"
    )
    API_RESET_PASSWORD_SUCCESS = (
        "API reset-password: password reset successful for user_id='{user_id}'"
    )
    API_GOOGLE_AUTH_REQUEST = "API google-auth: google authentication request received"
    API_GOOGLE_AUTH_SUCCESS = "API google-auth: google authentication successful"
    API_FORGOT_PASSWORD_REQUEST = "API forgot-password: request for email='{email}'"
    API_FORGOT_PASSWORD_COMPLETED = (
        "API forgot-password: request completed for email='{email}'"
    )
    API_VALIDATE_PASSWORD_REQUEST = (
        "API validate-password: password validation request received"
    )
    API_VALIDATE_PASSWORD_SUCCESS = (
        "API validate-password: password reset validation successful"
    )
    API_REFRESH_TOKEN_REQUEST = "API refresh-token: refresh_token request recieved"
    API_REFRESH_TOKEN_SUCCESS = (
        "API refresh-token: refresh_token generates access token successfully"
    )

    # User Service Logs
    REGISTER_USER_START = (
        "register_user: Start registration process for email='{email}'"
    )
    REGISTER_USER_EXISTS_VERIFIED = (
        "register_user: User already exists and is verified for email='{email}'"
    )
    REGISTER_USER_RESEND_OTP = "register_user: Resending verification OTP to existing unverified user email='{email}'"
    REGISTER_USER_RESEND_SUCCESS = (
        "register_user: Verification email resent successfully to email='{email}'"
    )
    REGISTER_USER_NEW_SEND = (
        "register_user: Sending verification email for new user email='{email}'"
    )
    REGISTER_USER_ROLE_NOT_FOUND = (
        "register_user: Default role '{role_name}' not found in database"
    )
    REGISTER_USER_CREATED = "register_user: New user record created successfully for email='{email}', user_id='{user_id}'"
    REGISTER_USER_ERROR = "register_user: Unexpected error during registration: {error}"

    VERIFY_OTP_START = "verify_otp: Verifying OTP code for user_id='{user_id}'"
    VERIFY_OTP_USER_NOT_FOUND = "verify_otp: User not found with user_id='{user_id}'"
    VERIFY_OTP_EXPIRED = "verify_otp: OTP expired or not set for user_id='{user_id}'"
    VERIFY_OTP_INVALID = "verify_otp: Invalid OTP code provided for user_id='{user_id}'"
    VERIFY_OTP_SUCCESS = "verify_otp: OTP verified and user activated successfully for user_id='{user_id}'"
    VERIFY_OTP_ERROR = "verify_otp: Unexpected error during OTP verification: {error}"

    USER_LOGIN_START = "user_login: Authentication request received for email='{email}'"
    USER_LOGIN_USER_NOT_FOUND = (
        "user_login: Login failed: User not found or deleted for email='{email}'"
    )
    USER_LOGIN_PENDING_VERIFICATION = "user_login: Login failed: Email verification pending or account inactive for email='{email}'"
    USER_LOGIN_INCORRECT_PASSWORD = (
        "user_login: Login failed: Incorrect password for email='{email}'"
    )
    USER_LOGIN_SUCCESS = (
        "user_login: Login successful for email='{email}', user_id='{user_id}'"
    )
    USER_LOGIN_ERROR = "user_login: Unexpected error during login flow: {error}"

    RESET_PASSWORD_START = (
        "reset_password: Initiating password reset for user_id='{user_id}'"
    )
    RESET_PASSWORD_USER_NOT_FOUND = (
        "reset_password: User not found or invalid status for user_id='{user_id}'"
    )
    RESET_PASSWORD_IDENTICAL = "reset_password: Password reset failed: new password is identical to old password for user_id='{user_id}'"
    RESET_PASSWORD_INCORRECT_OLD = "reset_password: Password reset failed: incorrect old password for user_id='{user_id}'"
    RESET_PASSWORD_SUCCESS = (
        "reset_password: Password reset successful for user_id='{user_id}'"
    )
    RESET_PASSWORD_ERROR = (
        "reset_password: Unexpected error during password reset: {error}"
    )

    GOOGLE_AUTH_START = "google_auth: Google SSO token verification started"
    GOOGLE_AUTH_NO_EMAIL = (
        "google_auth: Google token decoded successfully but did not contain email"
    )
    GOOGLE_AUTH_DELETED = "google_auth: Google login failed: existing user account is deleted for email='{email}'"
    GOOGLE_AUTH_UPDATE_PROFILE = "google_auth: Updating profile details to match Google Identity for email='{email}'"
    GOOGLE_AUTH_PROVISION_NEW = (
        "google_auth: No existing user found. Provisioning new user for email='{email}'"
    )
    GOOGLE_AUTH_ROLE_NOT_FOUND = (
        "google_auth: Default role '{role_name}' not found in database"
    )
    GOOGLE_AUTH_SUCCESS = "google_auth: Google SSO authentication successful for email='{email}', user_id='{user_id}'"
    GOOGLE_AUTH_ERROR = (
        "google_auth: Unexpected error during Google authentication: {error}"
    )

    FORGOT_PASSWORD_START = (
        "forgot_password: Password recovery requested for email='{email}'"
    )
    FORGOT_PASSWORD_USER_NOT_FOUND = "forgot_password: Recovery failed: User not found or deleted for email='{email}'"
    FORGOT_PASSWORD_UNVERIFIED = "forgot_password: Recovery failed: User is unverified or inactive for email='{email}'"
    FORGOT_PASSWORD_ACTIVE_LINK_EXISTS = "forgot_password: Active, unexpired reset link already exists for user_id='{user_id}'"
    FORGOT_PASSWORD_LINK_GENERATED = (
        "forgot_password: Password reset link generated and queued for email='{email}'"
    )
    FORGOT_PASSWORD_ERROR = (
        "forgot_password: Unexpected error during forgot password flow: {error}"
    )

    VALIDATE_FORGOT_PASSWORD_START = (
        "validate_forgot_password: Validating forgot password recovery token"
    )
    VALIDATE_FORGOT_PASSWORD_USER_NOT_FOUND = "validate_forgot_password: User not found or deleted/unverified for user_id='{user_id}'"
    VALIDATE_FORGOT_PASSWORD_NO_ACTIVE = "validate_forgot_password: Link validation failed: no active track records found in DB for user_id='{user_id}'"
    VALIDATE_FORGOT_PASSWORD_EXPIRED = "validate_forgot_password: Link validation failed: active tracks are expired for user_id='{user_id}'"
    VALIDATE_FORGOT_PASSWORD_SUCCESS = "validate_forgot_password: Password recovery and update successful for user_id='{user_id}'"
    VALIDATE_FORGOT_PASSWORD_ERROR = "validate_forgot_password: Unexpected error during forgot password validation: {error}"
    NOTIFICATION_SERVICE_INIT = "Notification Service Init..."

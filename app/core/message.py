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


class LoggerMessage:
    ExpiredSignatureError_Logtext = "user_id :: {user_id} & error :: {e}"

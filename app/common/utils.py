from datetime import datetime, timezone
from random import randint
from app.services.email_service import email_service
from pydantic import EmailStr

# Function: Get Unix Time
def get_unix_time() -> int:
    """
    Return UNIX TIME IN MILISECONDS
    """

    return int(datetime.now(tz=timezone.utc).timestamp() * 1000)

# Function: Get 4 digit OTP
def generate_otp() -> int:
    """
    Return 4 digis random number
    """

    return int("".join([str(randint(a=1, b=9)) for i in range(4)]))

# Function: Send Email Varification OTP 
async def send_email_verification_email(email: EmailStr, full_name: str) -> None:
    # Send Email for OTP Verification
    otp_expiry = get_unix_time() + (5 * 60 * 1000) # Add 5 Min to current time

    otp = generate_otp()

    await email_service.send_otp_email(
        to_email=email,
        otp=otp,
        name=full_name
    )
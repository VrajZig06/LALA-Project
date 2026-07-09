from datetime import UTC, datetime
from random import randint

from pydantic import EmailStr

from app.services.email_service import email_service


# Function: Get Unix Time
def get_unix_time() -> int:
    """
    Return UNIX TIME IN MILISECONDS
    """

    return int(datetime.now(tz=UTC).timestamp() * 1000)


# Function: Get 4 digit OTP
def generate_otp() -> int:
    """
    Return 4 digis random number
    """

    return int("".join([str(randint(a=1, b=9)) for i in range(4)]))


# Function: Send Email Varification OTP
async def send_email_verification_email(
    email: EmailStr,
    full_name: str,
    otp: int | None = None,
    otp_expiry: int | None = None,
) -> None:
    # Send Email for OTP Verification

    if otp is None or otp_expiry is None:
        otp_expiry = get_unix_time() + (5 * 60 * 1000)  # Add 5 Min to current time
        otp = generate_otp()

    await email_service.send_otp_email(to_email=email, otp=otp, name=full_name)


def generate_room_code() -> str:
    """
    Return a formatted random room code like 'abc-defg-hij'
    """
    import random
    import string
    chars = string.ascii_lowercase
    part1 = "".join(random.choices(chars, k=3))
    part2 = "".join(random.choices(chars, k=4))
    part3 = "".join(random.choices(chars, k=3))
    return f"{part1}-{part2}-{part3}"


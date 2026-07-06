from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.core.hash import password_hash


class UserRegistration(BaseModel):
    first_name: str = Field(..., description="First name of the User")
    last_name: str = Field(..., description="Last Name of the User ")
    email: EmailStr = Field(..., description="Email of user")
    password: str = Field(..., description="Password of user account")

    # We Convert Plain text to Hash text
    @field_validator("password", mode="after")
    def hash_password(v):
        return password_hash(v)


class UserRegistrationResponse(BaseModel):
    id: str
    first_name: str
    last_name: str
    email: str
    is_verified: bool
    role_id: str

    model_config = ConfigDict(from_attributes=True)


class UserOtpVerify(BaseModel):
    otp: int
    user_id: str


class UserOtpVerifyResponse(BaseModel):
    email: str
    id: str
    is_verified: bool
    is_active: bool

    model_config = ConfigDict(from_attributes=True)
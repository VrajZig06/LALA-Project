from pydantic import BaseModel, Field, EmailStr, field_validator
from app.core.hash import password_hash

class UserRegistration(BaseModel):
    first_name: str = Field(..., description="First name of the User")
    last_name: str = Field(..., description="Last Name of the User ")
    email: EmailStr = Field(..., description="Email of user")
    password: str = Field(..., description='Password of user account')

    # We Convert Plain text to Hash text
    @field_validator("password", mode = "after")
    def hash_password(v):
        return password_hash(v)

    
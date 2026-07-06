from enum import Enum


# Login Type
class LoginType(str, Enum):
    EMAIL = "email"
    GOOGLE = "google"
    GITHUB = "github"
    FACEBOOK = "facebook"

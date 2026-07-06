# pyrefly: ignore [missing-import]
from pwdlib import PasswordHash

password_hasher = PasswordHash.recommended()


# Function: Take Plain Text and return hash Text
def password_hash(plain_text: str) -> str:
    return password_hasher.hash(plain_text)


# Function: Take Plain text and Hash text and check
def check_password(plain_text: str, hash_text: str) -> bool:

    # Check if both correct
    if not password_hasher.verify(plain_text, hash_text):
        return False

    return True

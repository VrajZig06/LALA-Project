# pyrefly: ignore [missing-import]
from pwdlib import PasswordHash
from fastapi import HTTPException, status as http_status
from app.core.message import ErrorMessage 

password_hasher = PasswordHash.recommended()

# Function: Take Plain Text and return hash Text
def password_hash(plain_text: str) -> str:
    return password_hasher.hash(plain_text)

# Function: Take Plain text and Hash text and check 
def check_password(plain_text: str, hash_text: str) -> bool:
    current_user_hash_text = password_hash.hash(plain_text)

    # Check if both correct
    if current_user_hash_text != hash_text:
        return False

    return True
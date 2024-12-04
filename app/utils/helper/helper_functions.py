import base64
from datetime import datetime
import random
import string

from cryptography.fernet import Fernet, InvalidToken

from app.config import env_variables
from app.features.aws.secretKey import get_secret_keys

env_data = env_variables()
keys = get_secret_keys()


def generate_otp(length=4):
    characters = string.digits
    otp = "".join(random.choice(characters) for _ in range(length))
    return otp


def encrypt_otp(otp: int) -> str:
    key = keys["ENCRYPTION_KEY"]
    if key is None:
        raise ValueError("Encryption key not found in environment variable.")

    f = Fernet(key.encode())
    encrypted_otp = f.encrypt(str(otp).encode())
    encoded_otp = base64.urlsafe_b64encode(encrypted_otp).decode()
    return encoded_otp


def decrypt_otp(encrypted_otp: str) -> str:
    key = keys["ENCRYPTION_KEY"]

    if key is None:
        raise ValueError("Encryption key not found in environment variable.")

    if len(key) != 44:
        raise ValueError("Invalid Fernet key. Key must be 32 bytes.")

    try:
        f = Fernet(key.encode())
        decrypted_otp = f.decrypt(base64.urlsafe_b64decode(encrypted_otp.encode()))
        return decrypted_otp.decode()
    except InvalidToken as e:
        print(e)

        raise ValueError("Invalid or corrupted cipher text.")


def capitalize_words(value):
    if value is None:
        return value
    return " ".join(word.capitalize() for word in value.split())
def format_datetime_custom(date: datetime) -> str:
    if date is None:
        return "N/A"
    return date.strftime("%B %d %Y %I:%M %p")

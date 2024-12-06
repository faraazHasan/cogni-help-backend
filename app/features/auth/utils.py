import base64
import random
import string
from datetime import datetime

from cryptography.fernet import Fernet, InvalidToken
from jose import jwe, jwt
from passlib.hash import bcrypt

from app.common import constants
from app.common.email_sendgrid_utils import send_email
from app.config import env_variables
from app.features.aws.secretKey import get_secret_keys

env_data = env_variables()
keys = get_secret_keys()


# Generate a random OTP
def generate_otp(length=6):
    characters = string.digits
    otp = "".join(random.choice(characters) for _ in range(length))
    return otp


def create_access_token(data: dict):
    to_encode = data
    # never expire OTP
    encoded_jwt = jwt.encode(
        to_encode, key=keys["SECRET_KEY"], algorithm=keys["ALGORITHM"]
    )
    encoded_jwe = jwe.encrypt(
        encoded_jwt,
        "asecret128bitkey",
        algorithm="dir",
        encryption="A128GCM",
    )
    return encoded_jwe

def decode_token(token: str):
    jwt_token = jwe.decrypt(token, "asecret128bitkey")
    decoded_token = jwt.decode(
        jwt_token, keys["SECRET_KEY"], algorithms=keys["ALGORITHM"]
    )
    return decoded_token


def verify_password(plain_password, hashed_password):
    return bcrypt.verify(plain_password, hashed_password)


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
        print(e, "error in ", decrypt_otp)

        raise ValueError("Invalid or corrupted cipher text.")


async def send_verification_otp(user, template_env, template_name, subject, otp):
    try:
        # Render the email template with the OTP and other details
        template = template_env.get_template(template_name)
        rendered_message = template.render(
            user_name=user.first_name.capitalize() + " " + user.last_name.capitalize(),
            otp=otp,
            CURRENT_YEAR=datetime.now().year,  # Use current year dynamically
        )

        # Send the email with the OTP
        send_email(
            keys["SENDER_EMAIL"],
            user.email,
            subject,
            rendered_message,
        )

        return {
            "message": user.account_type == "user" and constants.OTP_SENT_SUCCESSFULLY or constants.ADMIN_OTP_SENT_SUCCESSFULLY,
            "success": True,
            "data": {"user": user.to_dict()},
        }
    except Exception as e:
        print("Error in send_verification_otp", e)
        return {
            "message": user.account_type == "user" and constants.SOMETHING_WENT_WRONG or constants.ADMIN_SOMETHING_WENT_WRONG,
            "success": False,
            "error": e,
        }

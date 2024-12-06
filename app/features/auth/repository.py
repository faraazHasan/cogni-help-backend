from app.features.auth.schemas import UserSchema
import json
import os
from datetime import datetime

from app.features.user.schemas import CurrentUser
from jinja2 import Environment, FileSystemLoader
from passlib.hash import bcrypt
from sqlalchemy import and_
from sqlalchemy.orm import Session

from app.common import constants
from app.config import env_variables
from app.features.auth.schemas import (
    ForgotPassSchema,
    LoginSchema,
    ResendVerificationCodeSchema,
    ResetPasswordFormSchema,
    UpdateAdminDetails,
    UpdateAdminImage,
    UpdatePassword,
    UserSchema,
    VerifyUserSignupOtpSchema,
)
from app.features.auth.utils import (
    create_access_token,
    decode_token,
    send_verification_otp,
    verify_password,
)
from app.models.company import Company
from app.models.forms import Forms
from app.models.user import User
from app.models.user_sessions import UserSession
from app.utils.helper.helper_functions import decrypt_otp, encrypt_otp, generate_otp

env_data = env_variables()
current_directory = os.path.dirname(os.path.abspath(__file__))
relative_templates_directory = "../../templates"
templates_directory = os.path.join(current_directory, relative_templates_directory)
template_env = Environment(loader=FileSystemLoader(templates_directory))


async def signup(request: UserSchema, db: Session):
    try:
        password_hash = bcrypt.hash(request.password)
        otp = generate_otp()
        encrypted_id = encrypt_otp(str(otp))
        # Check if a user with the given email already exists (case insensitive)
        existing_user = (
            db.query(User).filter(User.email == request.email.lower()).first()
        )
        if existing_user and not existing_user.is_verified:
            existing_user.first_name = request.first_name
            existing_user.last_name = request.last_name
            existing_user.password = password_hash
            existing_user.verification_code = (
                json.dumps(
                    {"otp": encrypted_id, "otp_created_ts": str(datetime.now())}
                ),
            )
            return await send_verification_otp(
                existing_user,
                template_env,
                "otp_email.html",
                constants.SIGNUP_OTP_SUBJECT,
                otp,
            )
        if existing_user:
            return {
                "message": constants.USER_WITH_EMAIL_ALREADY_EXISTS,
                "success": False,
            }
        else:
            company_id = db.query(Company).filter(
                Company.name == "Cogni Help").first().id
            # Create a new user object
            # TODO remove static data  in future
            new_user = User(
                first_name=request.first_name,
                last_name=request.last_name,
                email=request.email.lower(),
                company_id=company_id,
                password=password_hash,
                is_active=False,
                is_verified=False,
                account_type="user",
                verification_code=json.dumps(
                    {"otp": encrypted_id, "otp_created_ts": str(datetime.now())}
                ),
            )

            # Add the new user to the database
            db.add(new_user)
            # Prepare and send verification email
            return await send_verification_otp(
                new_user,
                template_env,
                "otp_email.html",
                constants.SIGNUP_OTP_SUBJECT,
                otp,
            )

    except Exception as e:
        print("error in signup", e)
        return {
            "message": constants.INTERNAL_SERVER_ERROR,
            "success": False,
        }


async def verify_user_otp(request: VerifyUserSignupOtpSchema, db: Session):
    try:
        enter_otp = request.otp
        email = request.email

        # Fetch user information from the database
        userInfo = (
            db.query(User)
            .filter(User.email == email, User.verification_code != None)
            .first()
        )
        if userInfo and userInfo.verification_code is not None:
            otp_data = json.loads(userInfo.verification_code)
            otp_value = otp_data.get("otp")
            otp_created_ts = otp_data.get("otp_created_ts")

            decrypted_id = decrypt_otp(otp_value)
            otp_time = datetime.strptime(otp_created_ts, "%Y-%m-%d %H:%M:%S.%f")
            otp_hours = otp_time.hour
            otp_minutes = otp_time.minute
            current_time = datetime.now()
            current_hour = current_time.hour
            current_minutes = current_time.minute
            if current_hour - otp_hours == 0 and current_minutes - otp_minutes <= 15:
                if int(decrypted_id) == int(enter_otp):
                    if userInfo.is_verified is not True:
                        userInfo.is_verified = True
                        userInfo.is_active = True
                        userInfo.verification_code = None

                else:
                    return {
                        "message":  userInfo.account_type == "user" and constants.OTP_VERIFY_FAILED or constants.ADMIN_OTP_VERIFY_FAILED,
                        "success": False,
                    }
            else:
                return {"message": userInfo.account_type == "user" and constants.OTP_EXPIRE or constants.ADMIN_OTP_EXPIRE, "success": False}

            return {
                "message": userInfo.account_type == "user" and constants.OTP_VERIFIED_SUCCESSFULLY or constants.ADMIN_OTP_VERIFIED_SUCCESSFULLY,
                "success": True,
            }
        else:
            return {
                "message": userInfo.account_type == "user" and constants.OTP_VERIFY_FAILED or constants.ADMIN_OTP_VERIFY_FAILED,
                "success": False,
            }

    except Exception as e:
        print(e)
        return {"message": userInfo.account_type == "user" and constants.OTP_VERIFY_FAILED or constants.ADMIN_OTP_VERIFIED_SUCCESSFULLY, "success": False}


# Reset password
async def reset_password(request: ResetPasswordFormSchema, db: Session):
    try:
        email = request.email
        new_password = request.password

        # Find the user by email
        user = db.query(User).filter(User.email == email).first()

        # If user is not found, return an error message
        if not user:
            return {"message": constants.USER_NOT_FOUND, "success": False}

        # Hash the new password
        user.password = bcrypt.hash(
            new_password
        )  # Ensure the password is stored as a string

        # Commit the changes to the database

        return {"message": constants.PASSWORD_RESET_SUCCESSFULLY, "success": True}

    except Exception as e:
        print(e)
        return {"message": constants.SOMETHING_WENT_WRONG, "success": False}


async def forgot_password(request: ForgotPassSchema, db: Session):
    try:
        # Find user with the given email and verified status
        user_exists = (
            db.query(User)
            .filter(
                and_(User.email == request.email.lower(), User.is_verified.is_(True))
            )
            .first()
        )

        # If user is not found, return an error message
        if not user_exists:
            return {"message": constants.USER_NOT_FOUND, "success": False}

        # Generate OTP and encrypt it
        otp = generate_otp()
        encrypted_id = encrypt_otp(f"{otp}")

        user_exists.verification_code = json.dumps(
            {"otp": encrypted_id, "otp_created_ts": str(datetime.now())}
        )

        return await send_verification_otp(
            user_exists,
            template_env,
            "otp_forget_email.html",
            constants.PASSWORD_RESET_CODE,
            otp,
        )

    except Exception as e:
        print(f"Error in forgot_password: {e}")
        return {
            "message": constants.SOMETHING_WENT_WRONG,
            "success": False,
        }


# User login api
async def login(request: LoginSchema, db: Session):
    try:
        user = (
            db.query(User)
            .filter(User.email == request.email.lower())
            .filter(User.account_type == request.account_type)
            .first()
        )
        if not user:
            return {
                "message": constants.ADMIN_INCORRECT_CREDENTIALS,
                "success": False,
            }

        if not verify_password(request.password, user.password):
            return {
                "message": user.account_type == "user" and constants.INCORRECT_CREDENTIALS or constants.ADMIN_INCORRECT_CREDENTIALS,
                "success": False,
            }
        if not user.is_verified:
            otp = generate_otp()
            encrypted_id = encrypt_otp(str(otp))
            user.verification_code = (
                json.dumps(
                    {"otp": encrypted_id, "otp_created_ts": str(datetime.now())}
                ),
            )

            return await send_verification_otp(
                user,
                template_env,
                "otp_email.html",
                constants.SIGNUP_OTP_SUBJECT,
                otp,
            )
        if not user.is_active:
            return {
                "message": user.account_type == "user" and constants.ACCOUNT_NOT_ACTIVE or constants.ADMIN_ACCOUNT_NOT_ACTIVE,
                "success": False,
            }

        payload = {
            "id": user.id,
            "email": user.email,
            "account_type": user.account_type,
        }

        access_token = create_access_token(payload)
        is_first_login = False

        if not user.last_login:
            is_first_login = False

        user.last_login = datetime.now()

        session = UserSession(user_id=user.id, token=access_token.decode())
        db.add(session)

        forms_count = db.query(Forms).count()
        return {
            "data": {
                "token": access_token,
                "user": user.to_dict(),
                "is_first_login": is_first_login,
                "forms_count": forms_count
            },
            "message": user.account_type == "user" and constants.LOGIN_SUCCESS or constants.ADMIN_LOGIN_SUCCESS,
            "success": True,
        }

    except Exception as e:
        print(e)
        return {
            "message":  constants.SOMETHING_WENT_WRONG,
            "success": False,
        }


async def resend_verification_details(
    request: ResendVerificationCodeSchema, db: Session
):
    try:
        user = db.query(User).filter(User.email == request.email.lower()).first()
        if not user:
            return {
                "message": constants.USER_NOT_FOUND,
                "success": False,
            }
        otp = generate_otp()
        encrypted_id = encrypt_otp(str(otp))
        user.verification_code = (
            json.dumps({"otp": encrypted_id, "otp_created_ts": str(datetime.now())}),
        )

        return await send_verification_otp(
            user,
            template_env,
            (
                "otp_forget_email.html"
                if request.type == "forgot-password"
                else "otp_email.html"
            ),
            (
                constants.PASSWORD_RESET_CODE
                if request.type == "forgot-password"
                else constants.SIGNUP_OTP_SUBJECT
            ),
            otp,
        )
    except Exception as e:
        print(e)
        return {
            "message": constants.SOMETHING_WENT_WRONG,
            "success": False,
        }


async def admin_image_update(request: UpdateAdminImage, db: Session):
    try:
        user = db.query(User).filter(User.email == request.email.lower()).first()
        if not user:
            return {
                "message": constants.ADMIN_NOT_FOUND,
                "success": False,
            }
        user.image = request.image

        return {
            "message": constants.ADMIN_IMAGE_UPDATED_SUCCESSFULLY,
            "success": True,
        }

    except Exception as e:
        print(e)
        return {
            "message": constants.SOMETHING_WENT_WRONG,
            "success": False,
        }


async def update_detail_of_admin(request: UpdateAdminDetails, db: Session):
    try:
        user = db.query(User).filter(User.email == request.email).first()
        if not user:
            return {
                "message": constants.ADMIN_NOT_FOUND,
                "success": False,
            }
        user.first_name = str(request.first_name + " " + request.last_name)

        return {
            "message": constants.ADMIN_UPDATED_SUCCESSFULLY,
            "success": True,
        }

    except Exception as e:
        print(e)
        return {
            "message": constants.SOMETHING_WENT_WRONG,
            "success": False,
        }


async def update_password_of_admin(request: UpdatePassword, db: Session):
    try:
        user = db.query(User).filter(User.email == request.email.lower()).first()
        if not user:
            return {
                "message": constants.ADMIN_NOT_FOUND,
                "success": False,
            }
        if (request.confirm_password != request.new_password):
            return {
                "message": constants.PASSWORD_NOT_MATCH,
                "success": False,
            }
        user.password = bcrypt.hash(
            request.new_password
        )

        return {
            "message": constants.ADMIN_PASSWORD_UPDATED_SUCCESSFULLY,
            "success": True,
        }

    except Exception as e:
        print(e)
        return {
            "message": constants.SOMETHING_WENT_WRONG,
            "success": False,
        }
    
async def delete_session(current_user: CurrentUser, db: Session):
    try:
        print(current_user)
        sessions = db.query(UserSession).filter(UserSession.user_id == current_user["id"]).all()
        if sessions:
            for session in sessions:
                db.delete(session)
        return {
            "message": constants.SESSION_DELETED,
            "success": True,
        }
    except Exception as e:
        print(e)
        return {
            "message": constants.SOMETHING_WENT_WRONG,
            "success": False,
        }

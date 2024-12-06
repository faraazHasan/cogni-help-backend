from app.features.user.schemas import CurrentUser
from app.utils.middlewares.oauth import is_user_authorized
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.common.schemas import ResponseModal
from app.database import db_connection
from app.features.auth.repository import (
    delete_session,
    forgot_password,
    login,
    resend_verification_details,
    reset_password,
    signup,
    update_detail_of_admin,
    update_password_of_admin,
    verify_user_otp,
    admin_image_update,
)
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
from app.utils.app_routes import routes
from app.utils.app_routes.routes import app_routes
auth_routes = app_routes.auth

router = APIRouter(prefix=auth_routes.INDEX)


# Signup api
@router.post(auth_routes.SIGNUP, response_model=ResponseModal)
async def signup_user(request: UserSchema, db: Session = Depends(db_connection)):
    response = await signup(request, db)
    return response


# Verify api
@router.post(auth_routes.VERIFY, response_model=ResponseModal)
async def verify_otp(
    request: VerifyUserSignupOtpSchema, db: Session = Depends(db_connection)
):
    return await verify_user_otp(request, db)


# Reset Password api
@router.post(auth_routes.RESET_PASSWORD, response_model=ResponseModal)
async def password_change(
    request: ResetPasswordFormSchema, db: Session = Depends(db_connection)
):
    response = await reset_password(request, db)
    return response


# forgot password api
@router.post(auth_routes.FORGOT_PASSWORD, response_model=ResponseModal)
async def password_forgot(
    request: ForgotPassSchema, db: Session = Depends(db_connection)
):
    response = await forgot_password(request, db)
    return response


# Login  api
@router.post(auth_routes.LOGIN, response_model=ResponseModal)
async def login_user(request: LoginSchema, db: Session = Depends(db_connection)):
    return await login(request, db)


# Resend Verification Code Schema  api
@router.post(routes.Routes.RESEND_VERIFICATION_CODE, response_model=ResponseModal)
async def resend_verification_code(
    request: ResendVerificationCodeSchema, db: Session = Depends(db_connection)
):
    return await resend_verification_details(request, db)

@router.put(auth_routes.UPDATE_ADMIN_IMAGE, response_model=ResponseModal)
async def update_admin_image(
    request: UpdateAdminImage,
    db : Session = Depends(db_connection)
):
    return await admin_image_update(request, db)

@router.put(auth_routes.UPDATE_ADMIN_DETAILS, response_model=ResponseModal)
async def update_admin_details(
    request: UpdateAdminDetails,
    db : Session = Depends(db_connection)
):
    return await update_detail_of_admin(request, db)

@router.put(auth_routes.UPDATE_PASSWORD, response_model=ResponseModal)
async def update_admin_password(
    request: UpdatePassword,
    db : Session = Depends(db_connection)
):
    return await update_password_of_admin(request, db)

@router.get(auth_routes.DELETE_SESSION, response_model=ResponseModal)
async def delete_user_session(
    current_user: CurrentUser = Depends(is_user_authorized),
    db : Session = Depends(db_connection)
):
    return await delete_session(current_user, db)



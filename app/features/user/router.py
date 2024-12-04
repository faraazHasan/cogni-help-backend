from fastapi import APIRouter, Depends, Query
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.common.schemas import ResponseModal
from app.database import db_connection
from app.features.aws.uploadFile import generate_presigned_urls
from app.features.user.repository import (
    add_user_details,
    dashboard_details,
    get_form_values,
    get_user_details,
    set_questions_count,
    update_detail_of_user,
    update_user_password,
    upload_user_profile_image,
    user_account_delete,
    user_profile_update,
    get_all_users,
    get_specific_user_details,
    update_user_status,
    get_user_profile_graph_details
)
from app.features.user.schemas import (
    AccountDeleteSchema,
    CurrentUser,
    PresignedUrlRequest,
    ProfileImageSchema,
    SetQuestionsCountSchema,
    UpdatePasswordSchema,
    UpdateUserDetails,
    UserDetailsSchema,
    UserProfileSchema,
    # SpecificUserDetails
)
from app.utils.middlewares.oauth import is_user_authorized
from app.utils.app_routes.routes import app_routes, Routes

user_routes = app_routes.user

userRouter = APIRouter(prefix=user_routes.INDEX)


# Add user details api
@userRouter.post(user_routes.ADD_USER_DETAILS, response_model=ResponseModal)
async def user_details(
    request: UserDetailsSchema, db: Session = Depends(db_connection), current_user: CurrentUser = Depends(is_user_authorized)
):
    response = await add_user_details(request, db, current_user)
    return response


# get form values api

@userRouter.get(user_routes.GET_FORM_VALUES, response_model=ResponseModal)
async def form_values(form_id: int | str = Query(-1), db: Session = Depends(db_connection), current_user: CurrentUser = Depends(is_user_authorized)):
    response = await get_form_values(form_id, db, current_user)
    return response


@userRouter.get(user_routes.GET_USER_DETAILS, response_model=ResponseModal)
async def user_details(db: Session = Depends(db_connection), current_user: CurrentUser = Depends(is_user_authorized)):
    response = await get_user_details(db, current_user)
    return response


# Add work history and education api


@userRouter.post(Routes.PROFILE_UPDATE, response_model=ResponseModal)
async def profile_update(
    request: UserProfileSchema,
    db: Session = Depends(db_connection),
    current_user: CurrentUser = Depends(is_user_authorized),
):
    return await user_profile_update(request, db, current_user)


@userRouter.post(Routes.GET_PRE_SIGN_URL, response_model=ResponseModal)
async def create_presigned_urls(
    request: PresignedUrlRequest, current_user: CurrentUser = Depends(is_user_authorized)
):
    return await generate_presigned_urls(request.file_path)


@userRouter.post(Routes.UPLOAD_PROFILE_IMAGE, response_model=ResponseModal)
async def upload_profile_image(
    request: ProfileImageSchema,
    db: Session = Depends(db_connection),
    current_user: CurrentUser = Depends(is_user_authorized),
):
    return await upload_user_profile_image(request.url, db, current_user["id"])


@userRouter.post(Routes.UPDATE_PASSWORD, response_model=ResponseModal)
async def update_password(
    request: UpdatePasswordSchema,
    db: Session = Depends(db_connection),
    current_user: CurrentUser = Depends(is_user_authorized),
):
    return await update_user_password(request, db, current_user["id"])


@userRouter.post(Routes.ACCOUNT_DELETE, response_model=ResponseModal)
async def delete_user(
    request: AccountDeleteSchema,
    db: Session = Depends(db_connection),
    current_user: CurrentUser = Depends(is_user_authorized),
):
    return await user_account_delete(request, db, current_user)


@userRouter.patch(Routes.SET_QUESTIONS_COUNT, response_model=ResponseModal)
async def set_user_daily_questions_count(
    request: SetQuestionsCountSchema,
    db: Session = Depends(db_connection),
    current_user: CurrentUser = Depends(is_user_authorized),
):
    return await set_questions_count(request, db, current_user)


@userRouter.get(Routes.GET_DASHBOARD_DETAILS, response_model=ResponseModal)
async def get_dashboard_details(
    db: Session = Depends(db_connection),
    current_user: CurrentUser = Depends(is_user_authorized),
):
    return await dashboard_details(db)


@userRouter.get(Routes.GET_ALL_USERS, response_model=ResponseModal)
async def get_all_user(
    db: Session = Depends(db_connection),
    offset: int = Query(0, description="Offset for pagination"),
    limit: int = Query(10, description="Limit for pagination"),
    searchQuery: str = Query("", description="Sting for search"),
    current_user: CurrentUser = Depends(is_user_authorized),
):
    return await get_all_users(db, offset, limit, searchQuery, current_user["id"])


@userRouter.get(Routes.GET_SPECIFIC_USER_DETAIL, response_model=ResponseModal)
async def get_specific_users_detail(
    user_id: str,
    db: Session = Depends(db_connection), current_user: CurrentUser = Depends(is_user_authorized)
):
    return await get_specific_user_details(user_id, db)


@userRouter.get(Routes.UPDATE_USER_STATUS, response_model=ResponseModal)
async def update_users_status(
    user_id: str,
    db: Session = Depends(db_connection), current_user: CurrentUser = Depends(is_user_authorized)
):
    return await update_user_status(user_id, db)


@userRouter.get(Routes.GET_USER_GRAPH_DETAILS, response_model=ResponseModal)
async def get_user_profile_graph_detail(
    user_id: str,
    db: Session = Depends(db_connection), current_user: CurrentUser = Depends(is_user_authorized)
):
    return await get_user_profile_graph_details(user_id, db)


@userRouter.post(Routes.UPDATE_USER_DETAILS, response_model=ResponseModal)
async def update_user_details(
    request: UpdateUserDetails,
    db: Session = Depends(db_connection),
    current_user: CurrentUser = Depends(is_user_authorized)

):
    return await update_detail_of_user(request, db, current_user)

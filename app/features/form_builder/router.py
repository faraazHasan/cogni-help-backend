from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.common.schemas import ResponseModal
from app.database import db_connection

from app.features.user.schemas import CurrentUser
from app.utils.middlewares.oauth import is_user_authorized
from app.utils.app_routes.routes import app_routes
from app.features.form_builder.schemas import FormBuilderSchema

from .repository import FormBuilderRepo

form_builder_routes = app_routes.form_builder

router = APIRouter(prefix=form_builder_routes.INDEX)


@router.post(form_builder_routes.CREATE, response_model=ResponseModal)
async def create(request: FormBuilderSchema, db: Session = Depends(db_connection), current_user: CurrentUser = Depends(is_user_authorized)):
    form_builder = FormBuilderRepo(db)
    return await form_builder.create_form(request)


@router.patch(form_builder_routes.UPDATE, response_model=ResponseModal)
async def update(request: FormBuilderSchema, db: Session = Depends(db_connection), current_user: CurrentUser = Depends(is_user_authorized)):
    form_builder = FormBuilderRepo(db)
    return await form_builder.update_form(request)


@router.get("/get-form/{form_id}", response_model=ResponseModal)
async def get(form_id: int, db: Session = Depends(db_connection), current_user: CurrentUser = Depends(is_user_authorized)):
    form_builder = FormBuilderRepo(db)
    return await form_builder.get_form(form_id)


@router.get(form_builder_routes.GET_ALL, response_model=ResponseModal)
async def get(db: Session = Depends(db_connection), current_user: CurrentUser = Depends(is_user_authorized)):
    form_builder = FormBuilderRepo(db)
    return await form_builder.get_forms()


@router.get(form_builder_routes.GET_FORM_COUNT, response_model=ResponseModal)
async def get(db: Session = Depends(db_connection), current_user: CurrentUser = Depends(is_user_authorized)):
    form_builder = FormBuilderRepo(db)
    return await form_builder.get_forms_count()

import asyncio
from uuid import uuid4
from fastapi import APIRouter, Depends
from app.common.schemas import ResponseModal
from app.database import db_connection
from app.features.questions.repository import QuestionsRepo, request_store
from app.features.questions.schema import ChangeCurrentQuestionIdSchema, ReduceOptionsSchema, SkipQuestionSchema, SubmitQuestionSchema
from app.features.user.schemas import CurrentUser
from app.utils.middlewares.oauth import is_user_authorized
from app.utils.app_routes.routes import app_routes
from sqlalchemy.orm import Session

questions_routes = app_routes.questions

questions_router = APIRouter(prefix=questions_routes.INDEX)


@questions_router.get(questions_routes.GET_DAILY_QUESTIONS, response_model=ResponseModal)
async def daily_questions(timeOffset: int, db: Session = Depends(db_connection), current_user: CurrentUser = Depends(is_user_authorized)
                          ):
    if current_user["id"] in request_store:
        return await request_store[current_user["id"]]["future"]
    task_id = str(uuid4())
    task = asyncio.create_task(QuestionsRepo(
        db).get_daily_questions(current_user, task_id, timeOffset))
    request_store[current_user["id"]] = {"task_id": task_id, "future": task}

    result = await task

    del request_store[current_user["id"]]
    return result


@questions_router.post(questions_routes.SUBMIT_ANSWER, response_model=ResponseModal)
async def submit_answer(request: SubmitQuestionSchema, db: Session = Depends(db_connection), current_user: CurrentUser = Depends(is_user_authorized)
                        ):
    response = await QuestionsRepo(db).submit_answer(request)
    return response


@questions_router.post(questions_routes.REDUCE_OPTIONS, response_model=ResponseModal)
async def reduce_options(request: ReduceOptionsSchema, db: Session = Depends(db_connection), current_user: CurrentUser = Depends(is_user_authorized)
                         ):
    response = await QuestionsRepo(db).reduce_options(request)
    return response


@questions_router.get("/view-answers/{quiz_id}", response_model=ResponseModal)
async def view_answers(quiz_id: int, db: Session = Depends(db_connection), current_user: CurrentUser = Depends(is_user_authorized)):
    response = await QuestionsRepo(db).view_answers(quiz_id)
    return response


@questions_router.post(questions_routes.SKIP_QUESTION, response_model=ResponseModal)
async def skip_question(request: SkipQuestionSchema, db: Session = Depends(db_connection), current_user: CurrentUser = Depends(is_user_authorized)):
    response = await QuestionsRepo(db).skip_question(request)
    return response


@questions_router.post(questions_routes.CHANGE_CURRENT_QUESTION_ID, response_model=ResponseModal)
async def change_current_question_index(request: ChangeCurrentQuestionIdSchema, db: Session = Depends(db_connection), current_user: CurrentUser = Depends(is_user_authorized)):
    response = await QuestionsRepo(db).change_current_question_index(request)
    return response

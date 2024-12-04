from typing import Optional
from pydantic import BaseModel


class DailyQuestionsSchema(BaseModel):
    question_count: int


class UpdateQuestionsSchema(BaseModel):
    question_id: int


class SubmitQuestionSchema(BaseModel):
    quiz_id: int
    question_id: int
    answer: Optional[str] | None
    start_datetime: Optional[str] | None
    end_datetime: Optional[str] | None
    date_completed: Optional[str] | None
    status: str
    current_question_id: int


class ReduceOptionsSchema(BaseModel):
    question_id: int


class SkipQuestionSchema(BaseModel):
    quiz_id: int
    question_id: int
    current_question_id: int
    status: str


class ChangeCurrentQuestionIdSchema(BaseModel):
    quiz_id: int
    current_question_id: int

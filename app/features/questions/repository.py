from datetime import datetime
from app.features.user.schemas import CurrentUser
from app.utils.contexts.common_contexts import process_request
from app.models.user_details import UserDetails
from app.models.quizs import Quizs
from app.models.questions import Questions
from app.features.questions.schema import ChangeCurrentQuestionIdSchema, ReduceOptionsSchema, SkipQuestionSchema, SubmitQuestionSchema
from app.features.bot.utils.response import ResponseCreator
from app.common import constants
from sqlalchemy.orm import Session
import json
request_store = {}


def normalize_questions(data):
    normalized_data = []

    for item in data:
        # Normalize 'questions'/'question' to 'question'
        normalized_item = {
            "question": item.get("questions") or item.get("question"),
            # Normalize 'options'/'option' to 'options'
            "options": item.get("options") or ([item["option"]] if "option" in item else []),
            # Normalize 'hints'/'hint' to 'hint'
            "hint": item.get("hint") or item.get("hints", "")
        }
        normalized_data.append(normalized_item)

    return normalized_data


def add_questions_to_db(db_session, quiz_id, user_id, questions_data, user_details):
    if isinstance(questions_data, str):
        questions_data = json.loads(questions_data)
    questions = normalize_questions(questions_data)
    questions_to_insert = []
    current_time = datetime.now()

    first_question_id = None  # To capture the first question's ID

    already_added_questions = json.loads(
        user_details.quiz_summary) if user_details.quiz_summary else []

    # Correct the loop to use enumerate
    for index, question in enumerate(questions):
        question_text = question["question"]
        options = question["options"]
        hint = question["hint"]

        options_json = json.dumps(
            [{"option": opt["option"], "is_correct": opt["is_correct"]} for opt in options])

        correct_answer = next(opt["option"] for opt in options if opt["is_correct"])

        new_question = Questions(
            user_id=user_id,
            quiz_id=quiz_id,
            details=question_text,
            options=options_json,
            correct_answer=correct_answer,
            hint=hint,
            created_ts=current_time,
            updated_ts=current_time,
        )
        already_added_questions.append({
            "details": question_text,
            "options": options_json,
            "correct_answer": correct_answer,
            "hint": hint})
        if index == 0:
            # After flushing, this ID will be captured
            db_session.add(new_question)
            db_session.flush()  # Flush to assign an ID to the first question
            first_question_id = new_question.id  # Capture the first question's ID
        else:
            questions_to_insert.append(new_question)
    user_details.quiz_summary = json.dumps(already_added_questions)
    db_session.bulk_save_objects(questions_to_insert)
    db_session.flush()

    return first_question_id  # Return the ID of the first question


class QuestionsRepo:
    def __init__(self, db: Session):
        self.db = db

    async def get_daily_questions(self, current_user: CurrentUser, task_id: str, time_offset: int):
        with process_request():
            quiz = self.db.query(Quizs).filter(
                Quizs.user_id == current_user["id"], Quizs.status == "pending").first()

            new_quiz = None
            if quiz:
                if len(quiz.questions):
                    return {
                        "success": True,
                        "message": constants.QUESTIONS_FETCHED,
                        "data": quiz.to_dict()
                    }
                new_quiz = quiz
            else:
                new_quiz = Quizs(
                    user_id=current_user["id"],
                    status="pending"
                )
                self.db.add(new_quiz)
                self.db.flush()

            user_details = self.db.query(UserDetails).filter(
                UserDetails.user_id == current_user["id"]).first()
            if not user_details:
                return {
                    "success": False,
                    "message": constants.USER_DETAILS_NOT_FOUND,
                }

            response_creator = ResponseCreator()
            daily_questions = await response_creator.generate_questions_from_profile_details(
                user_details.to_dict(), time_offset)

            if not daily_questions:
                raise Exception("Could not generate question. Please try again later")

            first_question = add_questions_to_db(
                self.db, new_quiz.id, current_user["id"], daily_questions, user_details)
            new_quiz.current_question_id = first_question

            if request_store.get(current_user['id']) == task_id:
                del request_store[current_user['id']]

            return {
                "success": True,
                "message": constants.DAILY_QUESTIONS,
                "data": new_quiz.to_dict()
            }

    async def submit_answer(self, request: SubmitQuestionSchema):
        with process_request():
            quiz = self.db.query(Quizs).filter(Quizs.id == request.quiz_id).first()
            question = self.db.query(Questions).filter(
                Questions.id == request.question_id).first()
            if quiz:
                quiz.current_question_id = request.current_question_id
                quiz.date_completed = request.date_completed
                quiz.status = request.status
                question.user_answer = request.answer
                question.end_datetime = request.end_datetime
                question.is_answered = True
                question.is_answer_correct = True if question.correct_answer == request.answer else False

                self.db.flush()

                return {
                    "success": True,
                    "message": constants.ANSWER_SUBMITTED
                }

            return {
                "success": False,
                "message": "quiz_not_found",
            }

    async def change_current_question_index(self, request: ChangeCurrentQuestionIdSchema):
        with process_request():
            quiz = self.db.query(Quizs).filter(Quizs.id == request.quiz_id).first()
            if quiz:
                quiz.current_question_id = request.current_question_id
                self.db.flush()

                return {
                    "success": True,
                    "message": constants.CURRENT_QUESTION_CHANGED
                }

            return {
                "success": False,
                "message": "quiz_not_found",
            }

    async def reduce_options(self, request: ReduceOptionsSchema):
        with process_request():
            question = self.db.query(Questions).filter(
                Questions.id == request.question_id).first()
            if question:

                return {
                    "success": True,
                    "message": constants.CURRENT_QUESTION_ID_UPDATED,
                    "data": question.selected_data(reduce_options=True)
                }

            return {
                "success": False,
                "message": constants.CURRENT_QUESTION_ID_NOT_UPDATED,
            }

    async def view_answers(self, quiz_id: str):
        with process_request():
            quiz = self.db.query(Quizs).filter(
                Quizs.id == int(quiz_id), Quizs.status == "completed").first()
            if quiz:
                question = self.db.query(Questions).filter(
                    Questions.quiz_id == quiz_id).all()
                if question:
                    questions = [q.data() for q in question]
                    return {
                        "success": True,
                        "message": constants.CURRENT_QUESTION_ID_UPDATED,
                        "data": questions
                    }

            return {
                "success": False,
                "message": constants.QUIZ_NOT_FOUND,
            }

    async def skip_question(self, request: SkipQuestionSchema):
        with process_request():
            quiz = self.db.query(Quizs).filter(Quizs.id == request.quiz_id).first()
            question = self.db.query(Questions).filter(
                Questions.id == request.question_id).first()
            if quiz:
                quiz.current_question_id = request.current_question_id
                quiz.status = request.status
                question.is_abandoned = True
                self.db.flush()

                return {
                    "success": True,
                    "message": constants.QUESTION_SKIPPED
                }

            return {
                "success": False,
                "message": constants.QUIZ_NOT_FOUND,
            }
